from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from ..utils import gen_secret_key


@deconstructible
class SecretKeyGenerator:
    """
    Helper to give default values to Client.secret and Client.key
    """

    def __init__(self, field):
        self.field = field

    def __call__(self):
        key = gen_secret_key(64)
        while self.get_model().objects.filter(**{self.field: key}).exists():
            key = gen_secret_key(64)
        return key


class ConsumerSecretKeyGenerator(SecretKeyGenerator):
    def get_model(self):
        return Consumer


class TokenSecretKeyGenerator(SecretKeyGenerator):
    def get_model(self):
        return Token


class Consumer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    private_key = models.CharField(
        max_length=64, unique=True,
        default=ConsumerSecretKeyGenerator('private_key')
    )
    public_key = models.CharField(
        max_length=64, unique=True,
        default=ConsumerSecretKeyGenerator('public_key')
    )

    def __unicode__(self):
        return self.name

    def rotate_keys(self):
        self.secret = ConsumerSecretKeyGenerator('private_key')()
        self.key = ConsumerSecretKeyGenerator('public_key')()
        self.save()


class Token(models.Model):
    consumer = models.ForeignKey(
        Consumer,
        related_name='tokens',
        on_delete=models.CASCADE,
    )
    request_token = models.CharField(
        unique=True, max_length=64,
        default=TokenSecretKeyGenerator('request_token')
    )
    access_token = models.CharField(
        unique=True, max_length=64,
        default=TokenSecretKeyGenerator('access_token')
    )
    timestamp = models.DateTimeField(default=timezone.now)
    redirect_to = models.CharField(max_length=1023)
    user = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        null=True,
        on_delete=models.CASCADE,
    )

    def refresh(self):
        self.timestamp = timezone.now()
        self.save()
