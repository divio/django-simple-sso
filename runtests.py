# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys


INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'simple_sso.sso_server',
    'simple_sso',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'simple_sso.test_urls'


def run_tests():
    import django
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS=INSTALLED_APPS,
        ROOT_URLCONF=ROOT_URLCONF,
        DATABASES=DATABASES,
        SSO_PRIVATE_KEY='private',
        SSO_PUBLIC_KEY='public',
        SSO_SERVER='http://localhost/server/',
        MIDDLEWARE=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        TEMPLATES=[{
            'NAME': 'django',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'debug': True,
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.request',
                ],
                'loaders': (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )
            }
        }]
    )
    django.setup()

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(['simple_sso'])
    return failures


if __name__ == "__main__":
    failures = run_tests()
    if failures:
        sys.exit(bool(failures))
