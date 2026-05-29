"""Incident + IncidentUpdate models.

Phase 2 schema:
  incidents:
    id          uuid pk
    user_id     uuid fk -> users
    service_id  uuid fk -> services (indexed)
    release_id  uuid fk -> releases (NULLABLE, indexed)  -- the correlation edge
    title       text not null
    severity    enum(sev1, sev2, sev3, sev4)
    status      enum(open, investigating, identified, resolved)
    root_cause  text
    resolution  text
    started_at  timestamptz
    resolved_at timestamptz (nullable)
    created_at / updated_at

  incident_updates (the timeline):
    id          uuid pk
    incident_id uuid fk -> incidents (indexed)
    note        text not null
    created_at  timestamptz (indexed)

TODO(phase3): implement Incident, IncidentUpdate + enums.
"""
