from django.conf import settings

settings.SSO_KEEP_ALIVE = getattr(settings, 'SSO_KEEP_ALIVE', 60)
settings.SSO_TOKEN_TIMEOUT = getattr(settings, 'SSO_TOKEN_TIMEOUT', 300)
settings.SSO_TOKEN_VERIFY_TIMEOUT = getattr(settings, 'SSO_TOKEN_VERIFY_TIMEOUT', 3600)
