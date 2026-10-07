# Nimbus Analytics — Product Overview

Nimbus Analytics is a fictional product-analytics platform that helps teams understand
how users behave inside web and mobile applications. It captures raw user events,
then turns them into funnels, retention cohorts, and real-time dashboards.

## Key features

- **Event tracking:** Capture custom events with a lightweight SDK available for
  JavaScript, iOS (Swift), and Android (Kotlin). Events are delivered to dashboards
  in under 60 seconds.
- **Funnels:** Build multi-step conversion funnels with breakdowns by device,
  geography, or any custom event property.
- **Retention cohorts:** Compare week-over-week retention for user cohorts grouped
  by signup date or first-touch campaign.
- **Dashboards:** Shareable, real-time dashboards with role-based access control.
- **Warehouse export:** Nightly sync of raw event data to your own data warehouse
  (Snowflake, BigQuery, or Postgres) on Scale plans and above.

## How it works

Install the SDK, call `nimbus.track("event_name", properties)` whenever something
meaningful happens, and the platform handles ingestion, identity resolution, and
aggregation. Identity resolution merges anonymous and logged-in activity into a
single user profile using a deterministic ID graph.

Nimbus is designed for product and growth teams at companies with 10 to 10,000
employees. It is not a marketing attribution tool and does not do ad-tech tracking.
