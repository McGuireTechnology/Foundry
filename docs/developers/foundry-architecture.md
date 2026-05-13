# Vortex Architecture and Milestones

## Concept Summary

Vortex is the operational data and application layer between business systems and analytics:

1. Connections ingest and sync data from source systems into Vortex Operational Data Stores (ODS).
2. Vortex Applications provide custom data entry and workflow capability where source systems are missing features.
3. Vortex unifies synced and app-entered records under one governed operational model.
4. Superset provides analytics and dashboards on top of curated Vortex datasets.

## Logical Architecture

- Source Systems: ERP, CRM, ticketing, spreadsheets, custom DBs
- Connection Layer: connector configs, sync schedules, incremental extraction, retries
- ODS Layer: normalized operational tables by domain (orders, customers, inventory, service)
- App Runtime Layer: metadata-driven internal apps for forms, workflows, and exception handling
- Governance Layer: tenancy, roles, audit logs, lineage, data quality rules
- Analytics Layer: Superset datasets, semantic metrics, dashboards, alerts

## Data Lifecycle

1. Extract: Connection pulls source data using full and incremental sync modes.
2. Land: Raw payloads are persisted for replay/debug and mapped into ODS staging.
3. Transform: Validation, normalization, dedupe, and conformance rules run into curated ODS tables.
4. Operate: Vortex Apps read/write curated ODS to support operational workflows.
5. Analyze: Superset reads curated views and metric tables for reporting and trend analysis.

## Monorepo Layout

- api: FastAPI service, auth, metadata APIs, connection orchestration, runtime endpoints
- web: Vue builder and app runtime shell
- docs: VitePress docs and onboarding
- packages/shared-types: shared domain contracts
- packages/sdk-js: client SDK for frontend and external integrations
- infra/docker: local container orchestration

## Backend Service Boundaries (FastAPI)

- Identity and tenancy: organizations, users, roles, permissions
- Metadata layer: apps, pages, components, fields, validation and actions
- Runtime layer: evaluates app metadata for request/response behavior
- Connection layer: connector registry, credentials, sync jobs, run history
- ODS layer: schema management, write pipelines, audit columns, soft deletes
- Job layer: async workflows and scheduled tasks via Redis-backed worker
- Analytics export layer: curated SQL views for Superset consumption

## Frontend Boundaries (Vue)

- Builder shell: navigation, project switcher, publish flow
- Connection studio: source setup, field mapping, sync status, run logs
- Schema editors: data model, page layout, component properties
- Logic builder: triggers, conditions, actions
- Runtime renderer: interprets published schema into user-facing apps
- Admin views: role management, audit trails, data quality exceptions

## Superset Integration Boundaries

- Dataset contracts: stable SQL views with versioned naming conventions
- Metric contracts: centrally defined KPI formulas with business owner metadata
- Freshness SLAs: per-domain sync windows exposed to dashboard consumers
- Row-level security: aligned with Vortex tenant and role boundaries

## Connection Instance Model

Vortex must support multiple connections of the same connector type (for example, multiple AD domains/forests).

- Connector type: reusable adapter implementation (for example, `active_directory`)
- Connection instance: tenant-owned configured source endpoint (for example, `corp-ad-prod`, `emea-ad`)
- Each instance has independent credentials, schedules, sync checkpoints, run history, and error streams
- All ingested records carry `connection_id` and `org_id` for strict data partitioning
- Identity uniqueness is scoped by `connection_id + source_object_id` rather than connector type alone

## First Connector: Active Directory

Active Directory (AD) is the first production connector and anchors the identity domain in ODS.

- Primary entities: users, groups, organizational units (OUs), group memberships
- Source protocol: LDAP/LDAPS bind with service account and scoped search base
- Sync modes: initial full sync plus incremental sync using `whenChanged` watermark
- Key identifiers: `objectGUID` (stable key), `sAMAccountName`, `userPrincipalName`, `distinguishedName`
- Security baseline: least-privileged bind account, encrypted credential storage, mandatory LDAPS in production

### AD ODS Canonical Tables (v1)

- `ods_identity_users`: one row per AD user object per connection instance
- `ods_identity_groups`: one row per AD group object per connection instance
- `ods_identity_group_memberships`: bridge table from group to member objectGUID per connection instance
- `ods_identity_ous`: OU hierarchy for org structure analysis
- `ods_identity_sync_runs`: connection run metadata (status, counts, duration, watermark)

### Connection Control Plane Tables (v1)

- `connector_types`: registry of available connector adapters (AD, NetSuite, Salesforce, etc.)
- `connector_connections`: tenant-defined connection instances linked to connector type
- `connector_sync_runs`: run history per connection instance
- `connector_sync_checkpoints`: per-entity incremental watermarks per connection instance
- `connector_sync_errors`: normalized error events per run/connection

### AD Data Quality and Governance Rules

- Preserve raw source payload for each changed object for audit and replay
- Enforce uniqueness on `connection_id + objectGUID` and prevent duplicate active records
- Mark deletes/disables with soft-delete columns (`is_deleted`, `deleted_at`) and status flags
- Capture source timestamps (`whenCreated`, `whenChanged`) and ingestion timestamps

### AD to Superset Starter Datasets

- `vw_identity_user_directory`: current active users with department/title/manager attributes
- `vw_identity_group_directory`: groups and ownership metadata
- `vw_identity_group_coverage`: group sizes and orphaned groups
- `vw_identity_joiner_mover_leaver`: recent joins, attribute moves, and disables by period

## Initial Delivery Milestones

1. Milestone 1: ODS foundation
- Define canonical domain model for first operational domains
- Implement connection config and manual sync execution
- Persist raw ingest plus curated ODS tables with audit fields

2. Milestone 2: App operations
- Deliver form-driven app runtime over curated ODS tables
- Add validation rules and required field policies
- Add change history for app-originated writes

3. Milestone 3: Analytics enablement
- Publish curated views for Superset
- Define core KPI metrics and ownership
- Deliver initial operations and exception dashboards

## v0.1 Acceptance Criteria

- User can configure one source connection and execute sync
- Synced data is available in curated ODS tables with run traceability
- User can create one app form bound to an ODS table and submit records
- App-entered and connector-synced records are queryable together
- Superset can read a published curated view for dashboarding
- Docs include a complete local setup and first-dashboard walkthrough
