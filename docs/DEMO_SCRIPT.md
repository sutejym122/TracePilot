# TracePilot — Demo Script

The demo follows the product loop: **release → health → latency → incident → rollback readiness.** Story: a payments team prepares and monitors a production release, refund errors rise, and the team works an incident whose timeline ties the degradation back to the recent release.

> Note on correlation: The MVP currently correlates through shared **service and timing context**. Direct incident-to-release linking is planned as a future enhancement — phrase it that way in the demo; don't claim automatic association.

The fastest setup is the seed script:

```bash
docker compose exec api python scripts/seed_demo_data.py
```

Then log in as `demo@tracepilot.dev` / `password123`. The scripts below assume you either seeded the data or are creating it live.

---

## 3-minute version (the loop, fast)

1. **Dashboard (15s).** "This is the operational summary — services, health, releases, readiness, incidents, error rate. One user = one workspace in this MVP."
2. **Service (20s).** Open `payment-service`. "A prod service with a healthy charge endpoint at 145ms and a refund endpoint throwing 500s at 1200ms — that's our degradation signal."
3. **Release + readiness (40s).** Open release `1.0.0`. "It's marked released, and the rollback-readiness checklist is 100/ready — all five gates green. That matters in a moment."
4. **Incident timeline (60s).** Open the refund-errors incident. Walk the three updates: Sam notes the error spike after `1.0.0`, on-call moves it to _investigating_, Maya resolves it citing the confirmed rollback path. "Status changes come from the timeline itself — resolving auto-stamps the resolved time."
5. **Back to dashboard (20s).** "Everything we just did is reflected here. The point isn't any single panel — it's that release, health, latency, and incident response are one connected story."

## 7-minute version (build it live)

1. **Frame the wedge (30s).** "TracePilot answers 'is this release safe, and if it broke, which release broke it?' Its wedge is correlation, not collection — not a Datadog replacement."
2. **Create the service (60s).** New Service → `payment-service`, owner `payments-team`, env `prod`, repo + health URL.
3. **Record metrics (90s).** On the service, add the healthy charge metric (`/api/payments/charge`, 200, 145ms, 250 req, 3 err), then the failing refund metric (`/api/payments/refund`, 500, 1200ms, 80 req, 18 err). Optionally hit **Simulate metric** once. "No real agent here — these are recorded/simulated samples; ingestion is future work."
4. **Cut the release (60s).** New Release → `1.0.0`, prod, status `released`, notes "Initial production payment release."
5. **Readiness (60s).** Open the release. Toggle three checks → **60 / risky**. Toggle all five → **100 / ready**. "Score is count×20; this is the rollback-preparedness gate."
6. **File + work the incident (120s).** New Incident → "Elevated payment refund errors after release 1.0.0", severity high, status open, summary about refund 500s. Add three timeline updates (no-status → investigating → resolved) as Sam, Sam, Maya. Show the header status flip and `resolved_at` populate.
7. **Dashboard close (30s).** Show counts and recent activity updated. "One service, one loop, fully connected."

## Full walkthrough (deep tour)

Cover everything in the 7-minute version, plus:

- **Auth**: register a fresh account, show the protected-route redirect when logged out, and the Settings page (user id, session status, API base URL, the user-scoped-tenancy note).
- **Breadth**: add a second service (`auth-service`) with its own release `2.3.1` in `testing` to show the dashboard aggregating multiple services.
- **Health checks**: run a health check and show the classification + denormalized service status (note: against `example.com` the result depends on what the URL returns; explain the 2xx/3xx-4xx/5xx classification rule).
- **Negative paths**: try to set a checklist score directly (rejected), post an empty incident update (rejected), open another user's resource (404). "Ownership is enforced server-side."
- **Migration story**: "Today ownership is `user_id`. In production this becomes `organization_id` + memberships + roles — the model is built to make that a contained change."
- **Honesty close**: walk `FUTURE_WORK.md` briefly — explicit `incident.release_id`, real ingestion, integrations. "The MVP favors breadth of integration over depth in any one silo, on purpose."
