# Repository Management

## Branching Strategy

Use a trunk-based model with short-lived branches.

- Protected branch: `main`
- Feature branches: `feature/<scope>-<summary>`
- Fix branches: `fix/<scope>-<summary>`
- Chore branches: `chore/<scope>-<summary>`
- Release branches (optional for stabilization): `release/<version>`

Guidelines:

- Branch from latest `main`.
- Keep branches small and focused.
- Rebase or merge `main` frequently to reduce drift.
- Delete branches after merge.

## Commit Strategy

Prefer small, logical commits.

- One concern per commit.
- Keep generated artifacts out of commits unless intentionally versioned.
- Use imperative commit messages.

Recommended commit style:

- `feat(api): add organization create endpoint`
- `fix(docker): correct pgadmin preload mount`
- `docs(repo): add release process`
- `chore(ci): add typecheck step`

## Pull Request Strategy

- Open PRs early as draft when work is in progress.
- Keep PR scope narrow.
- Include a short change summary and test notes.
- Link related issue(s).

PR checklist:

- Behavior verified locally
- Docs updated when behavior/config changed
- New config keys added to `.env*.example`
- No secrets committed

## Release Strategy

Use semantic versioning (`MAJOR.MINOR.PATCH`).

- `PATCH`: bug fixes, no breaking API changes
- `MINOR`: backward-compatible features
- `MAJOR`: breaking changes

Suggested release flow:

1. Merge completed work into `main`.
2. Create release PR or branch if stabilization is needed.
3. Update changelog and version.
4. Tag release: `vX.Y.Z`.
5. Publish artifacts/deploy.

## Hotfix Strategy

For production incidents:

1. Branch from the production tag or release branch.
2. Implement minimal fix.
3. Open expedited PR with focused review.
4. Release as patch (`vX.Y.Z+1` equivalent patch bump).
5. Back-merge into `main`.

## Ownership and Code Review

- Require at least one reviewer before merge.
- Require passing CI for merge.
- Prefer CODEOWNERS for critical areas (`apps/api`, `infra`, `compose*`).

## Dependency and Security Hygiene

- Pin major versions for core runtime dependencies.
- Schedule periodic dependency updates.
- Run security scans in CI where possible.
- Rotate credentials and never commit real secrets.
