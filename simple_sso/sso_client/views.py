# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.http import HttpResponseBadRequest, QueryDict, HttpResponseRedirect
from simple_sso.signatures import build_signature, verify_signature
from simple_sso.sso_client.utils import load_json_user
from urlparse import urljoin, urlparse
import requests
import urllib

BACKEND = ModelBackend()

def get_request_token():
    """
    Requests a Request Token from the SSO Server. Returns False if the request
    failed.
    """
    params = [('key', settings.SIMPLE_SSO_KEY)]
    signature = build_signature(params, settings.SIMPLE_SSO_SECRET)
    params.append(('signature', signature))
    url = urljoin(settings.SIMPLE_SSO_SERVER, 'request-token') + '/'
    response = requests.get(url, params=dict(params))
    if response.status_code != 200:
        return False
    data = QueryDict(response.content)
    if 'signature' not in data:
        return False
    if 'request_token' not in data:
        return False
    params = [(key, value) for key,value in data.items() if key != 'signature']
    if not verify_signature(params, data['signature'], settings.SIMPLE_SSO_SECRET):
        return False
    return data['request_token']

def verify_auth_token(data):
    """
    Verifies a Auth Token in a QueryDict. Returns a
    django.contrib.auth.models.User instance if successful or False.
    """
    if 'auth_token' not in data:
        return False
    if 'request_token' not in data:
        return False
    auth_token = data['auth_token']
    params = [('auth_token', auth_token), ('key', settings.SIMPLE_SSO_KEY)]
    signature = build_signature(params, settings.SIMPLE_SSO_SECRET)
    params.append(('signature', signature))
    url = urljoin(settings.SIMPLE_SSO_SERVER, 'verify') + '/'
    response = requests.get(url, params=dict(params))
    if response.status_code != 200:
        return False
    data = QueryDict(response.content)
    if 'signature' not in data:
        return False
    if 'user' not in data:
        return False
    params = [(key, value) for key,value in data.items() if key != 'signature']
    if not verify_signature(params, data['signature'], settings.SIMPLE_SSO_SECRET):
        return False
    return load_json_user(data['user'])

def get_next(request):
    """
    Given a request, returns the URL where a user should be redirected to 
    after login. Defaults to '/'
    """
    next = request.GET.get('next', None)
    if not next:
        return '/'
    netloc = urlparse(next)[1]

    # Heavier security check -- don't allow redirection to a different
    # host.
    # Taken from django.contrib.auth.views.login
    if netloc and netloc != request.get_host():
        return '/'
    return next

def login_view(request):
    """
    Login view.
    
    Requests a Request Token and then redirects the User to the the SSO Server.
    """
    next = get_next(request)
    request.session['simple-sso-next'] = next
    request_token = get_request_token()
    if not request_token:
        return HttpResponseBadRequest()
    params = [('request_token', request_token), ('key', settings.SIMPLE_SSO_KEY)]
    signature = build_signature(params, settings.SIMPLE_SSO_SECRET)
    params.append(('signature', signature))
    query_string = urllib.urlencode(params)
    url = urljoin(settings.SIMPLE_SSO_SERVER, 'authorize') + '/'
    return HttpResponseRedirect('%s?%s' % (url, query_string))
    
def authenticate_view(request):
    """
    Authentication view.
    
    Verifies the user token and logs the user in.
    """
    user = verify_auth_token(request.GET)
    if not user:
        return HttpResponseBadRequest()
    user.backend = "%s.%s" % (BACKEND.__module__, BACKEND.__class__.__name__)
    login(request, user)
    return HttpResponseRedirect(request.session.get('simple-sso-next', '/'))
