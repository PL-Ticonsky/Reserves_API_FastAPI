# Frontend UX Flows

This document describes the user interaction flows supported by the frontend MVP.

---

## Client Flow

### Registration
1. User visits `/register`
2. Submits email + password
3. Account is created
4. Redirected to `/login`

---

### Booking an Appointment
1. User logs in
2. Redirected to `/client`
3. Selects date
4. Loads available slots
5. Chooses a slot
6. Confirms appointment
7. Appointment created with status `pending`

---

### Managing Appointments
- Pending appointments:
  - Can be canceled
  - Can be rescheduled
- Confirmed appointments:
  - Read-only (MVP)
- Canceled appointments:
  - Displayed as historical

---

## Provider Flow

### Availability Setup
1. Provider logs in
2. Opens availability view
3. Defines weekly schedule
4. Saves availability in bulk

---

### Appointment Management
1. Provider views appointments
2. Filters by status/date
3. Confirms pending appointments
4. Cancels appointments (optional reason)

---

## UX Constraints (By Design)

- No optimistic updates
- No silent state changes
- All actions provide feedback (toasts)
- All destructive actions require confirmation

---

## Empty States

Handled explicitly:
- No slots available
- No appointments
- No availability defined

These prevent ambiguous UI states.
