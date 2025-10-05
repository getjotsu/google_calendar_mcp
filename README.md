# Google Calendar MCP Server

A multi-tenant Python-based MCP (Model Context Protocol) server that supports streamable-http.

## Requirements
* Python 3.12+
* [uv](https://docs.astral.sh/uv/)

## Getting Started

Client registration is by sending a POST request to the `/register` endpoint with `client_id`, `client_secret` and `redirect_uris`.
```shell
curl -X POST -d 'client_id=GOOGLE_CLIENT_ID&client_secret=GOOGLE_CLIENT_SECRETredirect_uris=[LOCAL_REDIRECT_URI]' http://localhost:8000/register
```

The LOCAL_REDIRECT_URI value is the url of your client and will be different from the one used to create the Google credentials.

## Why?
Why is this server needed when there are many other implementations?  No other Google Calendar MCP server met these requirements:

Requirements:
* **Streamable HTTP Transport** - Must fully support the streamable-http transport for interoperability with remote MCP clients.
* **Multi-Calendar Free/Busy Calculation** - Accurately compute user availability across all calendars (primary and secondary) rather than returning a simple list of events.
* **Event Creation** - Enable scheduling of new events.
* **Retrieve Settings** - Must expose user’s calendar settings such as working hours and default timezone.

Nice to have:
* Multi-tenancy


## Development
```shell
uv sync
cp .env.example .env
python3 manage.py runserver
```
