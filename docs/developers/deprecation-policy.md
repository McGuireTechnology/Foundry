# Deprecation Policy

Use this policy for API and behavior changes that can break clients.

## Policy

- Announce deprecations before removal.
- Provide an overlap period where old and new behavior can coexist when feasible.
- Document target removal version and date in changelog/backlog.

## Required Deprecation Notes

- What is deprecated
- What replaces it
- Migration steps for consumers
- Planned removal version (`YY.M.N`) and date

## Enforcement

- Breaking removals should not merge without documented migration guidance.
