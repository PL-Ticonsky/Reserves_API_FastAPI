"""
app/api/routers/me.py

Purpose:
- Minimal protected endpoint to verify JWT auth + deps.
- Returns the authenticated user identity.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/me", tags=["me"])


@router.get("")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
    }
