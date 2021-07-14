import time
from importlib import import_module

from simple_sso.settings import settings
from django.urls import NoReverseMatch, reverse
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

from webservices.sync import SyncConsumer


class PostAuthenticationMiddleware(MiddlewareMixin):
    # RemovedInDjango40Warning: when the deprecation ends, replace with:
    #   def __init__(self, get_response):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore
        self.consumer = SyncConsumer(
            settings.SSO_SERVER_URL, settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY)

    def process_request(self, request):
        access_token = request.session.get('sso_access_token', None)
        if access_token is not None:
            last_check = request.session.get('sso_last_verify', 0)
            if last_check == 0:
                request.session['sso_last_verify'] = time.time()
            elif last_check+settings.SSO_KEEP_ALIVE < time.time():
                if not self.verifySession(request, access_token):
                    logout(request)

    def verifySession(self, request, access_token):
        try:
            url = reverse('simple-sso-verify')
        except NoReverseMatch:
            # thisisfine
            url = '/verify/'

        data = {'access_token': access_token}
        try:
            user_data = self.consumer.consume(url, data)
            # Just a simple test that username is defined, non empty and matches the logged user
            return user_data['username'] == request.user.username
        except:
            # If any error ocurred we can consider that there is no valid logged user
            return False
