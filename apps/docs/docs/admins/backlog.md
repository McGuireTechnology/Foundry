# Backlog

This backlog tracks planned work for Foundry.

Status labels:

- `Now`: actively prioritized
- `Next`: queued for upcoming iterations
- `Later`: planned but not yet scheduled

## Now

- [x] Formalize API versioning policy and deprecation timeline.
- [x] Expand API test coverage for auth flows and user endpoints.
- [x] Implement primitive auth UX pages and token-based sign-in lifecycle.
- [x] Add local development CORS support for web-to-api auth requests (`localhost` and `127.0.0.1`).
- [ ] Add CI checks for docs link integrity and markdown linting.
- [ ] Add release workflow checklist tied to changelog updates.

## Next

- [ ] Introduce role-based access control (RBAC) primitives in API.
- [ ] Add observability baseline (structured logs, health metrics, request tracing).
- [ ] Publish SDK usage examples for common auth and user workflows.
- [ ] Add repository-level `CODEOWNERS` for `apps/api`, `apps/web`, and `infra`.
- [ ] Add integration tests validating browser-to-API CORS behavior for auth endpoints.
- [ ] Replace in-memory login attempt tracking with persistent and distributed-safe storage.
- [ ] Move runtime schema mutations from app startup into Alembic migrations (remove `init_db` DDL side effects).
- [ ] Add docs PR preview deployment links to pull requests.
- [ ] Add docs link checking and markdown linting in CI for docs-only and mixed PRs.
- [ ] Add `CODEOWNERS` coverage for docs sections by audience (`users`, `admins`, `developers`, `community`).
- [ ] Add PR template prompts for changelog coverage and docs impact notes.
- [ ] Define docs contribution workflow page with branch conventions and review expectations.
- [ ] Add docs feedback/discussion links for asynchronous community input.

## Later

- [ ] Define plugin/extension model for low-code runtime components.
- [ ] Add production deployment guides for container and cloud targets.
- [ ] Add multi-tenant organization and workspace data model docs.
- [ ] Establish performance budgets and frontend monitoring for web app UX.

## Backlog Maintenance

Update this page when work is added, reprioritized, or completed.
Completed items should move to the changelog when they ship.
