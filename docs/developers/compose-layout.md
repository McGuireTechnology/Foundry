# Compose Layout

## Base

`compose.yml` defines only the Compose project name.

## Service Files

- `compose.postgres.yml`: Postgres service and persistent volume
- `compose.pgadmin.yml`: pgAdmin service
- `api/compose.api.yml`: API service with healthcheck and watch config
- `web/compose.web.yml`: Web service with watch config
- `docs/compose.docs.yml`: Docs service with watch config

## Traefik Overlay

`compose.traefik.yml` adds host-based HTTPS routing for deployment.
