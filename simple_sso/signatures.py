# -*- coding: utf-8 -*-
import hashlib
import hmac
import urllib


def build_signature(parameters, secret):
    """
    Builds the signature for the parameters and the body given.
    
    Parameters is a list of tuples.
    """
    message = urllib.urlencode(sorted(parameters))
    return hmac.new(secret.encode('ascii'), message.encode('ascii'), hashlib.sha256).hexdigest()

def verify_signature(parameters, signature, secret):
    """
    Verifies the signature
    
    Parameters is a list of tuples.
    """
    return build_signature(parameters, secret) == signature
