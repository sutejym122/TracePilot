"""Auth routes: register and login. The only group with public endpoints.

Thin layer: validate via schema, delegate to domain.auth, shape the response.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth import authenticate_user, register_user
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut
from app.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterOut(UserOut):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=RegisterOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    user = register_user(db, payload.email, payload.password, payload.name)
    token = create_access_token(str(user.id))
    return RegisterOut(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        access_token=token,
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    token = create_access_token(str(user.id))
    return TokenOut(access_token=token)