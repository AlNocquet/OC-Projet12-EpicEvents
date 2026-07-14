# ADR-005 – Event management architecture

## Status

Accepted

---

## Date

2026-07-14

---

## Context

Epic Events requires secure management of events linked to signed contracts.

According to the project specifications:

- every authenticated collaborator can consult all events in read-only mode;
- a commercial collaborator can create an event only for one of their clients and only when the related contract is signed;
- a management collaborator can filter events without an assigned support contact;
- a management collaborator can assign a support collaborator to an event;
- a support collaborator can filter events assigned to them;
- a support collaborator can update only events for which they are responsible.

The application must continue to apply the principle of least privilege and keep business rules outside the command-line interface.

---

## Problem

How should event creation, consultation, assignment and update operations be organized so that role-based permissions, ownership rules and data validation remain centralized, testable and secure?

---

## Decision

A dedicated service module is introduced:

```text
src/services/event_service.py
```

This module centralizes:

- event business logic;
- event-data validation;
- role-based authorization;
- client-ownership checks;
- support-assignment checks;
- Peewee database operations.

The Typer CLI in `src/main.py` remains responsible only for:

- collecting terminal input;
- securely authenticating the current user;
- parsing ISO-formatted dates;
- calling the event service;
- displaying results and explicit error messages.

The existing `Event` model remains unchanged because it already contains every field required by the specifications.

---

## Authorization rules

### Read access

All authenticated and active collaborators from the following departments may consult every event:

- `COMMERCIAL`;
- `SUPPORT`;
- `MANAGEMENT`.

### Event creation

Only an authenticated and active commercial collaborator may create an event.

The service additionally verifies that:

- the selected contract exists;
- the contract is signed;
- the client linked to the contract is assigned to the authenticated commercial collaborator.

### Support assignment

Only an authenticated and active management collaborator may assign a support contact.

The selected collaborator must:

- exist;
- be active;
- belong to the `SUPPORT` department.

### Event update

Only an authenticated and active support collaborator may update an event.

The service additionally verifies that the authenticated support collaborator is the event's current `support_contact`.

Support assignment itself remains restricted to management collaborators.

---

## Data validation

The service validates that:

- the event name is not empty;
- the location is not empty;
- the attendee count is an integer;
- Boolean values are not accepted as attendee counts;
- the attendee count is greater than zero;
- the start value is a valid `datetime`;
- the end value is a valid `datetime`;
- the end date occurs strictly after the start date;
- optional notes are stripped and empty notes are stored as `None`.

The CLI accepts ISO-formatted date strings and converts them before calling the service.

---

## Security considerations

- Authorization is enforced inside the service layer, not only in the CLI.
- Department checks are performed before protected event lookups when appropriate.
- Ownership and assignment checks complement role checks.
- Error messages explicitly reject forbidden operations.
- Peewee queries remain parameterized, limiting SQL injection risks.
- The principle of least privilege is applied to every write operation.
- Existing authentication, collaborator, client and contract security rules remain unchanged.

---

## Consequences

### Positive

- Event rules are centralized and reusable.
- The CLI remains thin and maintainable.
- Permissions can be tested independently from terminal interaction.
- Role, ownership and assignment rules are clearly separated.
- Event creation and update paths directly match the project specifications.
- Existing features remain unaffected.

### Negative

- Every CLI command requires a new authentication prompt because the current application does not maintain a persistent session.
- Date parsing is limited to ISO-compatible formats.
- The service performs several explicit validation checks that increase code length but improve clarity and security.

---

## Alternatives considered

### Put event rules directly in `main.py`

Rejected because business rules would be coupled to the CLI, harder to test and easier to bypass from another entry point.

### Allow management collaborators to update every event field

Rejected because the specifications only require management to assign support collaborators. Broader update permissions would violate the principle of least privilege.

### Allow commercial collaborators to update events after creation

Rejected because the specifications assign event updates to the responsible support collaborator.

### Store dates as strings

Rejected because `datetime` values provide safer validation, ordering and database filtering.

---

## Validation

The complete automated suite was executed successfully:

- Python 3.12.2;
- pytest 9.1.1;
- 134 tests collected;
- 134 tests passed;
- 0 failures;
- execution time: 131.47 seconds.

The event tests cover creation, consultation, filters, support assignment, update permissions, data validation and regression of all previously implemented features.

---

## References

- OpenClassrooms Project 12 specifications.
- Project autoevaluation checklist.
- Existing authentication and service-layer architecture.
