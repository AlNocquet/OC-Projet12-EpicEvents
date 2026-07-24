# UML v1.0 – Application package and CLI architecture

## Status

Validated

## Date

2026-07-24

## Evolution from UML v0.9

UML v0.9 documented the organization of the automated test suite and the production architecture that existed at that time.

UML v1.0 documents the later refactoring of the production application into:

- a package entry point;
- domain-oriented CLI modules;
- a shared CLI helper module;
- a technical `core` package;
- service and model layers;
- independent setup utilities.

The domain entities and database relationships remain unchanged.

## Current source structure

```text
src/
├── __init__.py
├── __main__.py
│
├── cli/
│   ├── __init__.py
│   ├── auth.py
│   ├── client.py
│   ├── common.py
│   ├── contract.py
│   ├── event.py
│   ├── monitoring.py
│   └── user.py
│
├── core/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   └── monitoring.py
│
├── models/
│   ├── client.py
│   ├── contract.py
│   ├── event.py
│   └── user.py
│
├── services/
│   ├── client_service.py
│   ├── contract_service.py
│   ├── event_service.py
│   └── user_service.py
│
└── utils/
    ├── __init__.py
    ├── create_db.py
    └── create_user.py
```

## High-level application flow

```text
┌─────────────────────────────────────┐
│           PowerShell user           │
│                                     │
│           python -m src             │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│          src/__main__.py            │
│                                     │
│ - root Typer application            │
│ - app.add_typer registrations       │
│ - Sentry initialization             │
│ - global exception handling         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            src/cli/                 │
│                                     │
│ auth | user | client | contract     │
│ event | monitoring                  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│          src/services/              │
│                                     │
│ business rules                      │
│ role-based authorization            │
│ validation                          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           src/models/               │
│                                     │
│ User | Client | Contract | Event    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│              SQLite                 │
│          epic_events.db             │
└─────────────────────────────────────┘
```

## Root application composition

```text
src/__main__.py
        │
        ├── app.add_typer(auth_cli.app, name="auth")
        ├── app.add_typer(user_cli.app, name="user")
        ├── app.add_typer(client_cli.app, name="client")
        ├── app.add_typer(contract_cli.app, name="contract")
        ├── app.add_typer(event_cli.app, name="event")
        └── app.add_typer(monitoring_cli.app, name="monitoring")
```

Visible root commands:

```text
auth
user
client
contract
event
monitoring
```

## CLI command groups

### Authentication

```text
auth
├── login
└── check-management
```

Current flow before JWT implementation:

```text
auth login EMAIL
        │
        ▼
src/cli/common.py
        │
        ├── prompt password
        └── authenticate_current_user()
        │
        ▼
src/core/auth.py
        │
        └── authenticate_user()
        │
        ▼
User model
```

### Collaborators

```text
user
├── create
├── update
└── delete
```

Flow:

```text
src/cli/user.py
        │
        ▼
src/services/user_service.py
        │
        ▼
src/models/user.py
```

### Clients

```text
client
├── create
├── list
└── update
```

Flow:

```text
src/cli/client.py
        │
        ▼
src/services/client_service.py
        │
        ▼
src/models/client.py
```

### Contracts

```text
contract
├── create
├── list
├── list-unsigned
├── list-unpaid
└── update
```

Flow:

```text
src/cli/contract.py
        │
        ▼
src/services/contract_service.py
        │
        ▼
src/models/contract.py
```

### Events

```text
event
├── create
├── list
├── list-unassigned
├── list-mine
├── assign-support
└── update
```

Flow:

```text
src/cli/event.py
        │
        ▼
src/services/event_service.py
        │
        ▼
src/models/event.py
```

### Monitoring

```text
monitoring
└── test-sentry
```

Flow:

```text
src/cli/monitoring.py
        │
        ├── authentication
        ├── management authorization
        └── monitoring command
        │
        ▼
src/core/monitoring.py
        │
        ▼
Sentry SDK
```

## Shared CLI authentication flow

```text
Domain CLI command
        │
        ▼
src/cli/common.py
        │
        ├── prompt_password()
        └── authenticate_current_user()
        │
        ▼
src/core/auth.py
        │
        ├── authenticate_user()
        ├── has_required_permission()
        └── require_permission()
        │
        ▼
src/models/user.py
        │
        ▼
SQLite
```

`src/cli/common.py` centralizes CLI interaction.

`src/core/auth.py` centralizes authentication and authorization logic.

Service-layer functions remain responsible for enforcing permissions on business operations.

## Core package architecture

```text
src/core/
    │
    ├── auth.py
    │      ├── credential verification
    │      ├── active-user verification
    │      └── department permissions
    │
    ├── config.py
    │      ├── project base directory
    │      ├── SQLite path
    │      └── Sentry environment configuration
    │
    ├── database.py
    │      ├── shared SqliteDatabase
    │      └── foreign-key pragma
    │
    └── monitoring.py
           ├── initialize_sentry()
           ├── capture_application_exception()
           └── send_test_exception()
```

