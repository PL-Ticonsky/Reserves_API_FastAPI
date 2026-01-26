# ADR-0002: Time and Timezone Model

## Status
Accepted

## Context
The booking system is time-sensitive and must correctly handle:
- Appointments
- Availability windows
- Overlap validation

Incorrect time handling is a common source of bugs in booking systems.

## Decision
- All datetime values are stored in the database using **TIMESTAMPTZ**.
- All datetimes are stored in **UTC** internally.
- The barber (provider) has a defined timezone, which is used for:
  - Availability validation
  - Slot generation
- Incoming datetimes must be provided in **ISO 8601 format with timezone offset**.
- Appointments must start and end on the **same local day** (simplification for MVP).

## Alternatives Considered
- Storing local times without timezone information.
- Converting all times on the frontend.
- Allowing appointments to cross midnight.

These options were rejected due to higher complexity and increased risk of inconsistencies.

## Consequences
- Consistent and predictable time behavior.
- Easier reasoning about availability and overlaps.
- Simplified implementation suitable for MVP scope.
- Clear path to extend the model in future versions if needed.
