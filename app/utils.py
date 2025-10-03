import datetime

from mcp.server.fastmcp import Context

def calendar_service(ctx: Context):
    return ctx.request_context.request.state.service

def utcnow():
    # datetime.utcnow is deprecated.
    return datetime.datetime.now(datetime.UTC)
