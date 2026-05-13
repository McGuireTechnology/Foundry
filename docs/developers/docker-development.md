# Docker Development

## Compose Files

- `compose.yml`: base project name
- `compose.postgres.yml`: Postgres
- `api/compose.api.yml`: API
- `web/compose.web.yml`: Web
- `docs/compose.docs.yml`: Docs
- `compose.traefik.yml`: production-style Traefik/TLS overlay

## Default Command

```bash
docker compose -f compose.yml -f compose.postgres.yml -f api/compose.api.yml -f web/compose.web.yml watch
```

## Useful Commands

```bash
docker compose -f compose.yml -f compose.postgres.yml -f api/compose.api.yml -f web/compose.web.yml up --build
docker compose -f compose.yml -f compose.postgres.yml -f api/compose.api.yml -f web/compose.web.yml down
docker compose -f compose.yml -f compose.postgres.yml -f api/compose.api.yml -f web/compose.web.yml logs -f
docker compose -f compose.yml -f compose.postgres.yml up -d postgres
docker compose -f compose.yml -f compose.postgres.yml stop postgres
```

## Production-Like Traefik Overlay

```bash
docker network create traefik-public
docker compose -f compose.yml -f compose.postgres.yml -f api/compose.api.yml -f web/compose.web.yml -f compose.traefik.yml up -d --build
```
