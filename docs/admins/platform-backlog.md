# Vortex Backlog

## Platform

- [ ] Add API and dashboard end-to-end tests for Applications and Databases CRUD flows.
- [ ] Add authorization policies for Tables, Columns, Records, and Values resources.
- [ ] Add pagination and filtering support to list-heavy dashboard views.
- [ ] Implement Active Directory connector configuration (LDAP/LDAPS host, bind DN, search base, attribute mapping).
- [ ] Build AD full sync pipeline for users, groups, OUs, and group memberships into ODS identity tables.
- [ ] Add incremental AD sync with `whenChanged` watermark and run checkpoint persistence.
- [ ] Add connector secret management for AD bind credentials with encryption at rest and masked logs.
- [ ] Add connection-instance data model (`connector_types`, `connector_connections`, `connector_sync_runs`, `connector_sync_checkpoints`, `connector_sync_errors`).
- [ ] Enforce multi-connection uniqueness and partitioning keys in ODS identity tables (`org_id`, `connection_id`, `source_object_id`).
- [ ] Add dashboard/API support to create and manage multiple Active Directory connections per tenant.
- [ ] Publish Superset-ready identity views (`vw_identity_user_directory`, `vw_identity_group_coverage`, `vw_identity_joiner_mover_leaver`).

## Apple Client

- [ ] Add automated tests for `AppSession`, `CredentialsStore`, and `VortexAPIClient` (unit coverage plus request/response stubs).
- [ ] Close remaining web parity polish gaps (including sign-in caps-lock warning and minor auth UX alignment).
- [ ] Replace temporary brand assets with production app assets (app icon, launch assets, and logo mark variants).
- [ ] Tighten App Transport Security for non-local environments (remove arbitrary loads and explicitly allow required domains).
