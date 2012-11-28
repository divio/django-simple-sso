# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from simple_sso.utils import gen_secret_key
import datetime


def gen_client_key(field):
    """
    Helper function to give default values to Client.secret and Client.key
    """
    def _genkey():
        key = gen_secret_key(64)
        while Consumer.objects.filter(**{field: key}).exists():
            key = gen_secret_key(64)
        return key
    return _genkey

def gen_token_field(field):
    """
    Helper function to give default values to Client.secret and Client.key
    """
    def _genkey():
        key = gen_secret_key(64)
        while Token.objects.filter(**{field: key}).exists():
            key = gen_secret_key(64)
        return key
    return _genkey


class Consumer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    private_key = models.CharField(max_length=64, unique=True, default=gen_client_key('private_key'))
    public_key = models.CharField(max_length=64, unique=True, default=gen_client_key('public_key'))
    
    def __unicode__(self):
        return self.name
    
    def rotate_keys(self):
        self.secret = gen_client_key('private_key')()
        self.key = gen_client_key('public_key')()
        self.save()


class Token(models.Model):
    consumer = models.ForeignKey(Consumer, related_name='tokens')
    request_token = models.CharField(unique=True, max_length=64, default=gen_token_field('request_token'))
    access_token = models.CharField(unique=True, max_length=64, default=gen_token_field('access_token'))
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    redirect_to = models.CharField(max_length=255)
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), null=True)

    def refresh(self):
        self.timestamp = datetime.datetime.now()
        self.save()
