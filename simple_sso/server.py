# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseForbidden, 
    HttpResponseBadRequest, HttpResponseRedirect)
from django.utils import simplejson
from django.views.generic.base import View
from simple_sso.signatures import build_signature
from simple_sso.sso_server.forms import (RequestTokenRequestForm, AuthorizeForm, 
    VerificationForm)
from simple_sso.sso_server.models import Token, Client
from simple_sso.utils import SIMPLE_KEYS
from urlparse import urljoin
import datetime
import urllib


class RequestTokenView(View):
    """
    Request Token Request view called by the client application to obtain a
    one-time Request Token.
    """
    form_class = RequestTokenRequestForm
    server = None
    
    def get(self, request):
        self.form = self.form_class(self.request.GET)
        if self.form.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid()
    
    def get_token(self):
        return Token.objects.create_for_client(self.form.client)
    
    def form_valid(self):
        token = self.get_token()
        params = [('request_token', token.request_token)]
        signature = build_signature(params, token.client.secret)
        params.append(('signature', signature))
        data = urllib.urlencode(params)
        return HttpResponse(data)
    
    def form_invalid(self):
        if self.form.invalid_signature:
            return HttpResponseForbidden()
        return HttpResponseBadRequest()


class AuthorizeView(View):
    """
    The client get's redirected to this view with the `request_token` obtained
    by the Request Token Request by the client application beforehand.
    
    This view checks if the user is logged in on the server application and if
    that user has the necessary rights.
    
    If the user is not logged in, the user is prompted to log in.
    """
    form_class = AuthorizeForm
    server = None
    
    def get(self, request):
        self.form = self.form_class(request.GET)
        if self.form.is_valid():
            self.token = self.form.cleaned_data['token']
            if self.check_token_timeout():
                return self.form_valid()
            else:
                return self.token_timeout()
        else:
            return self.form_invalid()
        
    def form_valid(self):
        if self.request.user.is_authenticated():
            return self.form_valid_authenticated()
        else:
            return self.form_valid_unauthenticated()
        
    def check_token_timeout(self):
        delta = datetime.datetime.now() - self.token.created
        if delta > self.server.token_timeout:
            return False
        else:
            return True
    
    def token_timeout(self):
        self.token.delete()
        return HttpResponseForbidden()
    
    def form_valid_authenticated(self):
        if self.has_access():
            return self.success()
        else:
            return self.access_denied()
        
    def has_access(self):
        return True
    
    def success(self):
        url = urljoin(self.token.client.root_url, 'authenticate') + '/'
        params = [('request_token', self.token.request_token), ('auth_token', self.token.auth_token)]
        signature = build_signature(params, self.token.client.secret)
        params.append(('signature', signature))
        self.token.user = self.request.user
        self.token.save()
        return HttpResponseRedirect('%s?%s' % (url, urllib.urlencode(params)))
    
    def access_denied(self):
        return HttpResponseForbidden()
    
    def form_valid_unauthenticated(self):
        params = urllib.urlencode([('next', '%s?%s' % (self.request.path, urllib.urlencode(self.request.GET)))])
        return HttpResponseRedirect('%s?%s' % (reverse('django.contrib.auth.views.login'), params))
        
    def form_invalid(self):
        if self.form.invalid_signature:
            return HttpResponseForbidden()
        return HttpResponseBadRequest()


class VerifyView(View):
    """
    View called by the client application to verify the Auth Token passed by
    the client request as GET parameter with the server application
    """
    form_class = VerificationForm
    server = None
    
    def get(self, request):
        self.form = self.form_class(request.GET)
        if self.form.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid()
    
    def construct_user(self):
        data = {}
        for key in SIMPLE_KEYS:
            data[key] = getattr(self.token.user, key)
        data['permissions'] = []
        for perm in self.token.user.user_permissions.select_related('content_type').all():
            data['permissions'].append({
                'content_type': perm.content_type.natural_key(),
                'codename': perm.codename,
            })
        return data

    def get_user_json(self):
        """
        Returns the JSON string representation of the user object for a client.
        """
        data = self.construct_user()
        return simplejson.dumps(data)
    
    def form_valid(self):
        self.token = self.form.cleaned_data['token']
        self.user = self.get_user_json()
        params = [('user', self.user)]
        signature = build_signature(params, self.token.client.secret)
        params.append(('signature', signature))
        data = urllib.urlencode(params)
        self.token.delete()
        return HttpResponse(data)
        
    def form_invalid(self):
        if self.form.invalid_signature:
            return HttpResponseForbidden()
        return HttpResponseBadRequest()


class SimpleSSOServer(object):
    request_token_view = RequestTokenView
    authorize_view = AuthorizeView
    verify_view = VerifyView
    token_timeout = datetime.timedelta(minutes=30)
    client_admin = ModelAdmin
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.register_admin()
        
    def register_admin(self):
        admin.site.register(Client, self.client_admin)
    
    def get_urls(self):
        return patterns('simple_sso.sso_server.views',
            url(r'^request-token/$', self.request_token_view.as_view(server=self), name='simple-sso-request-token'),
            url(r'^authorize/$', self.authorize_view.as_view(server=self), name='simple-sso-authorize'),
            url(r'^verify/$', self.verify_view.as_view(server=self), name='simple-sso-verify'),
        )
