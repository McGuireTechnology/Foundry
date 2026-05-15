# Vortex Vue Frontend

This service is a Vue 3 + Vite frontend served by NGINX in Docker.

## Local Dev

From `vue/`:

```bash
npm install
npm run dev
```

App URL: `http://localhost:5173`

## Production Build (Docker)

From repo root:

```bash
docker compose build vue-nginx
docker compose up -d vue-nginx
```