## Service-layer authorization boundary

```text
CLI authentication
        │
        ▼
Current active User
        │
        ▼
Service function
        │
        ├── require_permission()
        ├── ownership checks
        ├── business validation
        └── database operation
```

Examples:

```text
user_service
    management-only collaborator administration

client_service
    commercial creation and ownership-based updates

contract_service
    management creation
    management or owning-commercial updates

event_service
    commercial event creation
    management support assignment
    assigned-support event updates
```

The CLI does not replace these checks.

## Domain model relationships

```text
User
│
├── 1 ─────── * Client
│              via Client.sales_contact
│
├── 1 ─────── * Contract
│              via Contract.sales_contact
│
└── 1 ─────── * Event
               via Event.support_contact
               nullable
```

```text
Client
│
└── 1 ─────── * Contract
               via Contract.client
```

```text
Contract
│
└── 1 ─────── * Event
               via Event.contract
```

Complete relationship flow:

```text
User (commercial)
        │
        ▼
Client
        │
        ▼
Contract
        │
        ▼
Event
        ▲
        │
User (support, optional assignment)
```

## Database configuration flow

```text
src/core/config.py
        │
        └── DATABASE_PATH
                │
                ▼
src/core/database.py
        │
        └── SqliteDatabase
                │
                ▼
User / Client / Contract / Event models
```

Foreign-key enforcement:

```text
PRAGMA foreign_keys = 1
```

## Utility-script architecture

Utility scripts do not pass through the regular CRM command groups.

### Database creation

```text
python -m src.utils.create_db
        │
        ▼
src/utils/create_db.py
        │
        ├── shared database connection
        └── safe table creation
        │
        ▼
User / Client / Contract / Event tables
```

### Initial management user

```text
python -m src.utils.create_user FULL_NAME EMAIL
        │
        ▼
src/utils/create_user.py
        │
        ├── hidden password prompt
        └── create_initial_management_user()
        │
        ▼
src/services/user_service.py
        │
        ▼
User model
```

The initial-user service rejects creation when a collaborator already exists.

## Monitoring and exception flow

```text
python -m src
        │
        ▼
initialize_sentry()
        │
        ▼
Typer application
        │
        ├── expected ValueError / PermissionError
        │       handled by CLI commands
        │
        └── unexpected Exception
                │
                ▼
capture_application_exception()
                │
                ▼
Sentry
```

## Test architecture after the refactoring

```text
tests/
├── conftest.py
├── unit/
│   └── test_monitoring.py
├── integration/
│   ├── test_auth.py
│   ├── test_client_service.py
│   ├── test_contract_service.py
│   ├── test_database.py
│   ├── test_event_service.py
│   └── test_user_service.py
└── functional/
    └── test_cli.py
```

Updated functional-test flow:

```text
tests/functional/test_cli.py
        │
        ▼
Typer CliRunner
        │
        ▼
src.__main__.app
        │
        ▼
grouped CLI command
        │
        ▼
service / model / in-memory SQLite
```

Updated monitoring unit-test flow:

```text
tests/unit/test_monitoring.py
        │
        ▼
src.core.monitoring
        │
        ├── mocked Sentry initialization
        ├── mocked exception capture
        └── mocked flush
```

## Validated execution matrix

```text
+-----------------------------------------------+----------------------------------+
| Command                                       | Purpose                          |
+-----------------------------------------------+----------------------------------+
| python -m src --help                          | Root CLI discovery               |
| python -m src auth --help                     | Authentication commands          |
| python -m src user --help                     | Collaborator commands            |
| python -m src client --help                   | Client commands                  |
| python -m src contract --help                 | Contract commands                |
| python -m src event --help                    | Event commands                   |
| python -m src monitoring --help               | Monitoring commands              |
| python -m src.utils.create_db --help          | Database setup script            |
| python -m src.utils.create_user --help        | Initial-user setup script        |
| python -m pytest                              | Complete regression suite        |
+-----------------------------------------------+----------------------------------+
```

## Validated results

```text
Complete suite: 147 passed
Failures:          0
```

## Change boundary

```text
Modified by UML v1.0:
    documented application package architecture
    documented grouped CLI
    documented core package
    documented utility scripts
    updated module paths
    updated functional and unit test flows

Not modified by this refactoring:
    database schema
    domain relationships
    service-layer business rules
    role permissions
    password hashing
    Sentry behavior
    test count
```

## Next evolution

UML v1.1 will document JWT authentication and local token storage.

Expected future flow:

```text
auth login
        │
        ▼
credential verification
        │
        ▼
JWT generation
        │
        ▼
local JSON token storage
        │
        ▼
subsequent CLI command
        │
        ▼
token validation
        │
        ▼
current user loaded from SQLite
        │
        ▼
service-layer authorization
```

## Final conclusion

The production architecture now separates:

```text
application startup
        +
CLI interaction
        +
cross-cutting technical concerns
        +
business services
        +
domain models
        +
setup utilities
```

The complete automated test suite remains green after the refactoring.
