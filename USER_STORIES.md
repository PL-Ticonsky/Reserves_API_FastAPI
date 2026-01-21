# USER_STORIES — Booking MVP (Single Provider)

## Roles
- Client: books and manages their own appointments
- Provider (single): manages availability and appointments (the barber)

## Core functionality — Client
- As a client, I want to register and log in so I can manage my appointments.
- As a client, I want to view available time slots so I can choose a time.
- As a client, I want to create an appointment request so I can book a time.
- As a client, I want to reschedule my appointment so I can change the date/time.
- As a client, I want to cancel my appointment so I can free the slot.
- As a client, I want to view my appointment history so I can track my bookings.

## Core functionality — Provider (barber)
- As the barber, I want to log in so I can manage my schedule.
- As the barber, I want to define weekly availability blocks so clients can book within them.
- As the barber, I want to view all upcoming appointments so I can plan my day.
- As the barber, I want to confirm an appointment so the client knows it’s accepted.
- As the barber, I want to cancel an appointment (with a reason) so the client knows it won’t happen.
- As the barber, I want to filter appointments by date range and status so I can find what I need.

## Business rules (backend-enforced)
- The system must prevent overlapping appointments.
- The system must only allow appointments within barber availability.
- Clients can only view/modify their own appointments.
- Only the barber can confirm/cancel any appointment.
- Status flow:
  - pending -> confirmed
  - pending/confirmed -> canceled

## UI (optional / minimal)
- As a client, I want a simple view to book from available slots.
- As a client, I want a simple view to list/reschedule/cancel my appointments.
- As the barber, I want a simple view to see the agenda and confirm/cancel.
