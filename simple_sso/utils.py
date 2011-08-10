# -*- coding: utf-8 -*-
from random import choice
import string

KEY_CHARACTERS = string.letters + string.digits

def gen_secret_key(length=40):
    return ''.join([choice(KEY_CHARACTERS) for _ in range(length)])
