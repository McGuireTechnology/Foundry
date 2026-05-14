import json
import os
import time

import psycopg
import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
EXAMPLE_QUEUE_KEY = os.getenv("EXAMPLE_QUEUE_KEY", "vortex:example:events")


def _normalize_pg_dsn(dsn: str) -> str:
    # Compose uses SQLAlchemy-style DSN; psycopg expects postgres:// or postgresql://.
    return dsn.replace("postgresql+psycopg://", "postgresql://", 1)


def _ensure_table(pg_dsn: str) -> None:
    with psycopg.connect(pg_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                create table if not exists analytics.example_events_raw (
                  event_id text primary key,
                  event_type text not null,
                  user_id text not null,
                  value double precision not null,
                  source text not null,
                  api_version text not null,
                  created_at timestamptz not null,
                  ingested_at timestamptz not null default now()
                )
                """
            )
        conn.commit()


def _insert_event(pg_dsn: str, payload: dict) -> None:
    with psycopg.connect(pg_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into analytics.example_events_raw (
                  event_id, event_type, user_id, value, source, api_version, created_at
                ) values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (event_id) do nothing
                """,
                (
                    payload["event_id"],
                    payload["event_type"],
                    payload["user_id"],
                    payload["value"],
                    payload["source"],
                    payload["api_version"],
                    payload["created_at"],
                ),
            )
        conn.commit()


def main() -> None:
    poll = float(os.getenv("FASTAPI_WORKER_POLL_SECONDS", "5"))
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@pgbouncer:5432/vortex")
    pg_dsn = _normalize_pg_dsn(database_url)
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    _ensure_table(pg_dsn)
    while True:
        item = redis_client.brpop(EXAMPLE_QUEUE_KEY, timeout=int(poll))
        if item is None:
            continue

        _, raw = item
        payload = json.loads(raw)
        _insert_event(pg_dsn, payload)
        time.sleep(0.1)


if __name__ == "__main__":
    main()
