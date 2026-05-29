"""Pydantic request/response schemas.

Convention per entity: XCreate (POST input), XUpdate (PATCH, all optional),
XOut (response, from_attributes=True), and XDetailOut where nested children
are needed. Input schemas never include server-controlled fields (id,
timestamps, user_id) to prevent mass-assignment.
"""
