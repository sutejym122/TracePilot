"""Reusable FastAPI dependencies.

`get_current_user` is the gate every protected route declares. It reads the
bearer token from the `Authorization: Bearer <token>` header, decodes it, loads
the user, and returns the ORM object whose `.id` scopes all downstream queries.

Uses HTTPBearer so the Swagger "Authorize" dialog is a single paste-your-token
box (the login route takes JSON, not OAuth2 form data). auto_error=False lets us
raise our own AuthError (401) for a missing/blank header instead of HTTPBearer's
default 403.
"""
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import AuthError
from app.models.user import User
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current user from the bearer token, or raise 401."""
    if credentials is None or not credentials.credentials:
        raise AuthError("Not authenticated")

    subject = decode_access_token(credentials.credentials)
    try:
        user_id = uuid.UUID(subject)
    except (ValueError, TypeError):
        raise AuthError("Invalid token subject")

    user = db.get(User, user_id)
    if user is None:
        raise AuthError("Could not validate credentials")
    return user