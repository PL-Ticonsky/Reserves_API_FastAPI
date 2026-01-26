# DB_DESIGN — Booking / Appointment MVP

This document defines the database design for the Booking MVP.
The system supports multiple clients and a single provider (barber).

The database is designed to enforce business rules at the data level whenever possible.

---

## Design principles

- Use UUIDs as primary keys
- Store all datetime values as `timestamptz`
- Enforce critical rules using database constraints
- Keep the schema simple and extensible
- Avoid duplicating state across tables

---

## Entities

### 1. Users

Represents all authenticated users in the system.

There are two roles:
- `client`
- `provider` (single barber)

#### Attributes
- `id` (UUID, PK)
- `email` (TEXT, UNIQUE, NOT NULL)
- `password_hash` (TEXT, NOT NULL)
- `role` (ENUM: client | provider, NOT NULL)
- `is_active` (BOOLEAN, default true)
- `created_at` (TIMESTAMPTZ, default now)

#### Notes
- Only one user with role `provider` is expected to exist
- Authentication and authorization are role-based
- Users do not store direct references to appointments

---

### 2. Provider Availability

Defines the weekly working hours of the barber.

Availability is recurring and based on weekdays.

#### Attributes
- `id` (UUID, PK)
- `weekday` (SMALLINT, NOT NULL)  
  - Values: 0 = Monday … 6 = Sunday
- `start_time` (TIME, NOT NULL)
- `end_time` (TIME, NOT NULL)
- `is_active` (BOOLEAN, default true)

#### Constraints
- `start_time < end_time`

#### Notes
- Multiple availability blocks per day are allowed
  (e.g. 09:00–12:00 and 14:00–18:00)
- Availability does not represent reservations
- Vacations and exceptions are out of scope for the MVP

---

### 3. Appointments

Represents a booked time slot between a client and the barber.

#### Attributes
- `id` (UUID, PK)
- `client_id` (UUID, FK → users.id)
- `start_at` (TIMESTAMPTZ, NOT NULL)
- `end_at` (TIMESTAMPTZ, NOT NULL)
- `status` (ENUM: pending | confirmed | canceled, default pending)
- `cancel_reason` (TEXT, NULL)
- `created_at` (TIMESTAMPTZ, default now)
- `updated_at` (TIMESTAMPTZ, default now)

#### Constraints
- `start_at < end_at`
- A client cannot have overlapping appointments
- Appointments must not overlap with other active appointments
  (pending or confirmed)

#### Notes
- Overlap prevention should be enforced at the database level
  using PostgreSQL range constraints where possible
- Business rules related to availability are validated at the service layer
- Canceled appointments do not block time slots

---

## Relationships

- A user (client) can have many appointments
- An appointment belongs to exactly one client
- Availability blocks belong implicitly to the single provider
- The provider manages all appointments but does not own them as a client

---

## Status lifecycle

Appointments follow a strict state machine:

- `pending → confirmed`
- `pending → canceled`
- `confirmed → canceled`
- `canceled` is a terminal state

Invalid transitions must be rejected by the backend.

---

## Time handling

- All datetime values are stored as `timestamptz`
- The provider timezone is used to validate availability
- Appointments must start and end on the same local day
  (simplification for MVP)

---

## Out of scope (database level)

- Payments
- Notifications
- Appointment completion tracking
- Historical availability changes
- Admin audit logs
