# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from itsdangerous import URLSafeTimedSerializer
from webservices.sync import SyncConsumer

try:
    # python 3
    # noinspection PyCompatibility
    from urllib.parse import urlparse, urlunparse, urljoin, urlencode
except ImportError:
    # python 2
    # noinspection PyCompatibility
    from urlparse import urlparse, urlunparse, urljoin
    from urllib import urlencode


class LoginView(View):
    client = None

    def get(self, request):
        next = self.get_next()
        scheme = 'https' if request.is_secure() else 'http'
        query = urlencode([('next', next)])
        netloc = request.get_host()
        path = reverse('simple-sso-authenticate')
        redirect_to = urlunparse((scheme, netloc, path, '', query, ''))
        request_token = self.client.get_request_token(redirect_to)
        host = urljoin(self.client.server_url, 'authorize/')
        url = '%s?%s' % (host, urlencode([('token', request_token)]))
        return HttpResponseRedirect(url)

    def get_next(self):
        """
        Given a request, returns the URL where a user should be redirected to
        after login. Defaults to '/'
        """
        next = self.request.GET.get('next', None)
        if not next:
            return '/'
        netloc = urlparse(next)[1]
        # Heavier security check -- don't allow redirection to a different
        # host.
        # Taken from django.contrib.auth.views.login
        if netloc and netloc != self.request.get_host():
            return '/'
        return next


class AuthenticateView(LoginView):
    client = None

    def get(self, request):
        raw_access_token = request.GET['access_token']
        access_token = URLSafeTimedSerializer(self.client.private_key).loads(raw_access_token)
        user = self.client.get_user(access_token)
        user.backend = self.client.backend
        login(request, user)
        next = self.get_next()
        return HttpResponseRedirect(next)


class Client(object):
    login_view = LoginView
    authenticate_view = AuthenticateView
    backend = "%s.%s" % (ModelBackend.__module__, ModelBackend.__name__)
    user_extra_data = None

    def __init__(self, server_url, public_key, private_key,
                 user_extra_data=None):
        self.server_url = server_url
        self.public_key = public_key
        self.private_key = private_key
        self.consumer = SyncConsumer(self.server_url, self.public_key, self.private_key)
        if user_extra_data:
            self.user_extra_data = user_extra_data

    @classmethod
    def from_dsn(cls, dsn):
        parse_result = urlparse(dsn)
        public_key = parse_result.username
        private_key = parse_result.password
        netloc = parse_result.hostname
        if parse_result.port:
            netloc += ':%s' % parse_result.port
        server_url = urlunparse((parse_result.scheme, netloc, parse_result.path, parse_result.params, parse_result.query, parse_result.fragment))
        return cls(server_url, public_key, private_key)

    def get_request_token(self, redirect_to):
        return self.consumer.consume('/request-token/', {'redirect_to': redirect_to})['request_token']

    def get_user(self, access_token):
        data = {'access_token': access_token}
        if self.user_extra_data:
            data['extra_data'] = self.user_extra_data
        user_data = self.consumer.consume('/verify/', data)
        user = self.build_user(user_data)
        return user

    def build_user(self, user_data):
        try:
            user = User.objects.get(username=user_data['username'])
        except User.DoesNotExist:
            user = User(**user_data)
        user.set_unusable_password()
        user.save()
        return user

    def get_urls(self):
        return patterns('',
            url(r'^$', self.login_view.as_view(client=self), name='simple-sso-login'),
            url(r'^authenticate/$', self.authenticate_view.as_view(client=self), name='simple-sso-authenticate'),
        )
