# Nimbus Analytics — API Reference

Base URL for all requests: `https://api.nimbus.example.com/v1`

## Authentication

All API requests authenticate with a Bearer token. Generate an API key from
Settings → API Keys in the dashboard, then send it in the `Authorization` header:

```
Authorization: Bearer nb_live_xxxxxxxxxxxxxxxx
```

Never expose a live key in client-side code; use the publishable key
(`nb_pub_...`) for browser and mobile SDKs instead.

## Endpoints

- `POST /events` — Ingest a batch of up to 500 events per request. The body is a
  JSON array of `{ "event": "name", "user_id": "abc", "properties": {...} }`.
- `GET /events` — Query aggregated event counts with `from`, `to`, and `event`
  parameters. Results are paginated with a cursor.
- `GET /funnels/{id}` — Fetch a saved funnel report as JSON.
- `DELETE /users/{id}` — Erase all data for a user ID (GDPR erasure requests).

## Rate limits and pagination

- The API allows **600 requests per minute** per API key. Exceeding the limit
  returns HTTP 429 with a `Retry-After` header in seconds.
- List endpoints return at most 100 items per page and include a `next_cursor`
  field; pass it as `?cursor=` to fetch the next page.
- Timestamps must be ISO 8601 UTC, e.g. `2026-03-14T09:30:00Z`.
