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
- local host-based routes (`api.localhost`, `docs.localhost`, `pgadmin.localhost`)

## Traefik Overlay

`compose.traefik.yml` adds host-based HTTPS routing for deployment.
