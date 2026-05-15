FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY fastapi/pyproject.toml /app/pyproject.toml
COPY fastapi/alembic.ini /app/alembic.ini
COPY fastapi/scripts /app/scripts
COPY fastapi/app /app/app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev

RUN chmod +x /app/scripts/*.sh

EXPOSE 8000

CMD ["bash", "-c", "/app/scripts/prestart.sh && fastapi run --workers 2 app/main.py --host 0.0.0.0 --port 8000"]
