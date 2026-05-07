# Compose Layout

## Base

`compose.yml` defines:
- `postgres`
- `pgadmin`
- `api`
- `web`
- `docs`

## Local Override

`compose.override.yml` adds:
- local Traefik proxy (`proxy`)
- local ports
- `develop.watch` sync/rebuild rules
- local path-based routes (`/api`, `/docs`, `/pgadmin`)

## Traefik Overlay

`compose.traefik.yml` adds host-based HTTPS routing for deployment.
