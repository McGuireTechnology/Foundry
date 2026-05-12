# Architecture

Foundry uses a monorepo with three primary apps:

- FastAPI backend (`apps/api`)
- Vue builder/runtime frontend (`apps/web`)
- VitePress documentation (`apps/docs`)

Shared contracts live under `packages/`.

## Operational Guardrails

Architecture decisions should stay aligned with project operating policies:

- [Environment Baseline](/developers/environment-baseline) for runtime/tooling consistency.
- [Testing Strategy](/developers/testing-strategy) for required verification by change type.
- [Security Baseline](/developers/security-baseline) for minimum security controls.
- [Deprecation Policy](/developers/deprecation-policy) for compatibility and removals.


