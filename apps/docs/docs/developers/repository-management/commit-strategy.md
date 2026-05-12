# Commit Strategy

Prefer small, logical commits.

- One concern per commit.
- Keep generated artifacts out of commits unless intentionally versioned.
- Use imperative commit messages.

## Recommended Commit Style

- `feat(api): add organization create endpoint`
- `fix(docker): correct pgadmin preload mount`
- `docs(repo): add release process`
- `chore(ci): add typecheck step`

## Imperative Commit Message Guidance

- Write the subject as a command (what this commit does now), not a description of what it did.
- Good: `add auth token refresh guard`
- Good: `update release checklist for AI review`
- Avoid: `added auth token refresh guard`
- Avoid: `adds auth token refresh guard`
- Keep the subject concise and specific.
