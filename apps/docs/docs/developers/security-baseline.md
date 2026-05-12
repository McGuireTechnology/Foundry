# Security Baseline

This baseline defines minimum security hygiene for ongoing development.

## Required

- No plaintext secrets in repository commits.
- Dependency updates reviewed on a regular cadence.
- Security scan signals reviewed before merge when available.
- Auth-sensitive changes receive focused review.

## Recommended

- Secret scanning in CI.
- Dependency vulnerability checks in CI.
- Periodic key and credential rotation.

## PR Guidance

- Call out security-relevant changes in the PR summary.
- Add follow-up backlog items for deferred security improvements.
