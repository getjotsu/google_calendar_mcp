import datetime

from mcp.server.fastmcp import Context
from mcp.server.lowlevel.server import request_ctx


def calendar_service(ctx: Context = None):
    if ctx:
        request_context = ctx.request_context
    else:
        request_context = request_ctx.get()
    return request_context.request.state.service


def utcnow():
    # datetime.utcnow is deprecated.
    return datetime.datetime.now(datetime.UTC)
