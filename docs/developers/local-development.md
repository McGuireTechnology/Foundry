# Local Development

Use this mode when you want to run one or more services directly on your machine.

## Start Everything Locally

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Hybrid Mode

Run Docker stack, stop one container, then run that service locally.

```bash
docker compose stop api
python -m uvicorn app.main:app --reload --port 8000
```

```bash
docker compose stop web
npm run dev --prefix web
```

```bash
docker compose stop docs
npm run dev --prefix docs
```

When a service runs locally, use direct ports (`8000`, `5173`, `5174`).
