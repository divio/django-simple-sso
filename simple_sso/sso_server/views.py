# -*- coding: utf-8 -*-
from django.http import (HttpResponse, HttpResponseForbidden, 
    HttpResponseBadRequest, HttpResponseRedirect)
from simple_sso.signatures import build_signature
from simple_sso.sso_server.forms import (RequestTokenRequestForm, AuthorizeForm, 
    VerificationForm)
from simple_sso.sso_server.models import Token
from simple_sso.sso_server.utils import get_user_json
from urlparse import urljoin
import urllib


def request_token(request):
    form = RequestTokenRequestForm(request.GET)
    if form.is_valid():
        token = Token.objects.create_for_client(form.client)
        params = [('request_token', token.request_token)]
        signature = build_signature(params)
        params.append(('signature', signature))
        data = urllib.urlencode(params)
        return HttpResponse(data)
    else:
        if form.invalid_signature:
            return HttpResponseForbidden()
        return HttpResponseBadRequest()

def authorize(request):
    form = AuthorizeForm(request.GET)
    if form.is_valid():
        token = form.cleaned_data['request_token']
        if request.user.is_authenticated():
            url = urljoin(token.client.root_url, 'authenticate') + '/'
            params = [('request_token', token.request_token), ('auth_token', token.auth_token)]
            signature = build_signature(params)
            params.append(('signature', signature))
            token.user = request.user
            token.save()
            return HttpResponseRedirect('%s?%s' % (url, urllib.urlencode(params)))
        else:
            # TODO: Promt login
            pass
    else:
        if form.invalid_signature:
            return HttpResponseForbidden()
        return HttpResponseBadRequest()

def verify(request):
    form = VerificationForm(request.GET)
    if form.is_valid():
        token = form.cleaned_data['auth_token']
        user = get_user_json(token.user, token.client)
        params = [('user', user)]
        signature = build_signature(params)
        params.append(('signature', signature))
        data = urllib.urlencode(params)
        token.delete()
        return HttpResponse(data)
    else:
        if form.invalid_signature:
            return HttpResponseForbidden()
        return HttpResponseBadRequest()
