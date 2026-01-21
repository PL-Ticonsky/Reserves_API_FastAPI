# API_CONTRACT — Booking / Appointment MVP (Single Provider)

This document defines the HTTP API contract for the Booking MVP.

## Conventions

- Base URL: `/api/v1`
- Auth: Bearer JWT (`Authorization: Bearer <token>`)
- All datetimes are ISO 8601 with timezone offset (e.g. `2026-01-20T15:00:00-05:00`)
- Responses are JSON
- Errors use a consistent format (see Errors section)

---

## Roles

- `client`: can manage only their own appointments
- `provider`: can manage availability and all appointments

---

## Auth

### POST `/auth/register`
Register a new client user.

**Auth:** public  
**Body:**
```json
{ "email": "user@mail.com", "password": "StrongPass123!" }
```
**200 Response**
```json
{ "id": "uuid", "email": "user@mail.com", "role": "client" }
```
**Erros**

409 EMAIL_ALREADY_EXISTS

## Login

### POST `/auth/login`
Log in an already existing user.

**Auth:** public  
**Body:**
```json
{ "email": "user@mail.com", "password": "StrongPass123!" }
```
**200 Response**
```json
{
  "access_token": "jwt",
  "token_type": "bearer"
}

```
**Erros**

401 INVALID_CREDENTIALS


## View Appointments (Client)

### GET `/me/appointments`
View all appointments for the authenticated client.

**Auth:** client  
**Headers:** `Authorization: Bearer <token>`

**Query (optional):**
- `from`: ISO datetime
- `to`: ISO datetime
- `status`: pending | confirmed | canceled

**200 Response**
```json
[
  {
    "id": "uuid",
    "start_at": "2026-01-21T15:00:00Z",
    "end_at": "2026-01-21T15:30:00Z",
    "status": "confirmed"
  }
]
``` 

**Erros**
401 UNAUTHORIZED (missing/invalid token)

## View One Appointment (Client)

### GET `/me/appointments/{id}`
View one appointments for the authenticated client.

**Auth:** client  
**Headers:** `Authorization: Bearer <token>`


**200 Response**
```json

  {
    "id": "uuid",
    "start_at": "2026-01-21T15:00:00Z",
    "end_at": "2026-01-21T15:30:00Z",
    "status": "confirmed"
  }

``` 

**Erros**
401 UNAUTHORIZED (missing/invalid token)

## View Availability Slots (Client)

### GET `/availability/slots`
List available time slots for booking.

**Auth:** client  
**Headers:** `Authorization: Bearer <token>`

**Query (required):**
- `date`: YYYY-MM-DD

**Query (optional):**
- `slot_minutes`: integer (default 30)

**200 Response**
```json
[
  { "start_at": "2026-01-21T15:00:00Z", "end_at": "2026-01-21T15:30:00Z" },
  { "start_at": "2026-01-21T15:30:00Z", "end_at": "2026-01-21T16:00:00Z" }
]
```

**Erros**
401 UNAUTHORIZED (missing/invalid token)


## Create Appointment

### POST `/appointments`
Create an appointment request for the authenticated client.

**Auth:** client  
**Headers:** `Authorization: Bearer <token>`

**Body**
```json
{
  "start_at": "2026-01-21T10:00:00-05:00",
  "end_at": "2026-01-21T10:30:00-05:00",
  "description": "Haircut"
}
```
**200 Response**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "start_at": "2026-01-21T15:00:00Z",
  "end_at": "2026-01-21T15:30:00Z",
  "status": "pending",
  "description": "Haircut",
  "created_at": "2026-01-20T18:00:00Z"
}
```
**Erros**

401 UNAUTHORIZED

409 APPOINTMENT_OVERLAP

422 OUTSIDE_AVAILABILITY

422 INVALID_TIME_RANGE

## Modify Appointment

### PATCH `/me/appointments/{id}/reschedule`

Modify an appointment of an already schedule appointment for the authenticated client

**Auth:** client  
**Headers:** `Authorization: Bearer <token>`

**Body**
```json
{
  "start_at": "2026-01-21T10:00:00-05:00",
  "end_at": "2026-01-21T10:30:00-05:00"
}
```
**200 Response**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "start_at": "2026-01-21T15:00:00Z",
  "end_at": "2026-01-21T15:30:00Z",
  "status": "pending",
  "updated_at": "2026-01-20T18:00:00Z"
}
```
**Erros**
401 UNAUTHORIZED

