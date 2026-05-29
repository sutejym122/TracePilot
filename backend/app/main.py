"""FastAPI application factory.

Wires together: CORS, the domain-error exception handlers (single place mapping
errors to status codes + a consistent JSON envelope), all resource routers, the
APScheduler lifespan, and a /health liveness probe.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.errors import DomainError
from app.routers import (
    auth,
    dashboard,
    incidents,
    metrics,
    releases,
    services,
    users,
)
from app.workers.scheduler import shutdown_scheduler, start_scheduler

logger = logging.getLogger("tracepilot")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    logger.info("Scheduler started (health-check interval=%ss)",
                settings.HEALTH_CHECK_INTERVAL_SECONDS)
    yield
    # Shutdown
    shutdown_scheduler()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="TracePilot API",
    version="0.1.0",
    description="Release intelligence and observability for small teams.",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Exception handlers: the single place mapping errors -> HTTP ---
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    detail = str(exc) if settings.DEBUG else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": detail}},
    )


# --- Liveness probe (unauthenticated) ---
@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


# --- Routers ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(metrics.router)
app.include_router(releases.router)
app.include_router(incidents.router)
app.include_router(dashboard.router)