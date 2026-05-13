# Release Strategy

Use calendar-based versioning: `YY.M.N`.

See also: [Release Checklist](/admins/release-checklist) and [Deprecation Policy](/developers/deprecation-policy).

## Version Format

- `YY`: two-digit release year
- `M`: release month (1-12)
- `N`: release sequence number within that month (starts at `1`)

Examples:

- `26.5.1` = first release in May 2026
- `26.5.2` = second release in May 2026
- `26.6.1` = first release in June 2026

Tag format:

- `vYY.M.N` (example: `v26.5.1`)

Display format:

- `Version YY.M.N` (example: `Version 26.5.1`)

## Migration Ordering

- Do not rely on app version numbers to order database migrations.
- Use migration-native ordering (for example, Alembic revision chains/timestamps) so out-of-order release branches do not break migration sequence.

## Suggested Release Flow

1. Merge completed work into `main`.
2. Create release PR or branch if stabilization is needed.
3. Update changelog and version.
4. Tag release: `vYY.M.N`.
5. Publish artifacts/deploy.


