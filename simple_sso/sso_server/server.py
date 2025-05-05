import datetime
from urllib.parse import urlparse, urlencode, urlunparse

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.http import (HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect, QueryDict)
from django.urls import re_path
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View
from itsdangerous import URLSafeTimedSerializer

from simple_sso.sso_server.models import Token, Consumer
from simple_sso.utils import BaseProvider, provider_wrapper


class Provider(BaseProvider):
    max_age = 5

    def __init__(self, server):
        self.server = server

    def get_private_key(self, public_key):
        try:
            self.consumer = Consumer.objects.get(public_key=public_key)
        except Consumer.DoesNotExist:
            return None
        return self.consumer.private_key


class RequestTokenProvider(Provider):
    def provide(self, data):
        redirect_to = data['redirect_to']
        token = Token.objects.create(consumer=self.consumer, redirect_to=redirect_to)
        return {'request_token': token.request_token}


class AuthorizeView(View):
    """
    The client get's redirected to this view with the `request_token` obtained
    by the Request Token Request by the client application beforehand.

    This view checks if the user is logged in on the server application and if
    that user has the necessary rights.

    If the user is not logged in, the user is prompted to log in.
    """
    server = None

    def get(self, request):
        request_token = request.GET.get('token', None)
        if not request_token:
            return self.missing_token_argument()
        try:
            self.token = Token.objects.select_related('consumer').get(request_token=request_token)
        except Token.DoesNotExist:
            return self.token_not_found()
        if not self.check_token_timeout():
            return self.token_timeout()
        self.token.refresh()
        if request.user.is_authenticated:
            return self.handle_authenticated_user()
        else:
            return self.handle_unauthenticated_user()

    def missing_token_argument(self):
        return HttpResponseBadRequest('Token missing')

    def token_not_found(self):
        return HttpResponseForbidden('Token not found')

    def token_timeout(self):
        return HttpResponseForbidden('Token timed out')

    def check_token_timeout(self):
        delta = timezone.now() - self.token.timestamp
        if delta > self.server.token_timeout:
            self.token.delete()
            return False
        else:
            return True

    def handle_authenticated_user(self):
        if self.server.has_access(self.request.user, self.token.consumer):
            return self.success()
        else:
            return self.access_denied()

    def handle_unauthenticated_user(self):
        next_ = '%s?%s' % (self.request.path, urlencode([('token', self.token.request_token)]))
        url = '%s?%s' % (reverse(self.server.auth_view_name), urlencode([('next', next_)]))
        return HttpResponseRedirect(url)

    def access_denied(self):
        return HttpResponseForbidden("Access denied")

    def success(self):
        self.token.user = self.request.user
        self.token.save()
        serializer = URLSafeTimedSerializer(self.token.consumer.private_key)
        parse_result = urlparse(self.token.redirect_to)
        query_dict = QueryDict(parse_result.query, mutable=True)
        query_dict['access_token'] = serializer.dumps(self.token.access_token)
        url = urlunparse((parse_result.scheme, parse_result.netloc, parse_result.path, '', query_dict.urlencode(), ''))
        return HttpResponseRedirect(url)


class VerificationProvider(Provider, AuthorizeView):
    def provide(self, data):
        token = data['access_token']
        try:
            self.token = Token.objects.select_related('user').get(access_token=token, consumer=self.consumer)
        except Token.DoesNotExist:
            return self.token_not_found()
        if not self.check_token_timeout():
            return self.token_timeout()
        if not self.token.user:
            return self.token_not_bound()
        extra_data = data.get('extra_data', None)
        return self.server.get_user_data(
            self.token.user, self.consumer, extra_data=extra_data)

    def token_not_bound(self):
        return HttpResponseForbidden("Invalid token")


class ConsumerAdmin(ModelAdmin):
    readonly_fields = ['public_key', 'private_key']


class Server:
    request_token_provider = RequestTokenProvider
    authorize_view = AuthorizeView
    verification_provider = VerificationProvider
    token_timeout = datetime.timedelta(minutes=5)
    client_admin = ConsumerAdmin
    auth_view_name = 'login'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.register_admin()

    def register_admin(self):
        admin.site.register(Consumer, self.client_admin)

    def has_access(self, user, consumer):
        return True

    def get_user_extra_data(self, user, consumer, extra_data):
        raise NotImplementedError()

    def get_user_data(self, user, consumer, extra_data=None):
        user_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': False,
            'is_superuser': False,
            'is_active': user.is_active,
        }
        if extra_data:
            user_data['extra_data'] = self.get_user_extra_data(
                user, consumer, extra_data)
        return user_data

    def get_urls(self):
        return [
            re_path(r'^request-token/$', provider_wrapper(self.request_token_provider(server=self)),
                    name='simple-sso-request-token'),
            re_path(r'^authorize/$', self.authorize_view.as_view(server=self), name='simple-sso-authorize'),
            re_path(r'^verify/$', provider_wrapper(
                    self.verification_provider(server=self)), name='simple-sso-verify'),
        ]
