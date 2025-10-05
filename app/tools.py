import logging
import typing
from datetime import datetime, timedelta

from mcp.server.fastmcp import Context
from starlette.concurrency import run_in_threadpool

from . import models
from .main import mcp
from .utils import calendar_service, utcnow

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_calendars(ctx: Context) -> models.ListCalendarsResponse:
    """Get information about all accessible calendars.

    Returns:
        An object containing 'calendars', a list of calendar details.
    """
    service = calendar_service(ctx)
    res = await run_in_threadpool(service.calendarList().list().execute)
    return models.ListCalendarsResponse(calendars=res.get('items', []))


@mcp.tool()
async def find_events(
    ctx: Context,
    calendar_id: str = 'primary',
    time_min: datetime = None,
    time_max: datetime = None,
) -> models.FindEventsResponse:
    """Get calendar events in the specified time range.

    Args:
        calendar_id: Calendar identifier (usually the user email).
        time_min: Start of the time range (inclusive). If None, defaults to the current time.
        time_max: End of the time range (exclusive). If None, no upper bound.

    Returns:
        An object containing 'events', a list of event details.
    """
    service = calendar_service(ctx)

    kwargs = {
        'calendarId': calendar_id,
        'timeMin': time_min.isoformat() if time_min else utcnow().isoformat(),
        'singleEvents': True,
        'orderBy': 'startTime',
    }
    if time_max:
        kwargs['timeMax'] = time_max.isoformat()

    res = await run_in_threadpool(service.events().list(**kwargs).execute)
    return models.FindEventsResponse(events=res.get('items', []))


# noinspection PyIncorrectDocstring
@mcp.tool()
async def free_busy(
    ctx: Context,
    calendar_ids: typing.List[str] = None,
    time_min: datetime = None,
    time_max: datetime = None,
) -> models.FreeBusyResponse:
    """Finds free/busy information for the given calendar.

    Args:
        calendar_ids: List of calendar identifiers .
        time_min: Start time range (inclusive).
        time_max: End time range (exclusive).

    Returns:
        An object containing 'busy', a list of event start and end times.
    """
    service = calendar_service(ctx)
    calendar_ids = calendar_ids if calendar_ids else ['primary']

    if not time_min:
        time_min = utcnow()

    if not time_max:
        # default to one week.
        time_max = time_min + timedelta(days=7)

    kwargs = {
        'timeMin': time_min.isoformat(),
        'timeMax': time_max.isoformat(),
        'items': [{'id': calendar_id} for calendar_id in calendar_ids],
    }

    res = await run_in_threadpool(service.freebusy().query(body=kwargs).execute)
    print(res)

    busy = []
    for calendar_id, calendar in res.get('calendars', {}).items():
        for item in calendar.get('busy', []):
            busy.append(models.FreeBusy(start=item['start'], end=item['end'], calendar_id=calendar_id))

    return models.FreeBusyResponse(busy=busy)


# noinspection PyIncorrectDocstring
@mcp.tool()
async def create_event(
    ctx: Context,
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = 'primary',
    description: typing.Optional[str] = None,
    location: typing.Optional[str] = None,
    attendees: typing.Optional[list[str]] = None,
    transparency: typing.Optional[typing.Literal['opaque', 'transparent']] = 'opaque'
) -> models.CreateEventResponse:
    """
    Creates a new event.

    Args:
        calendar_id: Calendar identifier (usually the user email, default='primary').
        summary (str): Event title.
        start_time (str): Start time or just date for all day.
        end_time (str): End time or just data for all day.
        description (Optional[str]): Event description.
        location (Optional[str]): Event location.
        attendees (Optional[List[str]]): Attendee email addresses.
        transparency ('opaque or 'transparent', default='opaque'): opaque marks the event as busy, transparent does not.
    Returns:
        str: Confirmation message of the successful event creation with event link.
    """

    def _date_param(value: str):
        return {'date': start_time} if 'T' not in value else {'dateTime': start_time}

    service = calendar_service(ctx)

    body: typing.Dict[str, typing.Any] = {
        'summary': summary,
        'start': _date_param(start_time),
        'end': _date_param(end_time),
        'transparency': transparency
    }

    if location:
        body['location'] = location
    if description:
        body['description'] = description
    if attendees:
        body['attendees'] = [{'email': email} for email in attendees]

    res = await run_in_threadpool(
        service.events().insert(calendarId=calendar_id, body=body).execute
    )
    return models.CreateEventResponse(**res)
