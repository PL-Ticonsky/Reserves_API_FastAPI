# Frontend State Management

This document describes how state is handled in the frontend application.

---

## Core Principle

The frontend is **not the source of truth**.

All authoritative state lives in the backend.

---

## Local State Only

The application uses:
- React `useState`
- React `useEffect`

State is scoped to:
- Pages
- Components
- Temporary UI interactions

---

## What Is Stored in State

- Form inputs
- Loading flags
- Fetched API responses
- UI visibility (dialogs, tabs)

---

## What Is NOT Stored in State

- Authentication rules
- Appointment lifecycle rules
- Availability logic
- Timezone conversions beyond display

---

## Shared Logic Location

Reusable logic lives in:

Including:
- `api.ts` — HTTP wrapper
- `auth.ts` — token helpers
- `time.ts` — formatting only
- `types.ts` — shared types

---

## Why No Global Store

Global stores were avoided because:
- App size is small
- State relationships are simple
- Backend already enforces correctness

This keeps the frontend easy to reason about.
