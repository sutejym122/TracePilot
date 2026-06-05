# TracePilot — Screenshot Checklist

Capture these eight screenshots in order. First seed the demo data and log in:

```bash
docker compose exec api python scripts/seed_demo_data.py
# then log in at the frontend as demo@tracepilot.dev / password123
```

Save all images to `docs/img/` using the suggested filenames. Use a desktop-width browser window (~1280px) on the dark theme. The captions below double as the alt text used in the README.

---

## A. Dashboard

- **Route:** `/`
- **Demo data visible:** 3 services, health checks, 2 releases, 1 incident, metric samples, a non-zero error rate, and a recent-activity feed with several entries.
- **Crop/focus:** the full six-card summary grid, the breakdown cards (service status / release readiness / incidents), and the top of the recent-activity feed.
- **Filename:** `dashboard.png`
- **Caption:** _Operational summary across services, releases, health, metrics, and incidents — one view of the whole loop._

## B. Services

- **Route:** `/services`
- **Demo data visible:** `payment-service`, `auth-service`, `notifications-service` with their environments and status badges.
- **Crop/focus:** the full services table including the "New Service" action.
- **Filename:** `services.png`
- **Caption:** _The service registry — the root entity every release, health check, metric, and incident hangs off of._

## C. Service Detail (health + metrics)

- **Route:** `/services/:serviceId` (open `payment-service`)
- **Demo data visible:** the service info card, the health-checks section, and the API metrics table showing the healthy `POST /api/payments/charge` (200, 145ms) alongside the failing `POST /api/payments/refund` (500, 1200ms, elevated errors).
- **Crop/focus:** frame the metrics table so both the healthy charge row and the failing refund row are visible.
- **Filename:** `service-detail-metrics.png`
- **Caption:** _Per-service health and latency/error context — the failing refund endpoint stands out against the healthy charge endpoint._

## D. Releases

- **Route:** `/releases`
- **Demo data visible:** release `1.0.0` (payment-service, released) and `2.3.1` (auth-service, testing).
- **Crop/focus:** the full releases table with version, service name, environment, and status badges.
- **Filename:** `releases.png`
- **Caption:** _Release tracking across services, with lifecycle status at a glance._

## E. Release Detail (readiness)

- **Route:** `/releases/:releaseId` (open `1.0.0`)
- **Demo data visible:** the release info card and the readiness ring at **100 / ready** with all five checklist toggles on.
- **Crop/focus:** the readiness ring and the checklist side by side.
- **Filename:** `release-readiness.png`
- **Caption:** _Rollback readiness as a scored gate — five checks, 0–100, blocked / risky / ready._

## F. Incidents

- **Route:** `/incidents`
- **Demo data visible:** the "Elevated payment refund errors after release 1.0.0" incident with severity and status badges.
- **Crop/focus:** the incidents table including severity/status columns.
- **Filename:** `incidents.png`
- **Caption:** _Incident tracking with severity and status, scoped to the affected service._

## G. Incident Detail (timeline)

- **Route:** `/incidents/:incidentId` (open the refund-errors incident)
- **Demo data visible:** the incident info card showing **resolved** status with a populated **resolved at** timestamp, and the three-step timeline (Sam → Sam → Maya, ending resolved).
- **Crop/focus:** the timeline rail with all three updates and the resolved header.
- **Filename:** `incident-timeline.png`
- **Caption:** _The incident response timeline — status is driven by updates, and resolving auto-stamps the resolution time._

## H. Settings

- **Route:** `/settings`
- **Demo data visible:** profile (name, email, user id, created date), session status, API base URL, and the MVP-scope note about user-scoped tenancy.
- **Crop/focus:** include the "MVP scope" card so the honest-scope note is legible.
- **Filename:** `settings.png`
- **Caption:** _Honest MVP scope: user-scoped tenancy today, with workspace/team collaboration noted as future work._

---

### Folder layout

```
docs/
  img/
    dashboard.png
    services.png
    service-detail-metrics.png
    releases.png
    release-readiness.png
    incidents.png
    incident-timeline.png
    settings.png
```
