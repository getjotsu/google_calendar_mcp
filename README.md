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

## Development
```shell
uv sync
cp .env.example .env
python3 manage.py runserver
```
