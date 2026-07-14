# UML v0.7 - Event management and authorization

## Status

Validated

## Date

2026-07-14

## Validation

- Complete suite executed with Python 3.12.2 and pytest 9.1.1.
- 134 tests collected.
- 134 tests passed.
- No regression detected in authentication, collaborator management, client management, contract management or database initialization.
- Event tests validate creation, consultation, filters, support assignment, update permissions and event-data validation.

---

## Evolution

Compared to UML v0.6:

- Added the event service to the business-service package.
- Added commercial event creation for signed contracts.
- Added commercial client-ownership validation.
- Added event consultation by all authenticated collaborators.
- Added the management filter for unassigned events.
- Added support assignment by management.
- Added the support filter for assigned events.
- Added event updates restricted to the assigned support collaborator.
- Added event text, attendee, date and notes validation.
- Preserved every previously implemented workflow.

---

## Project structure

```text
src/
├── auth.py
├── config.py
├── database.py
├── main.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── client.py
│   ├── contract.py
│   └── event.py
└── services/
    ├── __init__.py
    ├── user_service.py
    ├── client_service.py
    ├── contract_service.py
    └── event_service.py
```

Responsibilities:

- `main.py` defines CLI commands, parses dates, collects terminal input and displays results.
- `auth.py` authenticates users and applies reusable role-based authorization.
- `user_service.py` contains collaborator business rules.
- `client_service.py` contains client business rules.
- `contract_service.py` contains contract business rules and financial validation.
- `event_service.py` contains event business rules, event validation and event authorization.
- `models/` defines the Peewee entities and relationships.

---

## Entities

### User

Attributes:

- id
- full_name
- email
- password_hash
- department
- is_active

Relationships:

- One commercial User manages several Clients.
- One commercial User is associated with several Contracts.
- One support User can be assigned to several Events.

Relevant event rules:

- Only an active commercial User can create an Event.
- Only an active management User can assign a support User to an Event.
- Only the active support User assigned to an Event can update it.

---

### Client

Attributes:

- id
- full_name
- email
- phone
- company_name
- created_at
- updated_at
- sales_contact -> User

Relationships:

- One Client belongs to one commercial User.
- One Client can have several Contracts.

Relevant event rule:

- Event creation permission is determined from the commercial User assigned to the Client linked through the Contract.

---

### Contract

Attributes:

- id
- client -> Client
- sales_contact -> User
- total_amount
- amount_due
- is_signed
- created_at

Relationships:

- One Contract belongs to one Client.
- One Contract can have several Events.

Relevant event rules:

- An Event must reference an existing Contract.
- An Event can only be created when `Contract.is_signed` is `True`.

---

### Event

Attributes:

- id
- contract -> Contract
- support_contact -> User, nullable
- event_name
- location
- attendees
- event_start
- event_end
- notes

Relationships:

- One Event belongs to one Contract.
- One Event can be assigned to zero or one support User.
- One support User can be assigned to several Events.

Business rules:

- All active authenticated collaborators can consult all Events.
- Only the commercial User responsible for the related Client can create an Event.
- The related Contract must be signed.
- A newly created Event has no support contact.
- Only management can assign the support contact.
- The assigned collaborator must be active and belong to `SUPPORT`.
- Only the assigned support User can update the Event.
- Event deletion is not included because it is not required by the specifications.
- Event name and location are required.
- Attendees must be a positive integer.
- Event end must occur after event start.
- Empty notes are stored as `None`.

---

## Domain relationships

```text
+-----------------------+
| User                  |
| department=COMMERCIAL |
+-----------------------+
          │ 1
          │ manages
          ▼ *
+-----------------------+
| Client                |
| sales_contact -> User |
+-----------------------+
          │ 1
          │ owns
          ▼ *
+-------------------------+
| Contract                |
| client -> Client        |
| is_signed               |
+-------------------------+
          │ 1
          │ contains
          ▼ *
+---------------------------+
| Event                     |
| contract -> Contract      |
| support_contact -> User ? |
+---------------------------+
          ▲ *
          │ assigned to
          │ 0..1
+--------------------+
| User               |
| department=SUPPORT |
+--------------------+
```

