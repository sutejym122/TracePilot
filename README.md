# TracePilot

> TracePilot is a release intelligence and observability MVP for small engineering teams that helps answer: **"Is this release safe, and if something broke, which release broke it?"**

TracePilot connects the operational signals a small team already has — services, releases, health checks, API latency/error metrics, rollback-readiness checklists, and incidents — into a single loop so that when something degrades, the path back to the likely cause is short.

**TracePilot's wedge is correlation, not collection.** It does not try to out-instrument Datadog, replace PagerDuty, or be a feature-flag platform. It assumes a small team (roughly 2–15 engineers) that has outgrown "just check the logs" but cannot justify a full Datadog + PagerDuty + LaunchDarkly stack.

> The MVP intentionally favors breadth of integration over depth in any single observability silo.

---

## Overview

TracePilot is a full-stack portfolio MVP: a FastAPI + PostgreSQL backend and a React + TypeScript frontend, wired end to end. It models the operational loop:
