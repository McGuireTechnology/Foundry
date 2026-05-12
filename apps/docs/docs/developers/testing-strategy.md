# Testing Strategy

Use a lightweight test pyramid for a serious small project.

## Minimum Expectations by Change Type

- App behavior change: unit tests for changed logic.
- API contract/auth/CORS change: integration tests required.
- UI flow change: component tests preferred; end-to-end coverage when risk is high.
- Docs-only change: docs build/link checks.

## Pull Request Test Notes

PR descriptions should include:

- Commands run
- Scope of verification
- Known gaps (if any)

## Test Stability Guidelines

- Keep tests deterministic.
- Avoid network dependencies in unit tests.
- Prefer explicit fixtures over hidden shared state.
