# ADR-003 – Service layer organization and client authorization

## Status

Accepted

---

## Date

2026-07-14

---

## Context

The application now contains authentication, collaborator management and client management.

As the number of business operations grows, keeping every module directly under `src` would make the project harder to navigate. At the same time, authentication and authorization are transversal security concerns used by several business domains.

The client-management specifications also require two different authorization rules:

- only commercial collaborators may create clients;
- only the commercial collaborator responsible for a client may update it.

The architecture must therefore separate CLI concerns, reusable security rules and domain business logic while applying the principle of least privilege.

---

## Problem

How should business services and transversal authentication be organized, and where should client permissions be enforced?

---

## Decision

Business services are grouped inside the `src/services` package.

```text
src/
├── auth.py
├── main.py
└── services/
    ├── user_service.py
    └── client_service.py
```

The responsibilities are distributed as follows:

- `main.py` handles CLI input and output.
- `auth.py` handles authentication and reusable role-based authorization.
- `user_service.py` handles collaborator business rules.
- `client_service.py` handles client business rules.

`auth.py` remains directly under `src` because it is a transversal security module rather than a domain service.

Authorization is enforced inside the service layer:

- `create_client()` requires the `COMMERCIAL` department and automatically assigns the authenticated commercial user as the client's sales contact;
- `list_all_clients()` permits active users from the three authorized departments to read all clients;
- `update_client()` requires both the `COMMERCIAL` department and ownership of the selected client.

Collaborator deletion is implemented as account deactivation using `is_active=False` instead of physical deletion.

---

## Rationale

### Clear module responsibilities

The CLI remains focused on interaction with the user, while services contain business rules and database operations.

### Transversal authentication

Authentication and authorization are reused by several services. Keeping `auth.py` outside a specific domain service prevents it from being incorrectly associated with only user or client management.

### Defense in depth

Permissions are enforced in the services rather than only in CLI commands. This prevents unauthorized operations if a service is called from another entry point in the future.

### Least privilege

Client creation is restricted to commercial users, while client updates additionally require ownership. Read access remains available to all authenticated collaborators, as required by the specifications.

### Referential integrity

Deactivating collaborators preserves clients, contracts and events already linked to their user record.

---

## Consequences

### Positive

- Clearer and more maintainable project structure.
- Reusable authentication and authorization rules.
- Business rules remain independent from the CLI.
- Role and ownership checks are enforced close to database operations.
- Related CRM records remain valid after collaborator deactivation.
- Future contract and event services can follow the same organization.

### Negative

- Imports must use both `src.auth` and `src.services...`.
- The authorization flow is distributed between a transversal module and domain services.
- Soft-deleted collaborators remain stored in the database and require filtering through `is_active`.

---

## Alternatives considered

### Keep every module directly under `src`

Rejected because the growing number of business services would reduce clarity and maintainability.

### Move `auth.py` into `src/services`

Rejected because authentication and authorization are transversal security concerns rather than domain business services.

### Enforce permissions only in `main.py`

Rejected because service functions could then be called without the required authorization checks.

### Physically delete collaborators

Rejected because clients, contracts and events may reference collaborator records. Physical deletion could break relational integrity or remove useful historical information.

### Allow any commercial user to update any client

Rejected because the specifications restrict updates to clients for whom the commercial user is responsible.

---

## References

- OpenClassrooms Project 12 specifications.
- ADR-001 – Project architecture.
- ADR-002 – Authentication architecture.
- Principle of least privilege.
