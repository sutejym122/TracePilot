"""Generic, user-scoped persistence helpers shared by routers.

TODO(phase3): get_or_404(db, model, id, user_id), list_for_user, create_for_user,
update, delete. The 'smart' logic lives in the other domain modules; this is
just safe, scoped CRUD so routers stay DRY.
"""
