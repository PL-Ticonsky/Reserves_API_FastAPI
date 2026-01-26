# Frontend Authentication Model

This document explains how authentication is handled on the frontend.

---

## Authentication Flow

1. User submits credentials on `/login`
2. Backend returns JWT access token
3. Token is stored in `localStorage`
4. Frontend calls `/me` to fetch user identity
5. User is redirected based on role

---

## Token Storage

- Stored in `localStorage`
- Key: `booking_token`
- Read on every authenticated request

This is acceptable for the MVP because:
- HTTPS is assumed in production
- No refresh tokens are implemented
- Session duration is short-lived

---

## Request Handling

All requests pass through a shared API wrapper:

- Adds Authorization header automatically
- Handles JSON parsing
- Centralizes error handling

---

## Automatic Logout

If any request returns HTTP 401:
- Token is immediately cleared
- User is redirected to `/login`

This ensures:
- No stale sessions
- Consistent auth state
- Simple recovery from token expiry

---

## Why No Refresh Tokens (Yet)

Refresh tokens were intentionally omitted to:
- Reduce system complexity
- Avoid partial session states
- Keep MVP scope focused

The architecture allows adding them later without breaking changes.
