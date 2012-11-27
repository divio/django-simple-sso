# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.http import HttpResponse
from simple_sso.sso_client.client import Client
from simple_sso.sso_server.server import Server

test_server = Server()
test_client = Client(settings.SSO_SERVER, settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY)

urlpatterns = patterns('',
    url(r'^server/', include(test_server.get_urls())),
    url(r'^client/', include(test_client.get_urls())),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url('^$', lambda request: HttpResponse('home'), name='root')
)
