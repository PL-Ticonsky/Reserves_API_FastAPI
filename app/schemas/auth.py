"""

Purpose:
- Pydantic schemas for authentication endpoints.
- Define request/response shapes for /auth/register and /auth/login.

Why schemas exist:
- They validate user input (types, constraints).
- They control what fields are exposed in API responses.
- They decouple API contract from database models.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


# ---------------------------
# Register
# ---------------------------

class RegisterRequest(BaseModel):
    """
    Body for POST /auth/register

    Notes:
    - Email is validated using EmailStr.
    - Password constraints here are basic; we enforce stronger rules in services if needed.
    """
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterResponse(BaseModel):
    """
    Response for POST /auth/register
    """
    id: str
    email: EmailStr
    role: str


# ---------------------------
# Login
# ---------------------------

class LoginRequest(BaseModel):
    """
    Body for POST /auth/login
    """
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """
    Response for POST /auth/login
    """
    access_token: str
    token_type: str = "bearer"
