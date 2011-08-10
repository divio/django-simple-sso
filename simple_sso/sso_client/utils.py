# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson
from simple_sso.utils import SIMPLE_KEYS

def load_json_user(json):
    """
    Given a JSON string, returns a Django User instance.
    """
    data = simplejson.loads(json)
    try:
        user = User.objects.get(username=data['username'])
    except User.DoesNotExist:
        user = User()
    
    for key in SIMPLE_KEYS:
        setattr(user, key, data[key])
    user.set_unusable_password()
    user.save()
    
    ctype_cache = {}
    
    permissions = []
    
    for perm in data['permissions']:
        ctype = ctype_cache.get(perm['content_type'], None)
        if not ctype:
            try:
                ctype = ContentType.objects.get_by_natural_key(perm['content_type'])
            except ContentType.DoesNotExist:
                continue
            ctype_cache[perm['content_type']] = ctype
        try:
            permission = Permission.objects.get(content_type=ctype, codename=perm['codename'])
        except Permission.DoesNotExist:
            continue
        permissions.append(permission)
    
    user.user_permissions = permissions
    return user
