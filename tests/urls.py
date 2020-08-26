from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import re_path, include

from simple_sso.sso_client.client import Client
from simple_sso.sso_server.server import Server

test_server = Server()
test_client = Client(settings.SSO_SERVER, settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY)

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^server/', include(test_server.get_urls())),
    re_path(r'^client/', include(test_client.get_urls())),
    re_path(r'^login/$', LoginView.as_view(template_name='admin/login.html'), name="login"),
    re_path('^$', lambda request: HttpResponse('home'), name='root')
]
