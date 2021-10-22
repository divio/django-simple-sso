from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_out


class SimpleSSOServer(AppConfig):
    name = 'simple_sso.sso_server'

    def ready(self):
        from simple_sso.signals import logout_token
        user_logged_out.connect(logout_token, dispatch_uid='logout_token')
