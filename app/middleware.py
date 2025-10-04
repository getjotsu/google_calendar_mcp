import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import jwt

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from . import settings

logger = logging.getLogger(__name__)


def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=['HS256'])
        return payload['token']
    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError) as e:
        logger.info('Invalid JWT: %s', str(e))
    return None


class GoogleServiceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization = request.headers.get('authorization')
        if authorization:
            _, bearer_token = authorization.split(' ', 1)
            google_access_token = decode_jwt(bearer_token)
            if google_access_token:
                credentials = Credentials(google_access_token)
                service = build('calendar', 'v3', credentials=credentials)
                request.state.service = service
        response = await call_next(request)
        request.state.service = None
        return response
