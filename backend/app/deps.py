"""Reusable FastAPI dependencies.

`get_current_user` is the gate every protected route declares. It decodes the
bearer token, loads the user, and returns the ORM object whose `.id` scopes all
downstream queries. tokenUrl points at the login route for the Swagger UI.
"""
import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import AuthError
from app.models.user import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current user from the bearer token, or raise 401."""
    subject = decode_access_token(token)
    try:
        user_id = uuid.UUID(subject)
    except (ValueError, TypeError):
        raise AuthError("Invalid token subject")

    user = db.get(User, user_id)
    if user is None:
        raise AuthError("Could not validate credentials")
    return user