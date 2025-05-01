import string
from random import SystemRandom
from urllib.parse import urlparse, urlunparse, urljoin

import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from itsdangerous import TimedSerializer, SignatureExpired, BadSignature

from simple_sso.exceptions import BadRequest, WebserviceError

random = SystemRandom()

KEY_CHARACTERS = string.ascii_letters + string.digits
PUBLIC_KEY_HEADER = 'x-services-public-key'


def default_gen_secret_key(length=40):
    return ''.join([random.choice(KEY_CHARACTERS) for _ in range(length)])


def gen_secret_key(length=40):
    generator = getattr(settings, 'SIMPLE_SSO_KEYGENERATOR', default_gen_secret_key)
    return generator(length)


def _split_dsn(dsn):
    parse_result = urlparse(dsn)
    host = parse_result.hostname
    if parse_result.port:
        host += ':%s' % parse_result.port
    base_url = urlunparse((
        parse_result.scheme,
        host,
        parse_result.path,
        parse_result.params,
        parse_result.query,
        parse_result.fragment,
    ))
    return base_url, parse_result.username, parse_result.password


class BaseConsumer(object):
    def __init__(self, base_url, public_key, private_key):
        self.base_url = base_url
        self.public_key = public_key
        self.signer = TimedSerializer(private_key)

    @classmethod
    def from_dsn(cls, dsn):
        base_url, public_key, private_key = _split_dsn(dsn)
        return cls(base_url, public_key, private_key)

    def consume(self, path, data, max_age=None):
        if not path.startswith('/'):
            raise ValueError("Paths must start with a slash")
        signed_data = self.signer.dumps(data)
        headers = {
            PUBLIC_KEY_HEADER: self.public_key,
            'Content-Type': 'application/json',
        }
        url = self.build_url(path)
        body = self.send_request(url, data=signed_data, headers=headers)
        return self.handle_response(body, max_age)

    def handle_response(self, body, max_age):
        return self.signer.loads(body, max_age=max_age)

    def send_request(self, url, data, headers):
        raise NotImplementedError(
            'Implement send_request on BaseConsumer subclasses')

    @staticmethod
    def raise_for_status(status_code, message):
        if status_code == 400:
            raise BadRequest(message)
        elif status_code >= 300:
            raise WebserviceError(message)

    def build_url(self, path):
        path = path.lstrip('/')
        return urljoin(self.base_url, path)


class SyncConsumer(BaseConsumer):
    def __init__(self, base_url, public_key, private_key):
        super(SyncConsumer, self).__init__(base_url, public_key, private_key)
        self.session = requests.session()

    def send_request(self, url, data, headers):  # pragma: no cover
        response = self.session.post(url, data=data, headers=headers)
        self.raise_for_status(response.status_code, response.content)
        return response.content


class BaseProvider(object):
    max_age = None

    def provide(self, data):
        raise NotImplementedError(
            'Subclasses of services.models.Provider must implement '
            'the provide method'
        )

    def get_private_key(self, public_key):
        raise NotImplementedError(
            'Subclasses of services.models.Provider must implement '
            'the get_private_key method'
        )

    def report_exception(self):
        pass

    def get_response(self, method, signed_data, get_header):
        if method != 'POST':
            return 405, ['POST']
        public_key = get_header(PUBLIC_KEY_HEADER, None)
        if not public_key:
            return 400, "No public key"
        private_key = self.get_private_key(public_key)
        if not private_key:
            return 400, "Invalid public key"
        signer = TimedSerializer(private_key)
        try:
            data = signer.loads(signed_data, max_age=self.max_age)
        except SignatureExpired:
            return 400, "Signature expired"
        except BadSignature:
            return 400, "Bad Signature"
        try:
            raw_response_data = self.provide(data)
        except:
            self.report_exception()
            return 400, "Failed to process the request"
        response_data = signer.dumps(raw_response_data)
        return 200, response_data


def provider_wrapper(provider):
    def provider_view(request):
        def get_header(key, default):
            django_key = 'HTTP_%s' % key.upper().replace('-', '_')
            return request.META.get(django_key, default)

        method = request.method
        if getattr(request, 'body', None):
            signed_data = request.body
        else:
            signed_data = request.raw_post_data
        status_code, data = provider.get_response(
            method,
            signed_data,
            get_header,
        )
        return HttpResponse(data, status=status_code)

    return csrf_exempt(provider_view)
