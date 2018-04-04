import django

try:
    # python 3
    # noinspection PyCompatibility
    from urllib.parse import urlparse, urlunparse, urljoin, urlencode
except ImportError:
    # python 2
    # noinspection PyCompatibility
    from urlparse import urlparse, urlunparse, urljoin
    from urllib import urlencode

try:
    from django.urls import NoReverseMatch
    from django.urls import reverse
    from django.urls import reverse_lazy
except ImportError:
    from django.core.urlresolvers import NoReverseMatch
    from django.core.urlresolvers import reverse  # NOQA
    from django.core.urlresolvers import reverse_lazy  # NOQA


DJANGO_GTE_10 = django.VERSION >= (1, 10)


def user_is_authenticated(user):
    if DJANGO_GTE_10:
        return user.is_authenticated
    return user.is_authenticated()
