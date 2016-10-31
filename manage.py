#!/usr/bin/python
from django.core.management import execute_manager

urlpatterns = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'simple_sso.sso_server',
    'simple_sso',
    'south',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'manage'

if __name__ == "__main__":
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS = INSTALLED_APPS,
        ROOT_URLCONF = ROOT_URLCONF,
        DATABASES = DATABASES,
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner',
        SIMPLE_SSO_SERVER = '/server/',
    )
    execute_manager(settings)
