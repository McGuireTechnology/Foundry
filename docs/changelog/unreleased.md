# Changelog: Unreleased

## Added

- Documentation page for the project changelog.
- Users guide coverage for Applications and Databases features.
- API CRUD endpoints for Applications and Databases.
- EAV-style modeling endpoints using platform terms: Tables, Columns, Records, and Values.
- Convenience relationship endpoints:
  - `GET /databases/{id}/tables`
  - `GET /tables/{id}/columns`
  - `GET /tables/{id}/records`
  - `GET /columns/{id}/values`
  - `GET /records/{id}/values`
- Dashboard management UI sections for Applications and Databases.

## Changed

- Auth UX: sign-out page now uses a single explicit confirmation message in-page and removes redundant banner duplication.
- API CORS configuration expanded for local development to accept both `localhost` and `127.0.0.1` origins across ports via explicit origins plus regex.
- Auth frontend behavior clarified around explicit session messaging and sign-in redirection paths.
- API auth dependency moved to `OAuth2PasswordBearer` token extraction for protected endpoints.
- Databases model simplified to internal metadata (`name`, `slug`) and no longer stores external connection fields.
- Databases no longer maintain a foreign key link to applications.

## Documentation

- Authentication guide updated with current sign-out confirmation behavior and local dev CORS notes.
- Backlog and release-tracking docs synchronized with current auth feature branch progress.
- Added user documentation for Applications and Databases, including endpoint references and workflows.
