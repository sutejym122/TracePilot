# TracePilot — Architecture

## Backend architecture

- **FastAPI** application exposing a JSON API under `/api`.
- **SQLAlchemy 2.0** ORM models in `app/models/` (`user, service, health, metric, release, incident`).
- **Alembic** migrations in `alembic/versions/` (one revision per table).
- **PostgreSQL** as the system of record; **Redis** is provisioned for caching/coordination.
- **APScheduler** runs in-process background tasks (`app/workers/`) — periodic health checks and metric generation — reusing the same domain functions the manual routes call. (No separate Celery worker in the MVP.)
- **Domain layer** (`app/domain/`) holds all business logic: `auth, crud, dashboard, health_checker, metrics_simulator, metric_management, release_management, readiness, incident_management`. Note "service" as a folder name is avoided — `service` always means the microservice entity, never a logic layer.
- **Routers** (`app/routers/`) are thin HTTP adapters: validate via Pydantic schema, delegate to domain, return ORM objects serialized by response models.
- **Auth/JWT**: `POST /api/auth/*` issues bcrypt-verified JWTs; protected routes use an `HTTPBearer` dependency that resolves the current user. Errors flow through custom `DomainError` subclasses to a centralized handler returning `{"error": {"code", "message"}}`.

Layering: **routers → domain → models**. Routers never touch the ORM directly beyond simple fetch-or-404 helpers; domain functions own writes and invariants.

## Frontend architecture

- **React 19 + TypeScript**, built with **Vite**, styled with **Tailwind CSS v3** (dark "observability-console" theme).
- **React Router 7** for routing; protected routes gated by an auth check.
- **TanStack React Query 5** for all server state (queries + mutations with cache invalidation). No Redux.
- **Typed `fetch` API client** (`lib/apiClient.ts`) — prepends the base URL, attaches `Authorization: Bearer <token>`, normalizes the error envelope, and broadcasts a global event on `401` so auth state resets.
- **Auth context** (`context/AuthContext.tsx`) holds `user`/`token`, boots by validating a stored token via `/users/me`, and exposes `login`/`register`/`logout`.
- Dependency direction: **pages → hooks → api → apiClient**.

## Current data ownership

`user_id`-scoped tenancy: **one user = one workspace.** Every `Service` carries `user_id`; releases, incidents, metrics, health checks, and incident updates inherit ownership through their parent service. Cross-user reads return `404`.

> The current MVP uses user-scoped tenancy. In a production SaaS version, user ownership would be replaced or supplemented by workspace/organization ownership.

## Future production data ownership
