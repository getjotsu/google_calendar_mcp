import typing
from datetime import datetime
from typing import Any

import pydantic


class CalendarResponse(pydantic.BaseModel):
    id: str
    summary: str
    timeZone: str
    accessRole: str
    selected: bool


class ListCalendarsResponse(pydantic.BaseModel):
    calendars: list[CalendarResponse]


class EventResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='allow')

    summary: str
    transparency: typing.Optional[str] = None
    eventType: str

    busy: bool = False

    def model_post_init(self, context: Any, /) -> None:
        self.busy = (self.transparency != 'transparent' or self.eventType in ['outOfOffice', 'focusTime'])


class FindEventsResponse(pydantic.BaseModel):
    events: list[EventResponse]


class FreeBusy(pydantic.BaseModel):
    start: datetime
    end: datetime
    calendar_id: str | None

class FreeBusyResponse(pydantic.BaseModel):
    busy: typing.List[FreeBusy]


class CreateEventResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='allow')
    kind: str


class SettingsResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='allow')
    kind: str
