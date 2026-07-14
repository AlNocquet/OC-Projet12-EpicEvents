# UML v0.6 - Contract management and authorization

## Status

Validated

## Date

2026-07-14

## Validation

- Complete suite executed with Python 3.12.2 and pytest 9.1.1.
- 96 tests collected.
- 96 tests passed.
- No regression detected in authentication, collaborator management, client management or database initialization.
- Contract tests validate creation, consultation, filters, financial validation, signature-status validation, permissions, ownership and commercial-contact synchronization.

---

## Evolution

Compared to UML v0.5:

- Added the contract service to the business-service package.
- Added contract creation by management collaborators.
- Added contract consultation by all authenticated collaborators.
- Added management and commercial contract-update rules.
- Added ownership-based authorization for commercial contract updates.
- Added commercial filters for unsigned and not fully paid contracts.
- Added monetary and signature-status validation.
- Added synchronization between the client's commercial contact and the contract's commercial contact.
- Preserved every previously implemented authentication, collaborator and client workflow.

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
    └── contract_service.py
```

Responsibilities:

- `main.py` defines CLI commands, collects terminal input and displays results.
- `auth.py` authenticates users and applies reusable role-based authorization checks.
- `user_service.py` contains collaborator business rules.
- `client_service.py` contains client business rules.
- `contract_service.py` contains contract business rules, financial validation and contract authorization.
- `models/` defines the Peewee entities and their relationships.

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
- One commercial User can be associated with several Contracts.
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
- is_signed
- created_at

Relationships:

- One Contract belongs to one Client.
- One Contract is associated with the commercial User responsible for its Client.
- One Contract can have several Events.

Business rules:

- Only an active management User can create a Contract.
- `Contract.sales_contact` is automatically derived from `Client.sales_contact`.
- Every active collaborator can consult all Contracts in read-only mode.
- An active management User can update every Contract.
- An active commercial User can update a Contract only when the related Client is assigned to them.
- Commercial Users can filter all unsigned Contracts.
- Commercial Users can filter all Contracts with an `amount_due` greater than zero.
- The total amount must be greater than zero.
- The amount due cannot be negative.
- The amount due cannot exceed the total amount.
- Monetary values must be finite `Decimal` values.
- The signature status must be Boolean.
- Contract deletion is not included because it is not required by the specifications.

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
+-----------------------+
| User                  |
| department=COMMERCIAL |
+-----------------------+
          │ 1
          │
          │ manages
          ▼ *
+-----------------------+
| Client                |
| sales_contact -> User |
+-----------------------+
          │ 1
          │
          │ owns
          ▼ *
+-------------------------+
| Contract                |
| client -> Client        |
| sales_contact -> User   |
+-------------------------+
          │ 1
          │
          │ contains
          ▼ *
+---------------------------+
| Event                     |
| contract -> Contract      |
| support_contact -> User ? |
+---------------------------+
          ▲ *
          │ assigned to
          │ 1
+--------------------+
| User               |
| department=SUPPORT |
+--------------------+
```

The `Contract.sales_contact` value mirrors the commercial User assigned to `Client.sales_contact`.

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

## Contract creation workflow

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
Load Client by identifier
    │
    ├── not found
    │     ▼
    │ ValueError
    │
    ▼
Validate:
- total_amount
- amount_due
- is_signed
    │
    ▼
create_contract()
    │
    ▼
Contract.client = selected Client
Contract.sales_contact = Client.sales_contact
```

---

## Contract consultation workflow

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
list_all_contracts()
    │
    ▼
Read-only contract list
```

---

## Commercial contract-filter workflow

```text
Authenticated active User
    │
    ▼
require_permission("COMMERCIAL")
    │
    ├── denied
    │     ▼
    │ PermissionError
    │
    ├── list_unsigned_contracts()
    │       ▼
    │   Contract.is_signed = False
    │
    └── list_unpaid_contracts()
            ▼
        Contract.amount_due > 0
```

The filters apply to all contracts. They do not grant update permission over contracts belonging to other commercial collaborators' clients.

---

## Contract update workflow

```text
Authenticated active User
    │
    ▼
require_permission(
    "MANAGEMENT",
    "COMMERCIAL"
)
    │
    ├── denied
    │     ▼
    │ PermissionError
    │
    ▼
Load Contract by identifier
    │
    ├── not found
    │     ▼
    │ ValueError
    │
    ▼
Is current User MANAGEMENT?
    │
    ├── yes
    │     ▼
    │ Authorized
    │
    └── no
          │
          ▼
Is current User COMMERCIAL
and Contract.client.sales_contact_id == current_user.id?
          │
          ├── no
          │     ▼
          │ PermissionError
          │
          └── yes
                ▼
            Authorized
                │
                ▼
Validate:
- total_amount
- amount_due
- is_signed
                │
                ▼
Synchronize:
Contract.sales_contact = Contract.client.sales_contact
                │
                ▼
update_contract()
```

---

## Contract financial-validation workflow

```text
Raw monetary input
    │
    ▼
Decimal(str(value))
    │
    ├── invalid / infinite / NaN
    │       ▼
    │   ValueError
    │
    ▼
total_amount > 0
    │
    ├── false
    │     ▼
    │ ValueError
    │
    ▼
amount_due >= 0
    │
    ├── false
    │     ▼
    │ ValueError
    │
    ▼
amount_due <= total_amount
    │
    ├── false
    │     ▼
    │ ValueError
    │
    ▼
Validated Decimal values
```

---

## Security controls currently implemented

- Passwords are hashed with Passlib and bcrypt.
- Password input is hidden in the CLI.
- Inactive users cannot authenticate.
- Inactive users cannot obtain permissions.
- Authorization depends on the collaborator's department.
- Client ownership is checked before a client update.
- Contract ownership is checked before a commercial contract update.
- Unauthorized departments are rejected before contract lookup during updates.
- Contract monetary values are normalized and validated before persistence.
- The contract signature status is explicitly validated.
- Peewee parameterized queries limit SQL injection risks.
- Business rules are enforced inside services rather than only in CLI commands.

---

## Current implementation status

Implemented:

- authentication;
- collaborator creation, update and deactivation;
- client creation, consultation and update;
- contract creation, consultation, filtering and update;
- role-based authorization;
- client and contract ownership authorization.

Not yet implemented:

- event service and event CLI commands;
- support assignment to events;
- Sentry integration;
- final unit, integration and functional test organization;
- final coverage report;
- consolidated final architecture document.
