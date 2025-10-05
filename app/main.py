import typing
from contextlib import asynccontextmanager

import pydantic
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from mcp.server.auth.routes import build_metadata
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
from mcp.server.fastmcp import FastMCP

from jotsu.mcp.server.routes import StaticRegistrationHandler, RedirectHandler
from jotsu.mcp.local.client_manager import LocalEncryptedClientManager

from . import settings, middleware

from .auth import GoogleAuthServerProvider
from .cache import RedisCache


class MCPServer(FastMCP):
    def __init__(self):
        self.cache = RedisCache()
        self.client_manager = LocalEncryptedClientManager(settings.SECRET)

        auth = AuthSettings(
            issuer_url=pydantic.AnyHttpUrl(settings.ISSUER_URL),
            client_registration_options=ClientRegistrationOptions(enabled=False),
            resource_server_url=None,
        )
        auth_server_provider = GoogleAuthServerProvider(
            cache=self.cache, client_manager=self.client_manager
        )
        super().__init__(
            name='Google Calendar',
            auth_server_provider=auth_server_provider,
            auth=auth,
            json_response=True,
            stateless_http=True,
        )

        self.metadata = build_metadata(
            issuer_url=self.settings.auth.issuer_url,
            service_documentation_url=self.settings.auth.service_documentation_url,
            client_registration_options=self.settings.auth.client_registration_options,
            revocation_options=self.settings.auth.revocation_options or RevocationOptions(),
        ).model_dump(mode='json', exclude_none=True)
        self.metadata['static_registration_endpoint'] = (
            f'{settings.EXTERNAL_URL}/static_register'
        )

    @property
    def auth_server_provider(self):
        return typing.cast(GoogleAuthServerProvider, self._auth_server_provider)


mcp = MCPServer()


# --- FastAPI app w/ proper MCP session lifecycle ---
@asynccontextmanager
async def lifespan(*_args, **_kwargs):
    # Start/stop the MCP session manager
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    name=mcp.name,
    description='MCP server for interacting with Google Calendar API.',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET', 'POST', 'DELETE'],
    expose_headers=['Mcp-Session-Id'],  # required by streamable HTTP clients
)


@app.get('/.well_known/agent-card.json')
async def agent_card():
    return {
        'id': settings.EXTERNAL_URL,
        'name': mcp.name,
        'issuer': settings.ISSUER_URL,
        'capabilities': [StaticRegistrationHandler.CAPABILITY],
        'endpoints': {
            'static_registration_endpoint': f'{settings.EXTERNAL_URL}/static_register'
        },
    }

@app.api_route('/.well-known/oauth-authorization-server', methods=['GET', 'OPTIONS'])
async def oauth_authorization_server():
    return JSONResponse(
        content=mcp.metadata,
        headers={'Cache-Control': 'public, max-age=3600'},  # Cache for 1 hour
    )


streamable_http_app = mcp.streamable_http_app()
app.mount('/', streamable_http_app)
streamable_http_app.add_route(
    '/static_register',
    StaticRegistrationHandler(mcp.auth_server_provider).handle,
    methods=['POST'],
)
streamable_http_app.add_route(
    '/redirect', RedirectHandler(mcp.auth_server_provider).handle, methods=['GET']
)
streamable_http_app.add_middleware(middleware.GoogleServiceMiddleware)

