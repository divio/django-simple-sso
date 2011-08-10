# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('simple_sso.sso_server.views',
    url(r'^request-token/$', 'request_token', name='simple-sso-request-token'),
    url(r'^authorize/$', 'authorize', name='simple-sso-authorize'),
    url(r'^verify/$', 'verify', name='simple-sso-verify'),
)
