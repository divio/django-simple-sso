# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import simplejson
from django_load.core import load_object


def default_construct_user(user):
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

constructor_setting = getattr(settings, 'SIMPLE_SSO_USER_CONSTRUCTOR', None)
if constructor_setting:
    construct_user = load_object(constructor_setting)
else:
    construct_user = default_construct_user

def get_user_json(user):
    data = construct_user(user)
    return simplejson.dumps(data)
