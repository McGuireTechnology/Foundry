# Architecture

Vortex uses a monorepo with three primary apps:

- FastAPI backend (`api`)
- Vue builder/runtime frontend (`web`)
- VitePress documentation (`docs`)

Shared contracts live under `packages/`.

Detailed target-state architecture and milestones:

- [Vortex Architecture and Milestones](/developers/vortex-architecture)

## Operational Guardrails

Architecture decisions should stay aligned with project operating policies:

- [Environment Baseline](/developers/environment-baseline) for runtime/tooling consistency.
- [Testing Strategy](/developers/testing-strategy) for required verification by change type.
- [Security Baseline](/developers/security-baseline) for minimum security controls.
- [Deprecation Policy](/developers/deprecation-policy) for compatibility and removals.


