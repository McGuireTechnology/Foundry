import json
import os
import uuid
from datetime import UTC, datetime

import redis
from fastapi import FastAPI, Header
from pydantic import BaseModel, Field


app = FastAPI(title="Vortex FastAPI")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
EXAMPLE_QUEUE_KEY = os.getenv("EXAMPLE_QUEUE_KEY", "vortex:example:events")


class ExampleEventIn(BaseModel):
    event_type: str = Field(description="Logical event name, for example: page_view")
    user_id: str = Field(description="User identifier")
    value: float = Field(default=1.0, description="Optional numeric value for aggregations")
    source: str = Field(default="fastapi", description="Origin service")


def _redis_client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


@app.get("/health")
def health(x_api_version: str | None = Header(default=None, alias="X-API-Version")) -> dict[str, str]:
    return {"status": "ok", "api_version": x_api_version or "unknown"}


@app.post("/example/events")
def enqueue_example_event(
    payload: ExampleEventIn,
    x_api_version: str | None = Header(default=None, alias="X-API-Version"),
) -> dict[str, str | int]:
    event_id = str(uuid.uuid4())
    body = {
        "event_id": event_id,
        "event_type": payload.event_type,
        "user_id": payload.user_id,
        "value": payload.value,
        "source": payload.source,
        "created_at": datetime.now(UTC).isoformat(),
        "api_version": x_api_version or "unknown",
    }
    client = _redis_client()
    client.lpush(EXAMPLE_QUEUE_KEY, json.dumps(body))
    queue_depth = client.llen(EXAMPLE_QUEUE_KEY)
    return {"status": "queued", "event_id": event_id, "queue_depth": queue_depth}
