from jotsu.mcp.server import AsyncCache, AsyncClientManager, PassThruAuthServerProvider

from app import settings


class GoogleAuthServerProvider(PassThruAuthServerProvider):

    def __init__(self, cache: AsyncCache, client_manager: AsyncClientManager):
        super().__init__(
            issuer_url=settings.ISSUER_URL,
            cache=cache,
            client_manager=client_manager,
            secret_key=settings.SECRET,
            authorization_endpoint="https://accounts.google.com/o/oauth2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
            scope='https://www.googleapis.com/auth/calendar'
        )
