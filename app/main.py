import typing
from contextlib import asynccontextmanager

import pydantic
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
from mcp.server.fastmcp import FastMCP

from jotsu.mcp.server.routes import RegistrationHandler, RedirectHandler
from jotsu.mcp.local.client_manager import LocalEncryptedClientManager

from . import settings, middleware

from .auth import GoogleAuthServerProvider
from .cache import RedisCache


class MCPServer(FastMCP):

    def __init__(self):
        self.cache = RedisCache()
        self.client_manager = LocalEncryptedClientManager(settings.SECRET)
        auth_server_provider = GoogleAuthServerProvider(cache=self.cache, client_manager=self.client_manager)
        super().__init__(
            name="Google Calendar",
            auth_server_provider=auth_server_provider,
            auth=AuthSettings(
                issuer_url=pydantic.AnyHttpUrl(settings.ISSUER_URL),
                client_registration_options=ClientRegistrationOptions(enabled=False),
                resource_server_url=None
            ),
            json_response=True,
            stateless_http=True,
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
    description="MCP server for interacting with Google Calendar API.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    expose_headers=["Mcp-Session-Id"],   # required by streamable HTTP clients
)

@app.get("/.well_known/agent-card.json")
async def agent_card():
    return {
        "id": settings.EXTERNAL_URL,
        "name": mcp.name,
        "issuer": settings.ISSUER_URL,
        "capabilities": [RegistrationHandler.CAPABILITY],
        "endpoints": {
            "registration_endpoint": f"{settings.EXTERNAL_URL}/register"
        }
    }

streamable_http_app = mcp.streamable_http_app()
app.mount("/", streamable_http_app)
streamable_http_app.add_route("/register", RegistrationHandler(mcp.auth_server_provider).handle, methods=["POST"])
streamable_http_app.add_route("/redirect", RedirectHandler(mcp.auth_server_provider).handle, methods=["GET"])
streamable_http_app.add_middleware(middleware.GoogleServiceMiddleware)
