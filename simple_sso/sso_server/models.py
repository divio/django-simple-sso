# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.db import models
from django.utils.deconstruct import deconstructible

from ..utils import gen_secret_key


@deconstructible
class SecretKeyGenerator(object):
    """
    Helper to give default values to Client.secret and Client.key
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, instance):
        key = gen_secret_key(64)
        while instance._meta.model.objects.filter(**{self.field: key}).exists():
            key = gen_secret_key(64)
        return key

    def __eq__(self, other):
        return self.field == other.field


class Consumer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    private_key = models.CharField(max_length=64, unique=True, default=SecretKeyGenerator('private_key'))
    public_key = models.CharField(max_length=64, unique=True, default=SecretKeyGenerator('public_key'))

    def __unicode__(self):
        return self.name

    def rotate_keys(self):
        self.secret = SecretKeyGenerator('private_key')()
        self.key = SecretKeyGenerator('public_key')()
        self.save()


class Token(models.Model):
    consumer = models.ForeignKey(Consumer, related_name='tokens')
    request_token = models.CharField(unique=True, max_length=64, default=SecretKeyGenerator('request_token'))
    access_token = models.CharField(unique=True, max_length=64, default=SecretKeyGenerator('access_token'))
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    redirect_to = models.CharField(max_length=255)
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null=True)

    def refresh(self):
        self.timestamp = datetime.datetime.now()
        self.save()
