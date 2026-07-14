# UML v0.5 - Client management and service organization

## Status

Work in progress

## Date

2026-07-14

## Evolution

Compared to UML v0.4:

- Added complete collaborator management workflows.
- Added client creation, consultation and update workflows.
- Added the `services` package for business services.
- Kept authentication and authorization in the transversal `auth.py` module.
- Added ownership-based authorization for client updates.
- Added account deactivation for collaborator deletion.

---

## Project structure

```text
src/
├── auth.py
├── config.py
├── database.py
├── main.py
├── models/
│   ├── user.py
│   ├── client.py
│   ├── contract.py
│   └── event.py
└── services/
    ├── __init__.py
    ├── user_service.py
    └── client_service.py
```

Responsibilities:

- `main.py` defines CLI commands, collects input and displays results.
- `auth.py` authenticates users and applies reusable authorization checks.
- `user_service.py` contains collaborator business rules.
- `client_service.py` contains client business rules.
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

- One commercial User can manage several Clients.
- One commercial User can manage several Contracts.
- One support User can be assigned to several Events.

Business rules:

- Only an active management User can create, update or deactivate collaborators.
- A management User cannot remove their own management role.
- A management User cannot deactivate their own account.
- A deactivated User cannot authenticate or obtain permissions.

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

Business rules:

- Only an active commercial User can create a Client.
- The authenticated commercial User is automatically assigned as `sales_contact`.
- Every active collaborator can consult all Clients in read-only mode.
- Only the commercial User assigned to a Client can update it.
- Client deletion is not included because it is not required by the specifications.

---

### Contract

Attributes:

- id
- client -> Client
- sales_contact -> User
- total_amount
- amount_due
- created_at
- is_signed

Relationships:

- One Contract belongs to one Client.
- One Contract belongs to one commercial User.
- One Contract can have several Events.

Status:

- Domain model created.
- Business service not implemented yet.

---

### Event

Attributes:

- id
- contract -> Contract
- support_contact -> User
- event_name
- location
- attendees
- event_start
- event_end
- notes

Relationships:

- One Event belongs to one Contract.
- One Event can be assigned to one support User.

Status:

- Domain model created.
- Business service not implemented yet.

---

## Current domain relationships

```text
User (Commercial)
        │
        ├───────────────┐
        ▼               ▼
+---------------+  +---------------+
|    Client     |  |   Contract    |
+---------------+  +---------------+
        │               │
        └───────┬───────┘
                ▼
        +---------------+
        |     Event     |
        +---------------+
                ▲
                │
        User (Support)
```

---

## Authentication workflow

```text
CLI command
    │
    ▼
Secure password prompt
    │
    ▼
authenticate_user()
    │
    ├── invalid credentials / inactive account
    │       ▼
    │   Access denied
    │
    ▼
Authenticated active User
```

---

## Collaborator management workflow

```text
Authenticated active User
    │
    ▼
require_permission("MANAGEMENT")
    │
    ├── denied
    │     ▼
    │ PermissionError
    │
    ▼
user_service
    │
    ├── create_user()
    ├── update_user()
    └── delete_user()
            │
            ▼
     is_active = False
```

The deletion workflow uses deactivation instead of physical deletion so that related CRM records remain consistent.

---

## Client creation workflow

```text
Authenticated active User
    │
    ▼
require_permission("COMMERCIAL")
    │
    ▼
_validate_client_data()
    │
    ▼
create_client()
    │
    ▼
Client.sales_contact = current_user
```

---

## Client consultation workflow

```text
Authenticated active User
    │
    ▼
require_permission(
    "COMMERCIAL",
    "SUPPORT",
    "MANAGEMENT"
)
    │
    ▼
list_all_clients()
    │
    ▼
Read-only client list
```

---

## Client update workflow

```text
Authenticated active User
    │
    ▼
require_permission("COMMERCIAL")
    │
    ▼
Load Client by identifier
    │
    ▼
Client.sales_contact_id == current_user.id
    │
    ├── false
    │     ▼
    │ PermissionError
    │
    ▼
_validate_client_data()
    │
    ▼
update_client()
```

---

## Security controls currently implemented

- Passwords are hashed with Passlib and bcrypt.
- Password input is hidden in the CLI.
- Inactive users cannot authenticate.
- Authorization depends on the collaborator's department.
- Ownership is checked before a client update.
- Peewee parameterized queries limit SQL injection risks.
- User and client input is normalized and validated before persistence.
