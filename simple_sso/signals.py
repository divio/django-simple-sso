
from django.urls import NoReverseMatch, reverse
from simple_sso.settings import settings
from simple_sso.sso_server.models import Token
from webservices.sync import SyncConsumer


def logout_token(sender, request, **kwargs):
    """
    A signal receiver which removes a token when its users logs out.
    """
    tokens = Token.objects.select_related('session').filter(session__session_key=request.session.session_key)

    for token in tokens:
        token.delete()


def logout_sso_client(sender, request, user, **kwargs):
    """
    A signal receiver which notifies the server when the client have logged out.
    """
    access_token = request.session.get('sso_access_token', None)

    if access_token is not None:
        consumer = SyncConsumer(settings.SSO_SERVER_URL,
                                settings.SSO_PUBLIC_KEY, settings.SSO_PRIVATE_KEY)

        try:
            url = reverse('simple-sso-logout')
        except NoReverseMatch:
            # thisisfine
            url = '/logout/'

        data = {'access_token': access_token}
        try:
            consumer.consume(url, data)
        except:
            # Ignore errors for now
            pass
