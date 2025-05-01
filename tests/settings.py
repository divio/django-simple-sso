import os
import sys


urlpatterns = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'simple_sso.sso_server',
    'simple_sso',
    'tests',
]

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'templates')
        ],
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )
        },
    },
]

MIDDLEWARES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]


def runtests():
    from django import setup
    from django.conf import settings
    from django.test.utils import get_runner

    settings.configure(
        INSTALLED_APPS=INSTALLED_APPS,
        ROOT_URLCONF=ROOT_URLCONF,
        DATABASES=DATABASES,
        TEST_RUNNER='django.test.runner.DiscoverRunner',
        TEMPLATES=TEMPLATES,
        MIDDLEWARE=MIDDLEWARES,
        SSO_PRIVATE_KEY='private',
        SSO_PUBLIC_KEY='public',
        SSO_SERVER='http://localhost/server/',
        SECRET_KEY="secret-key-for-tests",
    )
    setup()

    # Run the test suite, including the extra validation tests.
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(INSTALLED_APPS)
    return failures


def run():
    failures = runtests()
    sys.exit(failures)


if __name__ == '__main__':
    run()
