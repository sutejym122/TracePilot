"""Health checking — shared by the scheduler and the manual-trigger route.

TODO(phase4): async check_service(service, db):
  - httpx GET service.health_url with timeout
  - measure response_time_ms, capture status_code, classify is_up (2xx)
  - insert a HealthCheck row
  - update the denormalized service.status (healthy / degraded / down)
    using named threshold constants defined here
There must be exactly one definition of "what checking health means".
"""
