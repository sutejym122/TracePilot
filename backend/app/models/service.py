"""Service model — a registered microservice (the entity, not business logic).

Phase 2 schema:
    id               uuid pk
    user_id          uuid fk -> users (indexed, cascade)
    name             text not null
    owner            text
    environment      enum(dev, uat, prod)
    status           enum(healthy, degraded, down, unknown)  -- denormalized, written by health_checker
    repo_url         text
    health_url       text
    last_deployed_at timestamptz
    created_at / updated_at

TODO(phase3): implement Service + the Environment / ServiceStatus enums.
"""
