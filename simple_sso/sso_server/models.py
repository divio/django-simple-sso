# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query_utils import Q
from simple_sso.utils import gen_secret_key
import datetime


def gen_client_key(field):
    """
    Helper function to give default values to Client.secret and Client.key
    """
    def _genkey():
        key = gen_secret_key(64)
        while Client.objects.filter(**{field: key}).exists():
            key = gen_secret_key(64)
        return key
    return _genkey


class TokenManager(models.Manager):
    def create_for_client(self, client):
        """
        Create a new token for a client object.
        """
        request_token = gen_secret_key(64)
        auth_token = gen_secret_key(64)
        # check unique constraints
        while self.filter(Q(request_token=request_token) | Q(auth_token=auth_token)).exists():
            request_token = gen_secret_key(64)
            auth_token = gen_secret_key(64)
        return self.create(
            client=client,
            request_token=request_token,
            auth_token=auth_token,
        )


class Client(models.Model):
    """
    A client. If secret/key change, the client website has to be updated too!
    """
    secret = models.CharField(max_length=64, unique=True, default=gen_client_key('secret'))
    key = models.CharField(max_length=64, unique=True, default=gen_client_key('key'))
    root_url = models.URLField(verify_exists=False)
    
    def __unicode__(self):
        return self.root_url
    
    def rotate_keys(self):
        self.secret = gen_client_key('secret')()
        self.key = gen_client_key('key')()
        self.save()


class Token(models.Model):
    """
    An auth token used to authenticate a user.
    """
    client = models.ForeignKey(Client)
    request_token = models.CharField(max_length=64, unique=True)
    auth_token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey('auth.User', null=True)
    created = models.DateTimeField(default=datetime.datetime.now)
    
    objects = TokenManager()
