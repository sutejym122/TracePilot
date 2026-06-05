# TracePilot — Final Demo Checklist

Run through this right before showing TracePilot to a recruiter or interviewer.

## 1. Pull the latest code

```bash
git checkout main
git pull
```

## 2. Start the backend

```bash
docker compose up -d db redis
docker compose up -d api
# if migrations don't run automatically:
docker compose exec api alembic upgrade head
```

Confirm: `http://localhost:8000/health` responds, and `http://localhost:8000/docs` loads.

## 3. Seed the demo data

```bash
docker compose exec api python scripts/seed_demo_data.py
```

## 4. (Optional) Final verification

```bash
docker compose exec api pytest          # expect: 107 passed
cd frontend && npm run build            # expect: clean build
```

## 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (usually `http://localhost:5173`). Confirm `frontend/.env` has `VITE_API_BASE_URL=http://localhost:8000`.

## 6. Log in as the demo user

- `demo@tracepilot.dev` / `password123`

## 7. Verify each screen (the demo loop)

- [ ] **Dashboard** (`/`) — summary cards populated, recent-activity feed shows entries.
- [ ] **Service metrics** — open `payment-service`; the metrics table shows the healthy `POST /api/payments/charge` (200, 145ms) and the failing `POST /api/payments/refund` (500, 1200ms, elevated errors).
- [ ] **Release readiness** — open release `1.0.0`; readiness ring shows **100 / ready**, all five checks on.
- [ ] **Incident timeline** — open the "Elevated payment refund errors after release 1.0.0" incident; status is **resolved**, **resolved at** is populated, and the three timeline updates (Sam → Sam → Maya) are present.
- [ ] **Settings** (`/settings`) — the user-scoped-tenancy MVP note is visible.

## 8. Presentation hygiene

- [ ] Capture/update screenshots if missing — follow `docs/SCREENSHOTS.md`, save to `docs/img/`.
- [ ] Confirm README screenshots render on GitHub (push images, view the repo page).
- [ ] Confirm no private docs are committed:

```bash
git ls-files docs/RESUME_BULLETS.md docs/INTERVIEW_ANSWERS.md
# should print nothing; if it prints, untrack with:
# git rm --cached docs/RESUME_BULLETS.md docs/INTERVIEW_ANSWERS.md
```

- [ ] Confirm no real `.env` is committed:

```bash
git ls-files | grep -E "(^|/)\.env$"   # should print nothing
```

## 9. Have the one-liner ready

> "TracePilot answers 'is this release safe, and if something broke, which release broke it?' Its wedge is correlation, not collection — it connects releases, health, latency, incidents, and rollback readiness into one loop. It's an honest MVP: user-scoped tenancy, with workspaces and real ingestion as documented future work."
