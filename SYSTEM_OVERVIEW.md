# SYSTEM_OVERVIEW — Booking / Appointment MVP

## Purpose
Build a backend-first web API to manage appointments for a hair salon, enforcing real-world booking rules (availability, permissions, and non-overlapping appointments).

## In scope
### Authentication & Users
- Email + password registration and login (JWT)
- Multi-user system
- Role-based access:
  - Provider: manages availability and appointment decisions
  - Client: books and manages own appointments

### Provider features
- Create and manage weekly availability blocks (e.g., Mon 09:00–18:00)
- View own appointment calendar (filters by date range and status)
- Confirm or cancel appointments

### Client features
- Book an appointment with a provider within available hours
- Cancel an appointment
- Reschedule an appointment (subject to rules)
- View own appointment history

### Business rules (backend-enforced)
- Appointments cannot overlap for the same provider
- Appointments must be fully inside provider availability
- Status workflow: pending -> confirmed, pending/confirmed -> canceled
- Clients cannot modify other clients’ appointments
- Providers cannot book appointments as clients

### Persistence
- Store all data in PostgreSQL
- Manage schema via Alembic migrations

## Out of scope (strict)
- Payments
- Notifications (email/SMS)
- Calendar integrations (Google Calendar, etc.)
- Admin dashboards and admin roles
- Social login (Google/Gmail)
- Offline support
- Native mobile apps
- Collaboration features (sharing calendars, teams, etc.)

## System characteristics
- API-first (minimal or no frontend)
- Production-minded error handling and validation
- Deterministic, reproducible setup (env-based config, optional Docker)

## Assumptions (to keep MVP simple)
- Appointments must start and end on the same local day (provider timezone)
- All stored datetimes are `timestamptz` (UTC in DB, converted for validation)
- Provider availability is weekly recurring (no vacations/holidays in MVP)
- No double-booking across providers is needed (only per-provider overlap)
- Appointment durations are provided by 30 minutes
- Only one admin
