"""
app/main.py

Purpose:
- FastAPI app entrypoint.
- Register routers and middleware.
"""

from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from app.api.routers.me_appointments import router as me_router



def create_app() -> FastAPI:
    app = FastAPI(title="Reserves API", version="0.1.0")

    app.include_router(auth_router)
    app.include_router(me_router)
    return app


app = create_app()
