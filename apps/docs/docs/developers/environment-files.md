# Environment Files

## Application

- `.env`: local runtime values
- `.env.example`: template to commit

## Compose

- `.env.compose`: compose/runtime values
- `.env.compose.example`: template to commit

## pgAdmin

Configured in `.env.compose`:
- `PGADMIN_DEFAULT_EMAIL`
- `PGADMIN_DEFAULT_PASSWORD`
Default values:
- `admin@example.com`
- `changethis`

Preloaded server connections are defined in `infra/pgadmin/servers.json`.

## Postgres

Configured in `.env.compose`:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
Default values:
- `foundry`
- `postgres`
- `postgres`
