# Changelog

All notable changes to Foundry are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Documentation page for the project changelog.

### Changed

- Auth UX: sign-out page now uses a single explicit confirmation message in-page and removes redundant banner duplication.
- API CORS configuration expanded for local development to accept both `localhost` and `127.0.0.1` origins across ports via explicit origins plus regex.
- Auth frontend behavior clarified around explicit session messaging and sign-in redirection paths.

### Documentation

- Authentication guide updated with current sign-out confirmation behavior and local dev CORS notes.
- Backlog and release-tracking docs synchronized with current auth feature branch progress.

## [0.1.0] - 2026-05-07

### Added

- Initial monorepo scaffold with `apps/api`, `apps/web`, `apps/docs`, and shared packages.
- Layered Docker Compose setup including Traefik and pgAdmin development components.
- VitePress documentation site structure with guide and reference sections.
- Repository management guidelines and authentication docs.
- GitHub Pages deployment workflow for docs with custom domain support.

### Changed

- CI workflows updated to Node 24 compatible GitHub Actions.
- CI adjusted to use `packageManager` pnpm version and remove fragile pnpm cache dependency.
- Docs site branding and theme styling updated.
- Web app branding mark and dark mode styling updated.

### Documentation

- Project README streamlined.

### Other

- MIT license file updated.

[unreleased]: https://github.com/McGuireTechnology/Foundry/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/McGuireTechnology/Foundry/releases/tag/v0.1.0
