# ARCHITECTURE — Booking / Appointment MVP (Single Provider)

This document describes the application architecture, module boundaries, and how business rules are enforced.

---

## Goals

- Clear separation of responsibilities (API, business rules, data access)
- Strong authorization and ownership checks (client vs provider)
- Correct enforcement of time-based rules (availability and no-overlap)
- Maintainable structure suitable for a backend portfolio project

---

## Architectural style

**Modular monolith + layered architecture**

Layers (top to bottom):
1. **API layer** (FastAPI routers): HTTP + validation + status codes
2. **Service layer**: business rules and orchestration
3. **Repository layer**: database queries and persistence logic
4. **DB/Models**: SQLAlchemy ORM models + Alembic migrations

Dependency direction:
`api → services → repositories → db/models`

Rules:
- Routers must not contain business rules.
- Repositories must not decide permissions or state transitions.
- Services enforce domain rules and call repositories.
- Overlap is checked in service layer and enforced at DB-level to prevent race conditions.
---

## Proposed folder structure

```txt
app/
  main.py
  api/
    deps.py
    routers/
      auth.py
      me_appointments.py
      availability_slots.py
      barber_appointments.py
      barber_availability.py
  core/
    config.py
    security.py
    errors.py
    logging.py
  db/
    session.py
    base.py
  models/
    user.py
    availability.py
    appointment.py
  schemas/
    auth.py
    user.py
    availability.py
    appointment.py
    common.py
  repositories/
    user_repo.py
    availability_repo.py
    appointment_repo.py
  services/
    auth_service.py
    availability_service.py
    appointment_service.py
  migrations/
    env.py
    versions/
tests/
