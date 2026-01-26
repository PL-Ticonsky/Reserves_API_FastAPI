# Frontend Routing Model

This document defines the routing structure and navigation rules of the frontend application.

---

## Public Routes

These routes are accessible without authentication.

| Route | Purpose |
|----|-------|
| `/` | Landing page |
| `/login` | User login |
| `/register` | Client registration |

---

## Protected Routes

These routes require a valid JWT token.

| Route | Role Required | Purpose |
|----|-------------|--------|
| `/client` | client | Client dashboard |
| `/provider` | provider | Provider dashboard |

---

## Navigation Rules

### 1. No Token
- Any access to protected routes redirects to `/login`

### 2. Token Present
- `/me` is called to determine role
- User is redirected accordingly

### 3. Role Mismatch
- client accessing `/provider` → redirected to `/client`
- provider accessing `/client` → redirected to `/provider`

---

## Redirect Strategy

Redirects are handled client-side after:
- Token presence check
- `/me` resolution

The frontend does not assume role from token payload.

---

## Error Handling

- 401 responses trigger automatic logout
- User is redirected to `/login`
- Token is cleared immediately
