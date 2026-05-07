# Foundry Architecture and Milestones

## Monorepo Layout

- apps/api: FastAPI service, auth, metadata APIs, app runtime endpoints
- apps/web: Vue builder and app runtime shell
- apps/docs: VitePress docs and onboarding
- packages/shared-types: shared domain contracts
- packages/sdk-js: client SDK for frontend and external integrations
- infra/docker: local container orchestration

## Backend Boundaries (FastAPI)

- Auth and tenancy: organizations, users, roles
- Metadata layer: apps, pages, components, fields, rules
- Runtime layer: evaluates metadata to serve app behavior
- Connector layer: start with Postgres, then generic SQL adapters
- Job layer: async workflows and scheduled tasks via Redis-backed worker

## Frontend Boundaries (Vue)

- Builder shell: navigation, project switcher, publish flow
- Schema editors: data model, page layout, component properties
- Logic builder: triggers, conditions, actions
- Runtime renderer: interprets published schema into user-facing apps

## Docs Boundaries (VitePress)

- Product guide: how to build and publish first app
- Operator guide: self-hosting, env vars, deployment
- API reference: endpoints and SDK usage

## First Two Weeks (Execution Plan)

1. Week 1: Platform skeleton
- Finalize app/project schema and persistence model
- Implement auth stub and org/project CRUD
- Add frontend project dashboard and API wiring
- Add docs quickstart and local dev instructions

2. Week 2: First usable low-code slice
- Implement table schema editor (create fields, types)
- Implement form page schema + runtime form renderer
- Add submit action to persist records through API
- Ship end-to-end demo: create app -> define form -> submit data

## Acceptance Criteria for v0.1

- User can create an organization and project
- User can define one table with typed fields
- User can create one form page bound to that table
- Published runtime form can create records through API
- Docs include a complete 10-minute quickstart