# ADR-0001: Tech Stack Selection

## Status
Accepted

## Context
We are building a backend-first MVP for a booking/appointment system for a single-provider business (hair salon).

The system requires:
- A REST API
- Strong request validation
- Clear separation of concerns
- Time-based business rules
- Relational data with constraints
- A stack suitable for backend portfolio and real-world usage

## Decision
We decided to use the following stack:

- **Python 3.12+**
- **FastAPI** for the API layer
- **SQLAlchemy 2.x** as ORM
- **PostgreSQL** as the relational database
- **Alembic** for database migrations
- **JWT (JSON Web Tokens)** for authentication

## Alternatives Considered
- **Django + Django REST Framework**
  - Rejected due to higher abstraction level and less explicit control over business rules.
- **Flask**
  - Rejected due to lack of built-in validation and structure compared to FastAPI.
- **Node.js (Express/NestJS)**
  - Rejected to focus on Python backend roles and ecosystem.
- **NoSQL databases**
  - Rejected due to the need for strong relational constraints and time-based validation.

## Consequences
- Clear and explicit backend architecture.
- Strong typing and validation via Pydantic.
- Full control over business rules and database behavior.
- Slightly more manual setup compared to full-stack frameworks, but better learning and maintainability.
