# TracePilot — Future Work

TracePilot's MVP intentionally favors breadth of integration over depth in any single observability silo. The roadmap below is grouped by product layer and is honest about what does **not** exist yet.

## A. Team / workspace layer

The biggest gap between the MVP and a real product. Today: **one user = one workspace**, no collaboration.

- Workspaces / organizations as the top-level tenant.
- Team membership and invites.
- Roles: `admin`, `engineer`, `viewer`, with enforcement in the auth dependency.
- Workspace-level dashboard aggregating across members.
- Ownership migration: `user_id → organization_id/workspace_id`, with a `memberships` join table. _The current MVP uses user-scoped tenancy; in a production SaaS version, user ownership would be replaced or supplemented by workspace/organization ownership._

## B. Deeper release correlation

Make the release→incident link explicit rather than inferred.

- Add `incident.release_id` (nullable) with a real foreign key.
- Auto-suggest the likely release based on `service_id` + timestamp proximity.
- Release impact timeline: overlay incidents and metric regressions on the release window.
- Link health regressions and latency/error spikes to specific release windows.

## C. Real integrations

Replace manual entry and simulation with real sources.

- GitHub releases/commits (auto-create releases from tags).
- CI/CD providers (deploy events).
- Slack notifications for incidents and status changes.
- PagerDuty / Opsgenie for on-call escalation.
- OpenTelemetry ingestion for real traces/metrics.

## D. Metrics and reliability intelligence

- Real ingestion SDK/agent (the MVP only stores manual/simulated samples).
- p95/p99 latency charts and trends.
- Anomaly detection on latency/error rates.
- SLO/SLA definition and tracking.
- Richer metrics visualization.

## E. Operational maturity

- Audit log of who changed what.
- Comments / @mentions on incidents.
- Configurable health-check intervals, retries, and multi-region checks.
- SSO (SAML/OIDC).
- Production deployment (managed Postgres/Redis, CI/CD, observability of TracePilot itself).
- Billing, if productized.

---

None of the above is implied to exist today. The MVP deliberately stops at the connective tissue so the core wedge — correlation across release, health, latency, incidents, and rollback readiness — is demonstrable end to end by a single developer.
