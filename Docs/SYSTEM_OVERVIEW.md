# SYSTEM OVERVIEW — Booking & Appointment MVP

## 1. Purpose

This project implements a **backend-driven booking system** for a barber shop, designed to enforce real-world appointment rules such as availability constraints, role-based permissions, and non-overlapping bookings.

The system prioritizes:
- Correctness over convenience
- Explicit business rule enforcement
- Clear separation of responsibilities between backend and frontend

The backend is the **single source of truth**.  
The frontend is a **pure consumer of the API**.

---

## 2. Scope

### 2.1 Authentication & Users

- Email + password authentication using JWT
- Multi-user system with strict role separation
- Supported roles:
  - **Provider** — manages availability and appointment decisions
  - **Client** — books and manages their own appointments only

Authentication is stateless and enforced at the API boundary.

---

### 2.2 Provider Capabilities (Single Provider MVP)

- Define weekly recurring availability blocks (e.g. Monday 09:00–18:00)
- View all appointments with optional filters:
  - Date range
  - Status (pending / confirmed / canceled)
- Confirm pending appointments
- Cancel appointments at any stage (optional cancellation reason)

> The MVP intentionally models a **single provider** to reduce coordination complexity and focus on correctness.

---

### 2.3 Client Capabilities

- Register and authenticate
- View personal appointment history
- Request new appointments within available time slots
- Cancel appointments (only while pending)
- Reschedule appointments (only while pending)

Clients can **never** access or affect appointments belonging to other users.

---

## 3. Business Rules (Backend-Enforced)

All business rules are enforced at the **service layer** of the backend.

### Core Rules

- Appointments cannot overlap for the same provider
- Appointments must be fully contained within provider availability
- `start_at` must precede `end_at`
- Appointments must start and end on the **same local day** (provider timezone)

### Authorization Rules

- Clients can only access and modify their own appointments
- Providers cannot book appointments as clients
- Provider-only endpoints are fully protected

### State Model

- Appointments follow a strict lifecycle:
  - `pending → confirmed`
  - `pending → canceled`
  - `confirmed → canceled`

Invalid transitions are rejected at the API level.

---

## 4. Persistence & Data Model

- All data is stored in **PostgreSQL**
- Schema changes are managed via **Alembic migrations**
- Data integrity is preserved through:
  - Database constraints
  - Service-layer validation
  - Explicit transaction boundaries

### Time Handling Strategy

- Appointments are stored as `TIMESTAMPTZ` (UTC in the database)
- Provider availability is defined in local time
- Timezone conversion is applied only for:
  - Availability validation
  - Slot generation
  - Display purposes (frontend)

---

## 5. Frontend Role in the System

The frontend is **not responsible** for enforcing business rules.

Its responsibilities are limited to:
- Authentication flow orchestration
- Data visualization
- User interaction and feedback
- Routing and role-based navigation

The frontend:
- Does not duplicate validation logic
- Does not maintain independent appointment state
- Does not assume correctness without API confirmation

All critical decisions remain server-side.

---

## 6. Out of Scope (Strict)

The following features are explicitly excluded from the MVP:

- Payments and billing
- Email or SMS notifications
- External calendar integrations (Google Calendar, etc.)
- Admin dashboards or admin roles
- Social authentication (Google, OAuth)
- Offline support
- Native mobile applications
- Multi-provider coordination
- Vacation or holiday calendars

These exclusions are intentional to keep the MVP focused and correct.

---

## 7. System Characteristics

- API-first architecture
- Deterministic behavior with explicit error handling
- Environment-based configuration
- Reproducible local setup
- Clear separation between:
  - API (business logic)
  - Frontend (presentation)

The system is designed to be **extended**, not rewritten.

---

## 8. Assumptions & Constraints

To keep the MVP bounded:

- Appointments must not span multiple calendar days
- Appointment duration is fixed to 30-minute increments
- Availability is weekly recurring (no exceptions)
- Only one provider exists
- Only one administrative identity exists (provider)

These constraints are documented and enforced consistently across the system.

---

## 9. Evolution Path (Non-MVP)

The architecture allows future extensions such as:
- Multiple providers
- Provider vacations / exceptions
- Refresh tokens
- Notifications
- Payments
- Calendar synchronization

None of these require fundamental architectural changes.

---

## Summary

This system is intentionally conservative:
- correctness > convenience
- backend authority > frontend assumptions
- explicit rules > implicit behavior

The MVP is small by design, but structurally sound.
