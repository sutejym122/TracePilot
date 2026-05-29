"""Background workers. APScheduler runs in-process (Phase 2 decision); the task
boundary is kept clean so a future swap to Celery is localized."""
