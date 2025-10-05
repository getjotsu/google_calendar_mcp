from starlette.concurrency import run_in_threadpool

from . import models
from .utils import calendar_service
from .main import mcp


@mcp.resource('mcp://google-calendar/settings', mime_type='application/json')
async def settings() -> models.SettingsResponse:
    service = calendar_service()

    res = await run_in_threadpool(
        service.settings().list().execute
    )
    return models.SettingsResponse(**res)
