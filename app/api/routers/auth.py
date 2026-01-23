"""
app/api/routers/auth.py

Purpose:
- Expose authentication endpoints (register, login).
- Translate HTTP requests into service calls.
- Convert domain errors into proper HTTP responses.

Routes:
- POST /auth/register
- POST /auth/login
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse
from app.services.auth_service import (
    register_client,
    login,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """
    Register a new client user (public endpoint).
    """
    try:
        result = register_client(db, email=str(payload.email), password=payload.password)
        return RegisterResponse(**result.__dict__)
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL_ALREADY_EXISTS")


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Login (public endpoint) -> returns JWT access token.
    """
    try:
        result = login(db, email=str(payload.email), password=payload.password)
        return TokenResponse(access_token=result.access_token, token_type=result.token_type)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CREDENTIALS")
    except InactiveUserError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="USER_INACTIVE")