403 FORBIDDEN

404 APPOINTMENT_NOT_FOUND

409 APPOINTMENT_OVERLAP

422 OUTSIDE_AVAILABILITY

400 INVALID_STATUS_TRANSITION


## Cancel Appointment
### PATCH `/me/appointments/{id}/cancel`

Cancel an existing appointment for the authenticated client.

**Auth:** client  
**Headers:** `Authorization: Bearer <token>`

**200 Response**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "start_at": "2026-01-21T15:00:00Z",
  "end_at": "2026-01-21T15:30:00Z",
  "status": "canceled",
  "updated_at": "2026-01-20T18:00:00Z"
}
```
**Erros**
401 UNAUTHORIZED

403 FORBIDDEN

404 APPOINTMENT_NOT_FOUND

400 INVALID_STATUS_TRANSITION

## View all appointments (barber)
### GET `/barber/appointments`
View all appointments (barber agenda).

**Auth:** provider  
**Headers:** `Authorization: Bearer <token>`

**Query (optional):**
- `from`: ISO datetime
- `to`: ISO datetime
- `status`: pending | confirmed | canceled

**200 Response**
```json
[
  {
    "id": "uuid",
    "client_id": "uuid",
    "start_at": "2026-01-21T15:00:00Z",
    "end_at": "2026-01-21T15:30:00Z",
    "status": "pending"
  }
]
``` 

**Erros** 
401 UNAUTHORIZED,
403 FORBIDDEN (if not provider)



## Create Barber Availability (bulk)

### POST `/barber/availability/bulk`

**Auth:** provider  
**Headers:** `Authorization: Bearer <token>`

**Body**
```json
[
  { "weekday": 0, "start_time": "09:00", "end_time": "12:00" },
  { "weekday": 0, "start_time": "14:00", "end_time": "18:00" }
]
```
**201 Response**
```json
[
  { "id": "uuid", "weekday": 0, "start_time": "09:00", "end_time": "12:00", "is_active": true },
  { "id": "uuid", "weekday": 0, "start_time": "14:00", "end_time": "18:00", "is_active": true }
]

```
**Errors**

401 UNAUTHORIZED

403 FORBIDDEN

422 INVALID_TIME_RANGE

## Confirm Appointment (Barber)

### PATCH `/barber/appointments/{id}/confirm`
Confirm an appointment as the barber (provider).

**Auth:** provider  
**Headers:** `Authorization: Bearer <token>`

**200 Response**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "start_at": "2026-01-21T15:00:00Z",
  "end_at": "2026-01-21T15:30:00Z",
  "status": "confirmed",
  "updated_at": "2026-01-20T18:00:00Z"
}
```
**Errors**
401 UNAUTHORIZED

403 FORBIDDEN

404 APPOINTMENT_NOT_FOUND

400 INVALID_STATUS_TRANSITION
## Cancel Appointment (Barber)

### PATCH `/barber/appointments/{id}/cancel`
Cancel an appointment as the barber (provider).

**Auth:** provider  
**Headers:** `Authorization: Bearer <token>`

**Body (optional)**
```json
{ "reason": "Barber unavailable" }
```
**200 Response**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "start_at": "2026-01-21T15:00:00Z",
  "end_at": "2026-01-21T15:30:00Z",
  "status": "canceled",
  "cancel_reason": "Barber unavailable",
  "updated_at": "2026-01-20T18:00:00Z"
}
```
**Errors**
401 UNAUTHORIZED

403 FORBIDDEN

404 APPOINTMENT_NOT_FOUND

400 INVALID_STATUS_TRANSITION