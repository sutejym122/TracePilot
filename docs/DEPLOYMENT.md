# TracePilot — Deployment

TracePilot is a portfolio MVP. These instructions cover running it locally for a demo and deploying it publicly so it can be linked from a portfolio. They do **not** claim production readiness — see [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for what real production would require.

---

## Option A — Local demo only

The fastest way to see the full product loop.

```bash
# 1. Backend dependencies (Postgres + Redis) and API
docker compose up -d db redis
docker compose up -d api

# 2. Apply migrations (if your compose doesn't run them automatically)
docker compose exec api alembic upgrade head

# 3. Seed the demo scenario
docker compose exec api python scripts/seed_demo_data.py

# 4. Frontend
cd frontend
npm install
npm run dev
```

- App: the URL Vite prints (usually `http://localhost:5173`, sometimes `5174`).
- API docs (Swagger): `http://localhost:8000/docs`
- Liveness probe: `http://localhost:8000/health`
- Log in with `demo@tracepilot.dev` / `password123`.

Frontend env (`frontend/.env`):
