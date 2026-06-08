# TracePilot

> A release intelligence and observability MVP for small engineering teams that answers one question well: **"Is this release safe, and if something broke, which release broke it?"**

TracePilot connects the operational signals a small team already has — services, releases, health checks, API latency/error metrics, rollback-readiness checklists, and incidents — into a single loop, so that when something degrades, the path back to the likely cause is short.

Its wedge is **correlation, not collection.** TracePilot doesn't try to out-instrument Datadog, replace PagerDuty, or act as a feature-flag platform. It's built for a small team that has outgrown "just check the logs" but can't justify a full Datadog + PagerDuty + LaunchDarkly stack. The MVP deliberately favors breadth of integration over depth in any single observability silo.

## Live demo

**Try it:** https://trace-pilot-two.vercel.app
**API docs:** https://tracepilot-api.onrender.com/docs

Demo credentials:

- **Email:** `demo@tracepilot.dev`
- **Password:** `password123`

The demo uses a shared public account with seeded data. If the data looks different, it may have been changed by another visitor.

> The backend runs on a free hosting tier that sleeps when idle, so the first request after a quiet period may take a few seconds to wake up. Subsequent requests are fast.

---

## Demo walkthrough

> A release goes out, refund errors spike, and TracePilot links the incident back to the release that likely caused it.

**Watch the demo:** [TracePilot walkthrough](docs/demo/tracepilot-demo.mov)

The walkthrough shows the core loop:

```text
release → health → latency/errors → incident → linked release → rollback readiness
```

In the demo, a `payment-service` release goes live, the refund endpoint starts failing, an incident is opened, and TracePilot links that incident back to release `1.0.0`.

---

## Why it exists

Small teams ship frequently but operate with fragmented tooling. After a deploy, the questions are always the same: _Is the system still healthy? Did latency or error rates move? If something broke, which release is the likely culprit — and were we prepared to roll back?_

Answering usually means stitching together a logs tool, a release spreadsheet, and team memory. Full observability suites answer these questions, but they can be heavy and expensive for a small team.

TracePilot keeps each capability deliberately shallow but ties them tightly together. The value isn't in any single panel; it's in the connective tissue across the operational loop:

```text
release → health → latency/errors → incident → linked release → rollback readiness
```

When refund errors spike after a release, an engineer can see the degraded metric, the recent release, whether a rollback plan was marked ready, and the incident timeline — in one place, scoped to one service, with the incident explicitly linked to the release that likely caused it.

---

## Who it's for

- **Maya — Backend/Platform Engineer:** owns a handful of services and cuts releases weekly. Wants confidence that systems are green before and after deploys.
- **Devraj — Engineering Lead:** cares about release-process quality. Wants rollback readiness visible and an incident history to learn from.
- **Sam — On-call Engineer:** during an incident, needs to answer "what changed?" quickly using the timeline plus release and health context.

---

## What the demo shows

The seeded scenario walks the full loop end to end:

- A `payment-service` in production with a healthy charge endpoint and a failing refund endpoint throwing elevated 500s.
- A release `1.0.0` with a rollback-readiness checklist scored **100 / ready**.
- An incident — _"Elevated payment refund errors after release 1.0.0"_ — with a three-step response timeline that resolves, explicitly linked to release `1.0.0`.
- A dashboard that aggregates services, releases, readiness, incidents, and error rate into one operational summary.

---

## Features

- **Authentication** — email/password registration and login with JWT bearer tokens.
- **Service registry** — the root entity for releases, health checks, metrics, and incidents.
- **Health checks** — checks that classify a service as healthy, degraded, or down.
- **API latency/error metrics** — endpoint-level samples with request volume, latency, and error-rate summaries.
- **Release tracker** — versions, environments, owners, and lifecycle status across services.
- **Rollback-readiness checklist** — a five-item gate scored 0–100 as blocked, risky, or ready.
- **Incident timeline** — incidents with chronological updates that drive status; resolving an incident auto-stamps the resolution time.
- **Incident-to-release correlation** — incidents can be explicitly linked to the release that likely caused them. The "Likely release" picker defaults to a service's most recent release, the incident view shows the linked release, and the release view lists related incidents.
- **Dashboard** — an aggregated operational summary with recent activity.

---

## Tech stack

**Backend:** FastAPI · PostgreSQL · SQLAlchemy 2.0 · Alembic · JWT auth · bcrypt · APScheduler · Pytest

**Frontend:** React · TypeScript · Vite · Tailwind CSS · TanStack React Query · React Router · typed fetch API client

**Infrastructure:** Vercel · Render · Neon Postgres · Docker Compose

---

## Screenshots

### Dashboard

![Dashboard — operational summary across services, releases, health, metrics, and incidents](docs/img/dashboard.png)

The dashboard summarizes services, health checks, releases, incidents, metrics, and error rate in one operational view.

### Services

![Services — service registry](docs/img/services.png)

