# TracePilot — Production Readiness Checklist

> **TracePilot is a portfolio MVP. This checklist describes what would be required before treating it as production software.** Nothing here is a claim that the MVP currently meets these bars — it intentionally does not.

The MVP favors breadth of integration over depth in any single observability silo, and uses user-scoped tenancy (one user = one workspace). The items below are the gap between that and a real multi-tenant SaaS.

## Security

- [ ] Enforce HTTPS everywhere; HSTS at the edge.
- [ ] Strong, rotated `SECRET_KEY` stored as a managed secret.
- [ ] Input validation and output encoding reviewed across all endpoints.
- [ ] Dependency scanning (e.g. `pip-audit`, `npm audit`) in CI.
- [ ] Security headers (CSP, X-Frame-Options, etc.) on the frontend.

## Auth / session hardening

- [ ] Refresh tokens + short-lived access tokens (currently a single 24h access token).
- [ ] Token revocation / logout-everywhere.
- [ ] Password policy, rate-limited login, and account lockout/backoff.
- [ ] Consider httpOnly cookie storage instead of localStorage to reduce XSS token theft.
- [ ] Email verification and password reset flows.

## Multi-tenancy / workspaces

- [ ] Introduce `organization`/`workspace` as the tenant; migrate ownership `user_id → organization_id`.
- [ ] Memberships + roles (admin / engineer / viewer) enforced in the auth dependency.
- [ ] Invites and per-workspace data isolation tests.

## Database backups

- [ ] Automated, tested backups with point-in-time recovery.
- [ ] Documented restore runbook; periodic restore drills.
- [ ] Migration rollback strategy validated on a copy of prod.

## Observability

- [ ] Structured request logging with correlation IDs.
- [ ] Metrics on the API itself (latency, error rate, throughput).
- [ ] Tracing for slow endpoints.

## Error monitoring

- [ ] Error tracking (e.g. Sentry) on backend and frontend.
- [ ] Alerting on error-rate spikes and failed background jobs.

## Rate limiting

- [ ] Per-IP / per-user rate limits on auth and write endpoints.
- [ ] Abuse protection on registration.

## CORS / env hardening

- [ ] `CORS_ORIGINS` locked to known origins (no wildcards).
- [ ] `DEBUG=false`, `ENVIRONMENT=production`.
- [ ] `/docs` disabled or access-restricted.
- [ ] All secrets via a secrets manager, never in the repo or image.

## Real metric ingestion

- [ ] Replace manual/simulated metrics with a real ingestion path (SDK/agent or OpenTelemetry).
- [ ] Time-series storage for volume; retention policy.
- [ ] p95/p99 aggregation rather than per-sample rows.

## Background worker reliability

- [ ] Move from the in-process APScheduler to a durable worker (e.g. a dedicated worker process / queue) with retries and visibility.
- [ ] Idempotent jobs; dead-letter handling; metrics on job health.

## Deployment pipeline

- [ ] CI running tests + build on every PR.
- [ ] Automated migrations as a release step.
- [ ] Blue/green or rolling deploys; health-gated rollouts.
- [ ] Reproducible, pinned dependencies.

## Tests / e2e coverage

- [ ] Maintain backend unit/integration coverage (currently 107 tests).
- [ ] Add frontend component tests and end-to-end tests (e.g. Playwright) for the core loop.
- [ ] Contract tests between frontend types and backend schemas.

## Secrets management

- [ ] All secrets in a managed store (platform secrets, Vault, etc.).
- [ ] No secrets in `.env` committed; `.gitignore` enforced (it is).
- [ ] Rotation policy for `SECRET_KEY`, DB credentials, and any integration tokens.
