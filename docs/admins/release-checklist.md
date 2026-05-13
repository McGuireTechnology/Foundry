# Release Checklist

Use this checklist for each release tag `vYY.M.N`.

## Pre-Release

- `main` is green on required CI checks.
- Changelog is updated for shipped work.
- Backlog reflects deferred work and known follow-ups.
- Version number is selected using `YY.M.N` sequence rules.

## Release

1. Pull latest `main`.
2. Create and push tag: `vYY.M.N`.
3. Record release notes from changelog deltas.
4. Deploy/publish release artifacts.

## Post-Release

- Run smoke checks for critical paths.
- Record rollback plan reference for the release.
- Confirm any urgent follow-up items are in backlog.
