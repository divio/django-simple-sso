# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('simple_sso.sso_client.views',
    url(r'^$', 'login_view', name='simple-sso-login'),
    url(r'^authenticate/$', 'authenticate_view', name='simple-sso-authenticate'),
)
