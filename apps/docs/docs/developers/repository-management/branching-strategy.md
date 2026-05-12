# Branching Strategy

Use short-lived branches and frequent integration with `main`.

- Protected branch: `main`
- Feature branches: `feature/<scope>-<summary>`
- Fix branches: `fix/<scope>-<summary>`
- Chore branches: `chore/<scope>-<summary>`
- Release branches (optional for stabilization): `release/<version>`
- Docs branches: `docs/<scope>-<summary>`
- Test branches: `test/<scope>-<summary>`
- Spike branches: `spike/<scope>-<summary>`

## Branch Name Parts

- `scope`: the primary area of the codebase being changed. Keep it short and stable.
  - Common scopes: `api`, `web`, `docs`, `infra`, `ci`, `auth`, `data`
  - Examples: `feature/api-user-search`, `fix/web-signin-redirect`, `docs/auth-reset-flow`
- `summary`: a brief kebab-case description of the specific change in that scope.
  - Good summaries: `signin-timeout`, `token-refresh-guard`, `repo-management-checklist`
  - Avoid vague summaries like `updates`, `stuff`, or `misc`

## Branch Type Definitions

- `feature`: new user-facing functionality or meaningful new capability.
- `fix`: a bug fix or regression fix for existing behavior.
- `chore`: maintenance work that does not change product behavior (tooling, cleanup, upgrades).
- `release`: release preparation or stabilization work (versioning, final verification, release-only fixes).
- `docs`: documentation-only updates.
- `test`: adding or improving tests without changing runtime behavior.
- `spike`: short-lived research/prototype work used to answer unknowns before implementation.

## Guidelines

- Branch from latest `main`.
- Keep branches small and focused.
- Rebase or merge `main` frequently to reduce drift.
- Delete branches after merge.
- Use lowercase branch names.
- Use kebab-case for `<summary>` (for example, `add-login-lockout`).
- Keep `<scope>` short and stable (for example, `api`, `web`, `docs`, `infra`).
- Include one clear concern per branch.
