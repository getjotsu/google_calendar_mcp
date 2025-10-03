import warnings

from starlette.config import Config

with warnings.catch_warnings(action='ignore'):
    # Suppress - UserWarning: Config file '.env' not found.
    config = Config('.env')

EXTERNAL_URL = config('EXTERNAL_URL', default='http://localhost:8000/')
ISSUER_URL = config('ISSUER_URL', default=EXTERNAL_URL)

SECRET = config('SECRET')  # must be 32 characters
assert len(SECRET) == 32

CLIENTS_PATH = config('CLIENTS_PATH', default=None)

REDIS_URL = config('REDIS_URL', default='redis://localhost:6379?decode_responses=True')
