# Architecture

Foundry uses a monorepo with three primary apps:

- FastAPI backend (`apps/api`)
- Vue builder/runtime frontend (`apps/web`)
- VitePress documentation (`apps/docs`)

Shared contracts live under `packages/`.