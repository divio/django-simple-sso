# -*- coding: utf-8 -*-
from random import SystemRandom
from django.conf import settings
import string
random = SystemRandom()

KEY_CHARACTERS = string.letters + string.digits

def default_gen_secret_key(length=40):
    return ''.join([random.choice(KEY_CHARACTERS) for _ in range(length)])

def gen_secret_key(length=40):
    generator = getattr(settings, 'SIMPLE_SSO_KEYGENERATOR', default_gen_secret_key)
    return generator(length)
