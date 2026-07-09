# ADR-001 – Project architecture

## Status

Accepted

---

## Date

2026-07-01

---

## Context

Epic Events needs a secure command-line Customer Relationship Management (CRM) application.

According to the project specifications, the application must:

- use Python 3;
- run as a command-line interface (CLI);
- store its data in an SQL database;
- implement authentication and role-based authorization;
- follow the principle of least privilege;
- protect against SQL injection;
- log application errors using Sentry.

The project is intended to remain lightweight, maintainable and easy to deploy.

---

## Problem

Which technologies and project architecture should be chosen to build a secure, maintainable and scalable CRM application while remaining compliant with the project specifications?

---

## Decision

The application will be developed using the following architecture:

- **Typer** for the command-line interface.
- **Peewee** as the Object-Relational Mapper (ORM).
- **SQLite** as the relational database.
- **Sentry SDK** for error logging and monitoring.
- **pytest** for automated testing.

The source code is organized inside the `src` package to clearly separate:

- application entry point;
- configuration;
- database access;
- business models;
- future services and controllers.

The application is executed using:

```bash
python -m src.main
```

---

## Rationale

### Typer

Provides a clean and intuitive command-line interface while remaining lightweight and fully compatible with Python type hints.

### Peewee

Offers a simple and readable ORM well suited to small and medium-sized projects without introducing unnecessary complexity.

### SQLite

Perfectly fits the project requirements.

It requires no external server, is easy to distribute, and allows rapid development while remaining fully SQL compliant.

### Sentry

Allows centralized monitoring of unexpected exceptions and runtime errors, improving maintainability and debugging.

### src package

Keeping all source files inside a dedicated package improves project organization and allows reliable absolute imports.

---

## Consequences

### Positive

- Lightweight architecture.
- Easy deployment.
- Readable codebase.
- Clear separation of responsibilities.
- Fast development.
- Simple project installation.

### Negative

- SQLite is not intended for high-concurrency production environments.
- Peewee does not provide Django-style migrations by default.
- Some features usually provided by larger frameworks must be implemented manually.

---

## Alternatives considered

### Django

Rejected because the project is a command-line application and does not require a complete web framework.

### Flask

Rejected because the project does not expose HTTP routes or provide a web interface.

### SQLAlchemy

Rejected in favor of Peewee because Peewee provides a simpler API for the project's scope and aligns with the mentor's recommendation.

---

## References

- OpenClassrooms Project 12 specifications.
- Mentor technical recommendations.
- Peewee documentation.
- Typer documentation.