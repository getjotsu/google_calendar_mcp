FROM python:3.13.7

WORKDIR /src

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml /src/pyproject.toml
COPY ./uv.lock /src/uv.lock
RUN uv sync --locked

COPY ./app /src/app

# Env defaults; tune via env in compose
ENV WEB_CONCURRENCY=4 \
    GUNICORN_TIMEOUT=60 \
    GUNICORN_KEEPALIVE=5 \
    PATH="$PATH:/src/.venv/bin"

CMD exec gunicorn "app.main:app" \
    -k uvicorn.workers.UvicornWorker \
    --workers ${WEB_CONCURRENCY} \
    --bind 0.0.0.0:8000 \
    --timeout ${GUNICORN_TIMEOUT} \
    --graceful-timeout 30 \
    --keep-alive ${GUNICORN_KEEPALIVE} \
    --max-requests 1000 --max-requests-jitter 100 \
    --access-logfile - \
    --log-level info \
    --chdir /src