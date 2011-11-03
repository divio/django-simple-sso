# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url, include
from django.http import HttpResponse
from simple_sso.server import SimpleSSOServer

test_server = SimpleSSOServer()

urlpatterns = patterns('',
    url('^server/', include(test_server.get_urls())),
    url('^client/', include('simple_sso.sso_client.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url('^$', lambda request: HttpResponse('home'), name='root')
)