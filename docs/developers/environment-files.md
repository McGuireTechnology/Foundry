# Environment Files

## Application

- `.env.compose`: local compose/service values
- `.env.example`: template to commit

## Compose

- `.env.compose.example`: compose/service template to commit

## pgAdmin

Defaults (overridable via shell env or `.env.compose`):
- `PGADMIN_DEFAULT_EMAIL`
- `PGADMIN_DEFAULT_PASSWORD`
Default values:
- `admin@example.com`
- `changethis`

Preloaded server connections are defined in `infra/pgadmin/servers.json`.

## Postgres

Defaults (overridable via shell env or `.env.compose`):
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
Default values:
- `vortex`
- `postgres`
- `postgres`
