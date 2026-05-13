# Environment Baseline

This page defines the minimum local toolchain for consistent development.

## Runtime Baseline

- Node.js: `24.x`
- npm: latest LTS-compatible runtime
- Python: `3.12+` for API development and tests

## Setup Expectations

- Install required runtimes before first run.
- Use `.env.example` values as the starting point for local `.env`.
- Keep local tooling aligned with CI where possible.

## Bootstrap

Typical bootstrap sequence:

1. Install dependencies (`npm install --prefix web` and `npm install --prefix docs`).
2. Install API dependencies for Python environment.
3. Start local stack (`compose.yml` workflow or app-local dev commands).
4. Run baseline verification:
   - web lint/typecheck/tests
   - API tests
