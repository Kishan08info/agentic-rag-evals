# Nimbus Analytics — Changelog

## v2.4 — March 2026

- **Cohort CSV export:** Retention cohort tables can now be exported to CSV
  directly from the dashboard.
- Improved funnel load times: p95 query latency dropped from 4.2s to 1.8s.
- Fixed a bug where deleted events still appeared in cached funnel results.

## v2.3 — January 2026

- **SAML SSO** is now generally available on Scale plans and above, with Okta
  and Google Workspace integrations.
- Added `DELETE /users/{id}` API endpoint for GDPR erasure requests.

## v2.2 — November 2025

- **Warehouse sync:** Nightly raw-event export to Snowflake, BigQuery, and
  Postgres (Scale plans and above).
- Dashboard folders for organizing shared reports.

## v2.1 — September 2025

- Real-time event stream view in the dashboard (sub-60-second freshness).
- New Kotlin SDK with offline event queuing.
