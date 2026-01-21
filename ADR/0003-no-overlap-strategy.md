# ADR-0003: Appointment Overlap Strategy

## Status
Accepted

## Context
The system must prevent overlapping appointments for the same provider.

This rule must hold even under concurrent requests (race conditions), such as multiple clients booking the same slot at the same time.

## Decision
The overlap prevention strategy is implemented at two levels:

1. **Service Layer Validation**
   - Before creating or rescheduling an appointment, the service layer checks:
     - Time range validity
     - Provider availability
     - Existing active appointments that overlap
   - This allows returning clear and user-friendly error messages.

2. **Database-Level Enforcement**
   - The database is treated as the final authority.
   - Overlap is enforced so that only appointments with status:
     - `pending`
     - `confirmed`
     block time slots.
   - Appointments with status `canceled` do not block time.
   - Database constraints or transactional strategies are used to prevent race conditions.

## Alternatives Considered
- Validating overlaps only in the application layer.
- Serializing all appointment creation requests.

These alternatives were rejected because they do not fully protect against concurrency issues.

## Consequences
- Strong guarantees against double booking.
- Correct behavior even under concurrent requests.
- Slightly more complexity in database setup, but significantly higher data integrity.
