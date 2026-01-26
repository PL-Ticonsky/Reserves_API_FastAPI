"""
app/main.py

Purpose:
- FastAPI app entrypoint.
- Register routers and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.me import router as me_router
from app.api.routers.barber_availability import router as barber_availability_router
from app.api.routers.availability_slots import router as availability_slots_router
from app.api.routers.me_appointments import (
    router as appointments_router,
    me_router as me_appointments_router,
)
from app.api.routers.barber_appointments import router as barber_appointments_router


def create_app() -> FastAPI:
    app = FastAPI(title="Reserves API", version="0.1.0")

    # CORS (frontend Next.js en :3000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router)
    app.include_router(me_router)
    app.include_router(barber_availability_router)
    app.include_router(availability_slots_router)
    app.include_router(me_appointments_router)
    app.include_router(appointments_router)
    app.include_router(barber_appointments_router)

    return app


app = create_app()