The service registry is the root entity for releases, health checks, metrics, and incidents.

### Service detail

![Service detail — health and metrics](docs/img/service-detail-metrics.png)

The service detail page shows health context plus endpoint-level latency and error metrics, including the healthy charge endpoint and failing refund endpoint.

### Releases

![Releases — version and lifecycle tracking](docs/img/releases.png)

Releases are tracked by service, version, environment, owner, and lifecycle status.

### Release readiness

![Release readiness — rollback checklist](docs/img/release-readiness.png)

Each release has a five-item rollback-readiness checklist scored from 0 to 100.

### Incidents

![Incidents — severity and status tracking](docs/img/incidents.png)

Incidents are scoped to affected services and tracked by severity and status.

### Incident timeline

![Incident timeline — updates and linked release](docs/img/incident-timeline.png)

The incident timeline captures investigation updates, status changes, resolution time, and the linked release.

### Settings

![Settings — MVP scope](docs/img/settings.png)

The settings page communicates the current MVP scope: user-scoped tenancy today, with team collaboration as future work.

---

## API overview

The API is served under `/api` and documented interactively at the Swagger UI:

https://tracepilot-api.onrender.com/docs

Every resource is scoped to the authenticated user. Requesting another user's resource returns `404`.

| Group     | Endpoints                                                                                               |
| --------- | ------------------------------------------------------------------------------------------------------- |
| Auth      | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/users/me`                                  |
| Services  | `GET/POST /api/services`, `GET/PATCH/DELETE /api/services/{id}`                                         |
| Health    | `POST /api/services/{id}/health/check`, `GET /api/services/{id}/health`                                 |
| Metrics   | `GET/POST /api/services/{id}/metrics`, `POST /api/services/{id}/metrics/simulate`                       |
| Releases  | `GET/POST /api/releases`, `GET/PATCH/DELETE /api/releases/{id}`, checklist endpoints                    |
| Incidents | `GET/POST /api/incidents`, `GET/PATCH/DELETE /api/incidents/{id}`, timeline updates, suggested releases |
| Dashboard | `GET /api/dashboard/summary`                                                                            |

A fuller reference, including example payloads, lives in [docs/API_OVERVIEW.md](docs/API_OVERVIEW.md).

---

## Local development

### Backend

Start PostgreSQL, Redis, and the API with Docker Compose:

```bash
docker compose up -d db redis
docker compose up -d api
```

Run migrations:

```bash
docker compose exec api alembic upgrade head
```

Seed demo data:

```bash
docker compose exec api python scripts/seed_demo_data.py
```

The local API is available at:

```text
http://localhost:8000
```

Swagger is available at:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The local frontend runs at:

```text
http://localhost:5173
```

The frontend reads its backend URL from `VITE_API_BASE_URL`.

More detail on configuration and deployment is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Testing

Run backend tests:

```bash
docker compose exec api pytest
```

The backend suite covers authentication, user-scoped access, services, health checks, metrics, releases, readiness scoring, incidents, timeline automation, dashboard summary, and incident-to-release correlation.

Current backend test count:

```text
117 passed
```

Build the frontend:

```bash
cd frontend
npm run build
```

---

## MVP scope and limitations

TracePilot is an honest portfolio MVP, not production software. Its scope is intentional:

- **User-scoped tenancy:** one user acts as one workspace.
- **No teams or RBAC yet:** organizations, memberships, roles, and invites are future work.
- **No real metrics ingestion yet:** metrics are manually recorded, seeded, or simulated.
- **No alerting or escalation:** TracePilot tracks incidents but does not page anyone.
- **No auto-rollback:** release readiness is advisory; infrastructure changes are not triggered automatically.
- **No anomaly detection:** the MVP focuses on visible correlation rather than ML-driven analysis.
- **No enterprise plumbing:** SSO, audit logs, billing, and compliance features are outside v1 scope.

What production-readiness would require is documented in [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md).

---

## Future work

- **Team/workspace layer** — organizations, memberships, invites, and roles such as admin, engineer, and viewer.
- **Deeper release correlation** — automatic likely-release suggestions based on service and timestamp proximity.
- **Release impact timeline** — overlay releases, incidents, health regressions, and metric spikes in one view.
- **Real integrations** — GitHub releases, CI/CD providers, Slack, PagerDuty/Opsgenie, and OpenTelemetry ingestion.
- **Metrics intelligence** — real ingestion, p95/p99 charts, anomaly detection, and SLO/SLA tracking.
- **Operational maturity** — alerting, audit logs, SSO, and configurable health checks.

The full roadmap is in [docs/FUTURE_WORK.md](docs/FUTURE_WORK.md).

---

## Author

Built by **Sutej Yadavanahalli Manjunath** as a full-stack portfolio project to demonstrate end-to-end product thinking, backend architecture, tested API design, typed React data flows, deployment, and deliberate MVP scoping.
