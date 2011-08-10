# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from simple_sso.signatures import build_signature, verify_signature
from simple_sso.sso_client.utils import load_json_user
from urlparse import urljoin
import requests
import urllib

BACKEND = ModelBackend()

def get_request_token():
    params = [('key', settings.SIMPLE_SSO_KEY)]
    signature = build_signature(params, settings.SIMPLE_SSO_SECRET)
    params.append(('signature', signature))
    url = urljoin(settings.SIMPLE_SSO_SERVER, 'request-token') + '/'
    response = requests.get(url, dict(params))
    if response.status_code != 200:
        return False
    data = QueryDict(response.content)
    if 'signature' not in data:
        return False
    if 'request_token' not in data:
        return False
    params = [(key, value) for key,value in data.items() if key != 'signature']
    if not verify_signature(params, data['signature']):
        return False
    return data['request_token']

def verify_auth_token(data):
    if 'auth_token' not in data:
        return False
    if 'request_token' not in data:
        return False
    auth_token = data['auth_token']
    params = [('auth_token', auth_token)]
    signature = build_signature(params)
    params.append(('signature', signature))
    url = urljoin(settings.SIMPLE_SSO_SERVER, 'verify') + '/'
    response = requests.get(url, dict(params))
    if response.status_code != 200:
        return False
    data = QueryDict(response.content)
    if 'signature' not in data:
        return False
    if 'user' not in data:
        return False
    params = [(key, value) for key,value in data.items() if key != 'signature']
    if not verify_signature(params, data['signature']):
        return False
    return load_json_user(data['user'])

def login_view(request):
    request_token = get_request_token()
    if not request_token:
        raise HttpResponseBadRequest()
    params = [('request_token', request_token)]
    signature = build_signature(params)
    params.append(('signature', signature))
    query_string = urllib.urlencode(params)
    url = urljoin(settings.SIMPLE_SSO_SERVER, 'authorize') + '/'
    return HttpResponseRedirect('%s?%s' % (url, query_string))
    
def authenticate_view(request):
    user = verify_auth_token(request.GET)
    if not user:
        raise HttpResponseBadRequest()
    user.backend = "%s.%s" % (BACKEND.__module__, BACKEND.__class__.__name__)
    login(request, user)
    return HttpResponseRedirect('/')
