from django.conf import settings


class NULL:
    pass


class SettingsOverride:
    """
    Overrides Django settings within a context and resets them to their inital
    values on exit.

    Example:

        with SettingsOverride(DEBUG=True):
            # do something
    """

    def __init__(self, **overrides):
        self.overrides = overrides

    def __enter__(self):
        self.old = {}
        for key, value in self.overrides.items():
            self.old[key] = getattr(settings, key, NULL)
            setattr(settings, key, value)

    def __exit__(self, type, value, traceback):
        for key, value in self.old.items():
            if value is not NULL:
                setattr(settings, key, value)
            else:
                delattr(settings, key)  # do not pollute the context!


class UserLoginContext:
    def __init__(self, testcase, user):
        self.testcase = testcase
        self.user = user

    def __enter__(self):
        loginok = self.testcase.client.login(username=self.user.username,
                                             password=self.user.username)
        self.old_user = getattr(self.testcase, 'user', None)
        self.testcase.user = self.user
        self.testcase.assertTrue(loginok)

    def __exit__(self, exc, value, tb):
        self.testcase.user = self.old_user
        if not self.testcase.user:
            delattr(self.testcase, 'user')
        self.testcase.client.logout()
