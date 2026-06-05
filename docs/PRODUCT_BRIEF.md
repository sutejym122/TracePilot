# TracePilot — Product Brief

## Product overview

TracePilot is a release intelligence and observability MVP for small engineering teams (roughly 2–15 engineers) that helps answer one question well: **"Is this release safe, and if something broke, which release broke it?"** It connects services, releases, health checks, API latency/error metrics, rollback-readiness checklists, and incidents into a single operational loop.

## Product wedge

**The product's wedge is correlation, not collection.** TracePilot does not try to out-instrument Datadog, replace PagerDuty, or act as a feature-flag platform. It assumes a team already has a handful of services and a steady release cadence, and gives them the connective tissue to reason about _change and consequence_ together.

> The MVP demonstrates the connective tissue between release tracking, health checks, latency/error metrics, incident timelines, and rollback readiness.

## Why correlation matters

For a small team, the expensive moment is not collecting one more metric — it's the post-deploy scramble: flipping between a logs tool, a release spreadsheet, and Slack to reconstruct what changed. The signals usually already exist in isolation. The leverage is in putting _release_, _health_, _latency/errors_, _rollback readiness_, and _incident response_ in one place, scoped to a service, so the path from "something is degraded" to "here is the likely release and whether we were ready to roll back" is short.

## Core personas

**Maya — Backend/Platform Engineer (primary).** Owns 3–4 services, cuts releases weekly. Wants confidence that systems are green before and after deploys. Uses service health, latency metrics, the release tracker, and the dashboard.

**Devraj — Engineering Lead (secondary).** Cares about release-process quality and accountability. Wants rollback readiness visible and an incident history to learn from. Uses readiness checklists and dashboard summaries.

**Sam — On-call Engineer (situational).** Shows up during an incident and must answer "what changed?" quickly. Uses the incident timeline alongside release and health context.

## MVP scope

Auth · Service Registry · Health Check Monitor · API Latency/Error Metrics · Release Tracker · Rollback Readiness Checklist · Incident Timeline · Dashboard Summary.

Each is intentionally shallow. The readiness checklist is five booleans, not a configurable policy engine. Health checks are on-demand, not a scheduling system. Metrics are samples, not a time-series database. That shallowness is the point: it keeps the surface small enough for one developer to build well while still demonstrating the whole loop.

## Non-MVP features intentionally avoided

- Real metrics ingestion SDK/agent / OpenTelemetry pipeline
- Alerting and notifications
- Multi-tenancy: teams, workspaces, roles, RBAC, invites
- Anomaly detection / ML
- Auto-rollback or deploy execution
- Deep historical analytics, p95/p99 charting
- Audit logs, SSO, billing
- Configurable check intervals/retries/regions

These are not oversights; they are scoped out so the demo stays focused on integration breadth.

## Why the project is scoped this way for one developer

A solo developer cannot credibly build a production observability suite, and trying to would produce five half-built silos. Building the _loop_ — even shallowly — is both achievable and more impressive: it shows product judgment (knowing the wedge), system design (clean layering, a real data model, a migration path to multi-tenancy), and the discipline to say no. _The MVP intentionally favors breadth of integration over depth in any single observability silo._

## What should feel impressive in a demo

Not a single chart — the **loop**. Cutting a release, watching refund errors climb, filing an incident, and walking a timeline that ties the degradation back to the recent release and the rollback-readiness state, then seeing the dashboard reflect the whole thing. The impressive part is that these are not five disconnected screens; they are one connected operational story. _The current MVP correlates through shared service and timing context; direct incident-to-release linking is planned as a future enhancement._
