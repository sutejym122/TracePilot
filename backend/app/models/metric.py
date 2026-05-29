"""ApiMetric model — per-endpoint latency/error windows (simulated in MVP).

Phase 2 schema:
    id             uuid pk
    service_id     uuid fk -> services
    endpoint       text          -- "GET /users"
    avg_latency_ms numeric
    p95_latency_ms numeric
    error_rate     numeric       -- 0..1
    window_start   timestamptz
    window_end     timestamptz

TODO(phase3): implement ApiMetric.
"""
