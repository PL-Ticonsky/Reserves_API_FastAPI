# Booking & Appointment API

> **MVP Version** — Single Provider Barber Shop System

A production-ready backend API for managing barber shop appointments with role-based authentication, time-slot availability, and comprehensive business rule enforcement.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org)

---

## Documentation

For detailed documentation, architecture diagrams, and advanced guides, see the [`docs/`](./docs) folder.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Usage Examples](#api-usage-examples)
- [Business Rules](#business-rules)
- [Status & Transitions](#status--transitions)
- [Timezone Handling](#timezone-handling)

---

## Features

### Authentication & Authorization
- **JWT Bearer Token** authentication
- **Role-based access control:**
  - `client` — Manages personal appointments only
  - `provider` — Full system access (availability & all appointments)

### Client Capabilities
- User registration & login
- View personal appointments
- Create new appointments (auto-status: `pending`)
- Cancel appointments (restriction: `pending` only)
- Reschedule appointments (restriction: `pending` only)

### Provider Capabilities (Single Barber MVP)
- Pre-seeded provider account
- Define weekly availability (bulk update)
- View all appointments with filters
- Confirm pending appointments
- Cancel appointments at any stage (with optional reason)

---

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **Python 3.12+** | Core language |
| **FastAPI** | REST API framework |
| **PostgreSQL** | Primary database |
| **SQLAlchemy 2.x** | ORM & query builder |
| **Alembic** | Database migrations |
| **psycopg v3** | PostgreSQL adapter |
| **JWT** | Secure authentication |

### Frontend

| Technology | Purpose |
|------------|---------|
| **Next.js 14+** | React framework (App Router) |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Accessible UI components |
| **React Hook Form** | Form management |
| **Zod** | Schema validation |

---

## Architecture

This project follows a **clean separation** between backend and frontend:

- **Backend:** Enforces all business rules, authentication, and data validation
- **Frontend:** Consumes the REST API, visualizes state, provides user interface

**Key Principle:** No business logic duplication. The frontend trusts the backend completely.

### Design Philosophy

- **Backend-first:** All validation, authorization, and state transitions are server-side
- **Frontend simplicity:** Focus on user experience, not rule enforcement
- **API-driven:** Frontend is a thin client over the REST API
- **Role-based access:** Navigation and permissions determined by backend responses

---

## Project Structure

### Backend

```
app/
│
├── main.py                    # Application entry point
│
├── api/
│   ├── deps.py               # Dependency injection
│   └── routers/
│       ├── auth.py           # Registration & login
│       ├── me.py             # Current user info
│       ├── me_appointments.py         # Client appointments
│       ├── availability_slots.py      # Public slot viewing
│       ├── barber_appointments.py     # Provider appointment mgmt
│       └── barber_availability.py     # Provider availability mgmt
│
├── core/
│   ├── config.py             # Environment configuration
│   └── security.py           # JWT & password hashing
│
├── db/
│   ├── base.py               # Base model class
│   ├── session.py            # Database session factory
│   └── seed.py               # Initial data seeding
│
├── models/                   # SQLAlchemy ORM models
│   ├── user.py
│   ├── availability.py
│   └── appointment.py
│
├── schemas/                  # Pydantic schemas (validation)
│   ├── auth.py
│   ├── user.py
│   ├── availability.py
│   └── appointment.py
│
├── repositories/             # Data access layer
│   ├── user_repo.py
│   ├── availability_repo.py
│   └── appointment_repo.py
│
├── services/                 # Business logic layer
│   ├── auth_service.py
│   ├── availability_service.py
│   └── appointment_service.py
│
├── migrations/               # Alembic migration files
└── tests/                    # Test suite
```

### Frontend

```
frontend/
│
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   │
│   ├── (auth)/              # Auth routes
│   │   ├── login/
│   │   └── register/
│   │
│   ├── client/              # Client dashboard
│   │   ├── layout.tsx
│   │   ├── page.tsx         # Appointment list
│   │   └── new/             # Create appointment
│   │
│   └── provider/            # Provider dashboard
│       ├── layout.tsx
│       ├── page.tsx         # All appointments
│       └── availability/    # Manage availability
│
├── components/
│   ├── ui/                  # shadcn/ui components
│   ├── appointment-card.tsx
│   ├── availability-form.tsx
│   └── slot-picker.tsx
│
├── lib/
│   ├── api.ts               # API client wrapper
│   ├── auth.ts              # Authentication helpers
│   └── utils.ts             # Utility functions
│
└── types/
    └── index.ts             # TypeScript definitions
```

---

## Getting Started

### Backend Setup

#### Prerequisites

- Python 3.12 or higher
- PostgreSQL 15+
- [uv](https://github.com/astral-sh/uv) package manager

#### 1. Environment Configuration

Create a `.env` file in the project root:

```env
# Database Connection
DATABASE_URL=postgresql+psycopg://reserves_user:YOUR_PASSWORD@127.0.0.1:5432/reserves_db

# JWT Configuration
JWT_SECRET=your_super_secret_key_change_in_production
JWT_EXPIRES_MINUTES=60

# Provider Timezone (for availability validation)
PROVIDER_TIMEZONE=America/Bogota

# Seeded Provider Credentials
PROVIDER_EMAIL=barber@mail.com
PROVIDER_PASSWORD=ProviderPass123!
```

> ⚠️ **Security Note:** Never commit `.env` to version control. Use `.env.example` for team reference.

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run Database Migrations

```bash
uv run alembic upgrade head
```

### 4. Seed Initial Provider

```bash
uv run python -m app.db.seed
```

**Expected output:**
```
✓ Provider seeded successfully
  ID: <uuid>
  Email: barber@mail.com
  Role: provider
```

### 5. Start the Server

```bash
uv run uvicorn app.main:app --reload
```

**Endpoints:**
- API: http://127.0.0.1:8000
- Interactive Docs: http://127.0.0.1:8000/docs
- OpenAPI Schema: http://127.0.0.1:8000/openapi.json

---

### Frontend Setup
---

## Frontend Interface (MVP)

The frontend provides a **clean, minimal, and role-aware UI** built exclusively on top of the backend API.

It focuses on:
- Simple booking for clients
- Clear decision-making for the provider
- Explicit visibility of appointment status
- No hidden or implicit actions

Below are real screenshots of the current MVP.

---

### Landing Page

Public entry point explaining the booking flow and system constraints.

![Landing page](Docs/assets/frontend/landing.png)

---

### Client Dashboard — Empty State

When no availability exists for a selected day, the system clearly communicates it.

![Client empty slots](Docs/assets/frontend/client-empty-slots.png)

---

### Client Dashboard — Available Time Slots

Clients select a date, load slots from the backend, and request an appointment.

All slots are generated server-side and reflect real availability.

![Client slots](Docs/assets/frontend/client-slots.png)

---

### Provider Dashboard — Availability Management

The provider defines **weekly availability blocks**.
Saving sends a full bulk payload to the backend.

![Provider availability](Docs/assets/frontend/provider-availability.png)

---

### Provider Dashboard — Appointment Management

Providers review appointments, filter by status/date, and confirm or cancel requests.

All decisions are enforced server-side.

![Provider appointments](Docs/assets/frontend/provider-appointments.png)

---

#### Prerequisites

- Node.js 18+ or Bun
- Backend API running on `http://127.0.0.1:8000`

#### 1. Environment Configuration

Navigate to the frontend directory and create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

#### 2. Install Dependencies

```bash
cd frontend
npm install
# or
bun install
```

#### 3. Start Development Server

```bash
npm run dev
# or
bun dev
```

**Access the application:**
- Frontend: http://localhost:3000

#### 4. Default Credentials

**Provider Account:**
- Email: `barber@mail.com`
- Password: `ProviderPass123!`

**Client Account:**
- Register a new account at `/register`

---

### Frontend Design Principles

The frontend is intentionally simple and follows these rules:

1. **No business logic duplication** — All validation happens in the backend
2. **Explicit API consumption** — Every action is a direct API call
3. **Role-based navigation** — User role determines available routes
4. **State visualization only** — Frontend displays state, doesn't enforce it
5. **JWT token storage** — Tokens stored in `localStorage` (MVP approach)

For detailed frontend architecture decisions, see [`docs/frontend-design.md`](./docs/frontend-design.md)

---

## API Usage Examples

### Authentication Flow

#### Register New Client

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@mail.com",
    "password": "StrongPass123!"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "client@mail.com",
  "role": "client"
}
```

#### Login (Client/Provider)

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@mail.com",
    "password": "StrongPass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

> **Note:** Save the `access_token` for subsequent requests

---

### Provider Operations

#### Set Weekly Availability

```bash
curl -X POST http://127.0.0.1:8000/barber/availability/bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <PROVIDER_TOKEN>" \
  -d '[
    {
      "weekday": 0,
      "start_time": "09:00",
      "end_time": "12:00"
    },
    {
      "weekday": 0,
      "start_time": "14:00",
      "end_time": "18:00"
    },
    {
      "weekday": 1,
      "start_time": "09:00",
      "end_time": "17:00"
    }
  ]'
```

> **Weekday Reference:** 0=Monday, 1=Tuesday, ..., 6=Sunday

#### View All Appointments

```bash
curl "http://127.0.0.1:8000/barber/appointments?status_=pending" \
  -H "Authorization: Bearer <PROVIDER_TOKEN>"
```

#### Confirm Appointment

```bash
curl -X PATCH "http://127.0.0.1:8000/barber/appointments/<APPOINTMENT_ID>/confirm" \
  -H "Authorization: Bearer <PROVIDER_TOKEN>"
```

---

### Client Operations

#### View Available Time Slots

```bash
curl "http://127.0.0.1:8000/availability/slots?date=2026-01-26&slot_minutes=30" \
  -H "Authorization: Bearer <CLIENT_TOKEN>"
```

**Response:**
```json
[
  {
    "start": "2026-01-26T09:00:00-05:00",
    "end": "2026-01-26T09:30:00-05:00"
  },
  {
    "start": "2026-01-26T09:30:00-05:00",
    "end": "2026-01-26T10:00:00-05:00"
  }
]
```

#### Create Appointment

```bash
curl -X POST http://127.0.0.1:8000/appointments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <CLIENT_TOKEN>" \
  -d '{
    "start_at": "2026-01-26T09:00:00-05:00",
    "end_at": "2026-01-26T09:30:00-05:00",
    "description": "Haircut and beard trim"
  }'
```

#### View My Appointments

```bash
curl http://127.0.0.1:8000/appointments \
  -H "Authorization: Bearer <CLIENT_TOKEN>"
```

#### Cancel Appointment

```bash
curl -X PATCH "http://127.0.0.1:8000/appointments/<APPOINTMENT_ID>/cancel" \
  -H "Authorization: Bearer <CLIENT_TOKEN>"
```

---

## Business Rules

The API enforces the following constraints at the service layer:

| Rule | Description |
|------|-------------|
| **No Overlaps** | Pending + confirmed appointments block time slots |
| **Availability Check** | Appointments must fall within provider's weekly schedule |
| **Time Validation** | `start_at` must precede `end_at` |
| **Single-Day Limit** | Appointments cannot span multiple calendar days (provider timezone) |
| **Authorization** | Clients can only access their own appointments |
| **Role Separation** | Clients cannot access provider-only endpoints |

---

## Status & Transitions

### Appointment States

```
pending → confirmed
   ↓         ↓
canceled ← canceled
```

### Allowed Transitions

| Actor | From State | To State | Notes |
|-------|-----------|----------|-------|
| **Client** | `pending` | `canceled` | Only their own appointments |
| **Client** | `pending` | `pending` | Reschedule (update times) |
| **Provider** | `pending` | `confirmed` | Accept appointment |
| **Provider** | `pending` | `canceled` | Reject with optional reason |
| **Provider** | `confirmed` | `canceled` | Cancel confirmed with reason |

---

## Timezone Handling

### Storage Strategy

- **Availability:** Stored as weekly patterns with `TIME` fields (provider timezone)
- **Appointments:** Stored as `TIMESTAMPTZ` (UTC in database)

### Input Requirements

All datetime inputs must include timezone offset:

✅ **Correct:**
```json
{
  "start_at": "2026-01-26T09:00:00-05:00"
}
```

❌ **Incorrect:**
```json
{
  "start_at": "2026-01-26T09:00:00"
}
```

### Configuration

Set the provider's timezone in `.env`:

```env
PROVIDER_TIMEZONE=America/Bogota  # GMT-5
```

This timezone is used for:
- Validating appointments against weekly availability
- Preventing appointments from crossing calendar days
- Generating available time slots

---

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

**Built with ❤️ using FastAPI & PostgreSQL**