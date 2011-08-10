# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import simplejson
from django_load.core import load_object


def default_construct_user(user, client):
    """
    Default user constructor. Ignores the client and returns the Django User
    as a dictionary with the fields required by the specifications.
    """
    simple_keys = [
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_superuser',
    ]
    data = {}
    for key in simple_keys:
        data[key] = getattr(user, key)
    data['permissions'] = []
    for perm in user.user_permissions.select_related('content_type').all():
        data['permissions'].append({
            'content_type': perm.content_type.natural_key(),
            'codename': perm.codename,
        })
    return data

def construct_user(user, client):
    # load custom constructor if available
    constructor_setting = getattr(settings, 'SIMPLE_SSO_USER_CONSTRUCTOR', None)
    if constructor_setting:
        return load_object(constructor_setting)(user, client)
    else:
        return default_construct_user(user, client)

def get_user_json(user, client):
    """
    Returns the JSON string representation of the user object for a client.
    """
    data = construct_user(user, client)
    return simplejson.dumps(data)
