# Getting Started

## Prerequisites

- Docker Desktop running (Linux containers)
- Node.js 20+
- pnpm 10+

## Install

```bash
pnpm install
```

## Start Development Stack

```bash
docker compose watch
```

## Default Access Points

- App: `http://app.localhost` (also `http://localhost`)
- API: `http://api.localhost`
- Docs: `http://docs.localhost`
- pgAdmin: `http://pgadmin.localhost` (or `http://localhost:5050`)
- Traefik dashboard: `http://localhost:8090`

## Default Credentials

- Postgres user: `postgres`
- Postgres password: `postgres`
- pgAdmin email: `admin@example.com`
- pgAdmin password: `changethis`
