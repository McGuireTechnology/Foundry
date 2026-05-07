# Docker Development

## Compose Files

- `compose.yml`: base services
- `compose.override.yml`: local development behavior and watch rules
- `compose.traefik.yml`: production-style Traefik/TLS overlay

## Default Command

```bash
docker compose watch
```

## Useful Commands

```bash
docker compose up --build
docker compose down
docker compose logs -f
docker compose up -d postgres
docker compose stop postgres
```

## Production-Like Traefik Overlay

```bash
docker network create traefik-public
docker compose -f compose.yml -f compose.traefik.yml --env-file .env.compose up -d --build
```