---

## Event creation workflow

```text
Typer CLI
    │
    ▼
Authenticate active User
    │
    ▼
event_service.create_event()
    │
    ├── require COMMERCIAL
    ├── load Contract
    ├── verify Client.sales_contact == current User
    ├── verify Contract.is_signed
    ├── validate event data
    │
    ▼
Create Event
    │
    ▼
support_contact = None
```

Rejected paths:

```text
Unauthenticated / inactive / wrong department
    └── PermissionError

Unknown contract
    └── ValueError

Another commercial's client
    └── PermissionError

Unsigned contract
    └── ValueError

Invalid event data
    └── ValueError
```

---

## Read workflow

```text
Authenticated active User
    │
    ▼
require COMMERCIAL or SUPPORT or MANAGEMENT
    │
    ▼
list_all_events()
    │
    ▼
Read-only event list
```

---

## Management assignment workflow

```text
Typer CLI
    │
    ▼
Authenticate active User
    │
    ▼
assign_support_to_event()
    │
    ├── require MANAGEMENT
    ├── load Event
    ├── load selected User
    ├── verify User.is_active
    ├── verify User.department == SUPPORT
    │
    ▼
Event.support_contact = selected User
```

Management filter:

```text
Authenticated MANAGEMENT User
    │
    ▼
list_unassigned_events()
    │
    ▼
Event.support_contact IS NULL
```

---

## Support workflow

Support filter:

```text
Authenticated SUPPORT User
    │
    ▼
list_my_support_events()
    │
    ▼
Event.support_contact == current User
```

Support update:

```text
Typer CLI
    │
    ▼
Authenticate active SUPPORT User
    │
    ▼
update_event()
    │
    ├── load Event
    ├── verify Event.support_contact == current User
    ├── validate event data
    │
    ▼
Save updated Event fields
```

Support cannot:

- update an unassigned Event;
- update an Event assigned to another support User;
- assign or reassign a support contact;
- create Events;
- modify Contracts or Clients outside existing permissions.

---

## Validation workflow

```text
Event input
    │
    ├── event_name.strip() is not empty
    ├── location.strip() is not empty
    ├── attendees is int and not bool
    ├── attendees > 0
    ├── event_start is datetime
    ├── event_end is datetime
    ├── event_end > event_start
    └── empty notes -> None
    │
    ▼
Validated Event data
```

---

## Security boundaries

```text
CLI
    │ collects input and authenticates
    ▼
Service layer
    │ enforces permissions, ownership, assignment and validation
    ▼
Peewee ORM
    │ executes parameterized SQL queries
    ▼
SQLite database
```

Security properties:

- authentication is required before event access;
- inactive users receive no permission;
- role checks are centralized;
- commercial creation requires ownership;
- support updates require assignment;
- management receives only the assignment capability required by the specifications;
- unauthorized operations are rejected explicitly;
- protected lookups occur only after the relevant role check when appropriate;
- SQL queries are generated through Peewee.

---

## CLI event commands

```text
create-event-command
list-events-command
list-unassigned-events-command
list-my-events-command
assign-support-to-event-command
update-event-command
```

Dates are supplied in ISO-compatible format, for example:

```text
2026-08-20T09:00
2026-08-20 18:00
```

---

## Automated validation

The event suite covers:

- successful creation;
- empty-note normalization;
- unauthorized roles;
- unauthenticated and inactive users;
- unknown and unsigned contracts;
- client ownership;
- required text fields;
- attendee validation;
- chronological date validation;
- read access for all departments;
- unassigned-event filtering;
- assigned-support filtering;
- support assignment;
- invalid support collaborators;
- assigned-event updates;
- unassigned and differently assigned update rejection;
- authorization order;
- update-data validation.

Final result:

```text
134 passed in 131.47s
```
