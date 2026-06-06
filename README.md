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

## Why it exists

Small teams ship frequently but operate with fragmented tooling. After a deploy, the questions are always the same: _Is the system still healthy? Did latency or error rates move? If something broke, which release is the likely culprit — and were we prepared to roll back?_

Answering usually means stitching together a logs tool, a release spreadsheet, and team memory. Full observability suites answer these questions, but they can be heavy and expensive for a small team.

TracePilot keeps each capability deliberately shallow but ties them tightly together. The value isn't in any single panel; it's in the connective tissue across the operational loop:

```text
release → health → latency/errors → incident → linked release → rollback readiness
```
