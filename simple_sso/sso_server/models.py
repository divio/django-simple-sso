# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query_utils import Q
from simple_sso.utils import gen_secret_key


def gen_client_key(field):
    def _genkey():
        key = gen_secret_key(64)
        while Client.objects.filter(**{field: key}).exists():
            key = gen_secret_key(64)
        return key
    return _genkey


class TokenManager(models.Manager):
    def create_for_client(self, client):
        request_token = gen_secret_key(64)
        auth_token = gen_secret_key(64)
        while self.filter(Q(request_token=request_token) | Q(auth_token=auth_token)).exists():
            request_token = gen_secret_key(64)
            auth_token = gen_secret_key(64)
        return self.create(
            client=client,
            request_token=request_token,
            auth_token=auth_token,
        )


class Client(models.Model):
    secret = models.CharField(max_length=64, unique=True, default=gen_client_key('secret'))
    key = models.CharField(max_length=64, unique=True, default=gen_client_key('key'))
    root_url = models.URLField(verify_exists=False)


class Token(models.Model):
    client = models.ForeignKey(Client)
    request_token = models.CharField(max_length=64, unique=True)
    auth_token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey('auth.User', null=True)
    
    objects = TokenManager()
