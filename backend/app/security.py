"""Security primitives: password hashing and JWT creation/decoding.

Uses the `bcrypt` library directly (passlib is effectively unmaintained and
breaks against bcrypt 4.1+/5.x). Stateless auth — tokens carry the user id in
`sub` and an `exp` claim. No server-side session store, which is why Redis is
not needed for auth.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.errors import AuthError

# bcrypt only considers the first 72 bytes of a password and raises on longer
# input in 4.1+. Truncating here keeps hashing/verification consistent.
_BCRYPT_MAX_BYTES = 72


def _to_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_to_bytes(plain), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except ValueError:
        # Malformed stored hash, etc. Treat as a non-match rather than crash.
        return False


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str:
    """Return the subject (user id) or raise AuthError on any failure."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise AuthError("Invalid or expired token")
    subject = payload.get("sub")
    if subject is None:
        raise AuthError("Invalid token payload")
    return subject