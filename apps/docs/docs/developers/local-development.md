# Local Development

Use this mode when you want to run one or more services directly on your machine.

## Start Everything Locally

```bash
pnpm dev:local
```

## Hybrid Mode

Run Docker stack, stop one container, then run that service locally.

```bash
docker compose stop api
pnpm dev:api
```

```bash
docker compose stop web
pnpm dev:web
```

```bash
docker compose stop docs
pnpm dev:docs
```

When a service runs locally, use direct ports (`8000`, `5173`, `5174`).
