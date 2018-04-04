# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.hashers import is_password_usable
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.test.testcases import TestCase
from simple_sso.sso_server.models import Token, Consumer
from simple_sso.test_urls import test_client
from simple_sso.test_utils.context_managers import (SettingsOverride, 
    UserLoginContext)
from simple_sso.utils import gen_secret_key
from webservices.sync import DjangoTestingConsumer

from .compat import reverse, urlparse


class SimpleSSOTests(TestCase):
    urls = 'simple_sso.test_urls'

    def setUp(self):
        import requests
        def get(url, params={}, headers={}, cookies=None, auth=None, **kwargs):
            return self.client.get(url, params)
        requests.get = get
        test_client.consumer = DjangoTestingConsumer(self.client, test_client.server_url, test_client.public_key, test_client.private_key)

    def _get_consumer(self):
        return Consumer.objects.create(name='test', private_key=settings.SSO_PRIVATE_KEY, public_key=settings.SSO_PUBLIC_KEY)
    
    def test_walkthrough(self):
        USERNAME = PASSWORD = 'myuser'
        server_user = User.objects.create_user(USERNAME, 'my@user.com', PASSWORD)
        consumer = self._get_consumer()
        # verify theres no tokens yet
        self.assertEqual(Token.objects.count(), 0)
        response = self.client.get(reverse('simple-sso-login'))
        # there should be a token now
        self.assertEqual(Token.objects.count(), 1)
        # this should be a HttpResponseRedirect
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        # check that it's the URL we expect
        url = urlparse(response['Location'])
        path = url.path
        self.assertEqual(path, reverse('simple-sso-authorize'))
        # follow that redirect
        response = self.client.get(response['Location'])
        # now we should have another redirect to the login
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code, response.content)
        # check that the URL is correct
        url = urlparse(response['Location'])
        path = url.path
        self.assertEqual(path, reverse('login'))
        # follow that redirect
        login_url = response['Location']
        response = self.client.get(login_url)
        # now we should have a 200
        self.assertEqual(response.status_code, HttpResponse.status_code)
        # and log in using the username/password from above
        response = self.client.post(login_url, {'username': USERNAME, 'password': PASSWORD})
        # now we should have a redirect back to the authorize view
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        # check that it's the URL we expect
        url = urlparse(response['Location'])
        path = url.path
        self.assertEqual(path, reverse('simple-sso-authorize'))
        # follow that redirect
        response = self.client.get(response['Location'])
        # this should again be a redirect
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        # this time back to the client app, confirm that!
        url = urlparse(response['Location'])
        path = url.path
        self.assertEqual(path, reverse('simple-sso-authenticate'))
        # follow it again
        response = self.client.get(response['Location'])
        # again a redirect! This time to /
        url = urlparse(response['Location'])
        path = url.path
        self.assertEqual(path, reverse('root'))
        # if we follow to root now, we should be logged in
        response = self.client.get(response['Location'])
        client_user = get_user(self.client)
        self.assertFalse(is_password_usable(client_user.password))
        self.assertTrue(is_password_usable(server_user.password))
        for key in ['username', 'email', 'first_name', 'last_name']:
            self.assertEqual(getattr(client_user, key), getattr(server_user, key))
    
    def test_user_already_logged_in(self):
        USERNAME = PASSWORD = 'myuser'
        server_user = User.objects.create_user(USERNAME, 'my@user.com', PASSWORD)
        consumer = self._get_consumer()
        with UserLoginContext(self, server_user):
            # try logging in and auto-follow all 302s
            self.client.get(reverse('simple-sso-login'), follow=True)
            # check the user
            client_user = get_user(self.client)
            self.assertFalse(is_password_usable(client_user.password))
            self.assertTrue(is_password_usable(server_user.password))
            for key in ['username', 'email', 'first_name', 'last_name']:
                self.assertEqual(getattr(client_user, key), getattr(server_user, key))
    
    def test_custom_keygen(self):
        # WARNING: The following test uses a key generator function that is
        # highly insecure and should never under any circumstances be used in
        # a production enivornment
        with SettingsOverride(SIMPLE_SSO_KEYGENERATOR=lambda length: 'test'):
            self.assertEqual(gen_secret_key(40), 'test')
