from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_out


class SimpleSSOClient(AppConfig):
    name = 'simple_sso.sso_client'

    def ready(self):
        from simple_sso.signals import logout_sso_client
        user_logged_out.connect(
            logout_sso_client, dispatch_uid='logout_sso_client')
