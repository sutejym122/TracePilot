"""Auth business logic: registration and authentication.

No HTTP awareness — takes a db session and primitives, raises DomainError
subclasses. Routers translate the result to responses.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AuthError, ConflictError
from app.models.user import User
from app.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str, name: str | None) -> User:
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ConflictError("A user with that email already exists")

    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    # Verify even when the user is missing is unnecessary here; a generic error
    # avoids revealing whether the email exists.
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password")
    return user