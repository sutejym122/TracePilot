# TracePilot — Backend

Release intelligence and observability API. FastAPI + PostgreSQL + SQLAlchemy +
Alembic, JWT auth, APScheduler for periodic health checks, Redis for cache/jobs.

## Status

Skeleton scaffold. The app boots, `/docs` renders all route groups, `/health`
responds, Alembic is wired, and the readiness scorer is implemented and tested.
Models, schemas, routes, and domain logic are documented stubs filled in from
Phase 3 onward — look for `TODO(phaseN)` markers.

## Layout

```
app/
  main.py        app factory: CORS, error handlers, routers, scheduler lifespan
  config.py      typed settings from env
  database.py    engine, SessionLocal, Base, get_db
  deps.py        get_current_user dependency
  security.py    password hashing + JWT
  errors.py      domain exceptions -> HTTP envelope
  models/        SQLAlchemy ORM (DB shape only)
  schemas/       Pydantic I/O contracts
  routers/       thin HTTP layer, one file per resource
  domain/        business logic (health_checker, readiness, dashboard, ...)
  workers/       APScheduler + scheduled tasks
  seed.py        idempotent demo-data loader
alembic/         migrations
tests/           smoke + unit tests
```

## Local setup (Docker)

```bash
cp backend/.env.example backend/.env      # then edit SECRET_KEY
docker compose up -d db redis
docker compose up api
docker compose exec api alembic upgrade head
docker compose exec api python -m app.seed
# http://localhost:8000/docs
```

## Local setup (bare metal)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# point DATABASE_URL at a reachable Postgres
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

## Migrations

```bash
alembic revision --autogenerate -m "describe change"   # generate from model changes
# review the generated file in alembic/versions/, then:
alembic upgrade head
```

## Tests

```bash
pytest
```
