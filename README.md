# Vortex

Vortex is a low-code application platform built on FastAPI, Vue, and VitePress.

## Quick Start

```bash
npm install --prefix web
npm install --prefix docs
docker compose -f compose.yml -f compose.postgres.yml -f api/compose.api.yml -f web/compose.web.yml watch
```

## Documentation

- Local docs site: `http://localhost/docs`
- Docs source: `docs`
- Getting started page: `docs/developers/getting-started.md`
