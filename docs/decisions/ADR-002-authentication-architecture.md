# ADR-002 – Authentication architecture

## Status

Accepted

---

## Date

2026-07-09

---

## Context

The project specifications require every collaborator to authenticate before accessing the CRM.

Passwords must be stored securely, user permissions must depend on the user's department, and the principle of least privilege must be respected.

The authentication implementation should remain maintainable and avoid mixing command-line logic, business logic and security concerns.

---

## Problem

How should authentication and authorization be organized while keeping the application modular, secure and maintainable?

---

## Decision

Authentication responsibilities are separated across dedicated modules.

- **main.py** defines CLI commands and collects user input.
- **user_service.py** validates user data and hashes passwords before storing them.
- **auth.py** authenticates users and enforces role-based authorization.
- **User** stores only password hashes, never plain-text passwords.

Passwords are hashed using **Passlib** with the **bcrypt** algorithm before being persisted.

Authorization is based on the authenticated user's department.

---

## Rationale

### Separation of responsibilities

Each module has a single responsibility.

The command layer remains independent from authentication and business logic.

### Password security

Password hashing prevents credentials from being stored in plain text and follows the project security requirements.

### Reusable authorization

Keeping authorization inside a dedicated module allows the same permission checks to be reused throughout the application.

---

## Consequences

### Positive

- Clear separation of responsibilities.
- Improved maintainability.
- Secure password storage.
- Reusable authentication logic.
- Reusable authorization logic.

### Negative

- Introduces an additional dependency (`passlib`).
- Authentication is distributed across several modules instead of a single file.

---

## Alternatives considered

### Authentication inside `main.py`

Rejected because it mixes presentation, business and security logic.

### Password hashing in the CLI layer

Rejected because security logic belongs to the service layer rather than the user interface.

### Plain-text password storage

Rejected because it violates security best practices and the project requirements.

---

## References

- OpenClassrooms Project 12 specifications.
- Passlib documentation.
- bcrypt documentation.