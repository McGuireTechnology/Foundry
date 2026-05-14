# Vortex Example Pipeline (End-to-End)

This example pipes sample events through the Vortex ecosystem:

1. `fastapi` accepts events over HTTP.
2. Events are queued in Redis list `vortex:example:events`.
3. `fastapi-worker` consumes queue messages and writes to Postgres table `analytics.example_events_raw`.
4. `dbt-runner` transforms raw events into aggregated model `analytics.example`.
5. `superset` can query `analytics.example` for charts/dashboards.

## 1) Start Services

```bash
docker compose --env-file .env.compose -f compose.yml up -d fastapi fastapi-worker redis postgres pgbouncer dbt-docs superset
```

## 2) Send Sample Events

```bash
curl -X POST http://localhost:8000/example/events \
  -H "Content-Type: application/json" \
  -H "X-API-Version: v1" \
  -d '{"event_type":"page_view","user_id":"u1","value":1,"source":"demo"}'

curl -X POST http://localhost:8000/example/events \
  -H "Content-Type: application/json" \
  -H "X-API-Version: v1" \
  -d '{"event_type":"purchase","user_id":"u1","value":49.99,"source":"demo"}'
```

## 3) Run dbt Transformation

```bash
docker compose --env-file .env.compose -f compose.yml run --rm dbt-runner
```

## 4) Validate in Postgres

```bash
docker compose --env-file .env.compose -f compose.yml exec -T postgres \
  psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-vortex} \
  -c "select * from analytics.example order by event_day desc, event_type;"
```

## 5) Visualize in Superset

- Open `http://localhost:8088`
- Use database connection to Postgres
- Explore table/view `analytics.example`
- Build chart with:
  - Dimension: `event_day`
  - Series: `event_type`
- Metric: `event_count` or `total_value`

## 6) Orchestrate with Airflow

- DAG file: `/opt/airflow/dags/vortex_dbt_example.py` (from `airflow/dags/vortex_dbt_example.py`)
- Schedule: hourly (`0 * * * *`)
- Task: runs `dbt run` against mounted project at `/opt/vortex/dbt`

Bring up or refresh Airflow services after DAG/image updates:

```bash
docker compose --env-file .env.compose -f compose.yml up -d --build \
  airflow-init airflow-webserver airflow-scheduler airflow-worker airflow-triggerer
```

Trigger manually from UI:

- Open `http://localhost:8081`
- DAG: `vortex_dbt_example`
- Click Play

## Notes

- Worker is idempotent on `event_id` with `on conflict do nothing`.
- Queue key can be overridden with `EXAMPLE_QUEUE_KEY`.
- The worker normalizes SQLAlchemy DSN format for psycopg.
