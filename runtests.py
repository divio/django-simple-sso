# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
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

def teardown(state):
    from django.conf import settings
    # Restore the old settings.
    for key, value in state.items():
        setattr(settings, key, value)

def run_tests():
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS = INSTALLED_APPS,
        ROOT_URLCONF = 'runtests',
        DATABASES = DATABASES,
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner',
    )

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
    