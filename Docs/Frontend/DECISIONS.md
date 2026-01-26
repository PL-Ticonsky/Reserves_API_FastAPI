# Frontend Design Decisions

This document captures the **key design decisions** behind the frontend layer of the Booking & Appointment System MVP.

The frontend is intentionally simple, explicit, and fully dependent on the backend API. No business rules are duplicated here.

---

## 1. Why a Dedicated Frontend Layer

The frontend exists to:
- Provide a clean and usable interface for clients and the provider
- Consume the REST API exclusively
- Visualize state, not enforce business rules

All validation, authorization, and state transitions are enforced **server-side**.

---

## 2. Framework Choice: Next.js (App Router)

**Next.js App Router** was chosen because it provides:
- File-based routing aligned with mental models
- Built-in support for server + client components
- Easy environment configuration
- Production-grade defaults

The App Router also allows:
- Clear separation between public and protected routes
- Predictable navigation behavior
- Clean redirects based on authentication state

---

## 3. Styling & UI Components

### Tailwind CSS
Chosen for:
- Speed of iteration
- Consistent spacing and typography
- Utility-first clarity over custom CSS abstractions

### shadcn/ui
Used for:
- Accessible base components
- Minimal, SaaS-like visual style
- Full control over markup and behavior (no black boxes)

Only foundational components are used (Button, Card, Dialog, etc.).

---

## 4. Authentication Strategy (MVP)

- Authentication is JWT-based
- Tokens are stored in `localStorage`
- Token is attached to every request via `Authorization: Bearer`

This is acceptable for an MVP because:
- No sensitive PII is stored client-side
- No refresh-token rotation is required yet
- Simplicity is prioritized over advanced session handling

---

## 5. Role-Based Navigation

The frontend does not decide permissions.

Instead:
1. User logs in
2. Token is stored
3. `/me` endpoint determines the role
4. User is redirected to the correct dashboard

This avoids frontend role drift.

---

## 6. State Management Philosophy

- No Redux / Zustand / global stores
- Local state + React hooks only
- Shared logic extracted into `lib/`

This keeps the mental model small and avoids over-engineering.

---

## 7. What Was Explicitly NOT Implemented

By design, the frontend does NOT:
- Validate business rules
- Handle timezone math independently
- Maintain appointment state machines
- Cache or mutate server state optimistically

These responsibilities belong to the backend.

---

## 8. MVP Scope Boundaries

The frontend intentionally supports:
- Single provider
- Single active session
- No offline mode
- No optimistic UI

These can be added later without rewriting architecture.
