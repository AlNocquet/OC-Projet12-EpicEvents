# Epic Events CRM

## Overview

Epic Events is a secure command-line CRM application built with Python.

It allows the **management**, **sales**, and **support** departments to manage collaborators, clients, contracts, and events according to precise permissions.

The project implements:

- a relational SQLite database;
- the Peewee ORM;
- a Typer command-line interface;
- passwords hashed with bcrypt;
- JWT session authentication;
- authorization based on role, ownership, and assignment;
- the principle of least privilege;
- error monitoring with Sentry;
- unit, integration, and functional tests.

---

## Features

### Collaborators

- Create the initial management account
- Log in with an email address and password
- Create a local JWT session after authentication
- Log out and remove the local session
- Create collaborator accounts
- Update collaborators
- Logically deactivate accounts while preserving related CRM records
- Assign a department:
  - `MANAGEMENT`
  - `COMMERCIAL`
  - `SUPPORT`
- Protect the authenticated management account:
  - it cannot deactivate itself;
  - it cannot remove its own `MANAGEMENT` department

### Clients

- Create clients as a sales collaborator
- Automatically assign each client to the authenticated sales collaborator
- Allow all active collaborators to read client information
- Allow only the responsible sales collaborator to update a client
- Preserve clients when a collaborator is deactivated

### Contracts

- Create contracts as a management collaborator
- Automatically associate contracts with the client and the client’s responsible sales collaborator
- Allow all active collaborators to read contracts
- Allow updates:
  - by management for every contract;
  - by sales collaborators for contracts linked to their own clients
- Filter contracts:
  - unsigned;
  - not fully paid
- Validate total and remaining amounts

### Events

- Create events as the sales collaborator responsible for the client
- Allow creation only for signed contracts
- Allow all active collaborators to read events
- List events without an assigned support collaborator
- Assign an active support collaborator as management
- List events assigned to the authenticated support collaborator
- Allow only the assigned support collaborator to update an event
- Validate dates, attendee counts, and required fields

### Security and monitoring

- Password hashing with Passlib and bcrypt
- Hidden password prompts
- JWT signed with HS256
- JWT expiration after 60 minutes
- Local session stored in `.epic_events_token.json`
- User reloaded from SQLite for every protected command
- Immediate rejection of deleted or inactive users, even with a technically valid JWT
- Service-layer permission enforcement
- Parameterized queries through Peewee
- Input validation before persistence
- Secrets, local database, and token excluded from Git
- Unexpected exception monitoring with Sentry

---

## Architecture

The application follows a layered architecture.

```text
User
    |
    v
python -m src
    |
    v
src/__main__.py
    |
    +--> src/cli/
    |      auth.py
    |      user.py
    |      client.py
    |      contract.py
    |      event.py
    |      monitoring.py
    |      common.py
    |
    +--> src/core/
    |      auth.py
    |      jwt_auth.py
    |      config.py
    |      database.py
    |      monitoring.py
    |
    +--> src/services/
    |      user_service.py
    |      client_service.py
    |      contract_service.py
    |      event_service.py
    |
    +--> src/models/
           user.py
           client.py
           contract.py
           event.py
               |
               v
          SQLite / epic_events.db
```

### Layer responsibilities

| Layer | Responsibility |
|---|---|
| `src/__main__.py` | Composes the Typer application, initializes Sentry, and catches unexpected errors |
| `src/cli/` | Collects arguments, displays results, and converts expected errors into CLI output |
| `src/core/auth.py` | Verifies email, bcrypt password, and authorized departments |
| `src/core/jwt_auth.py` | Creates, signs, validates, loads, stores, and deletes JWTs |
| `src/core/config.py` | Centralizes paths and environment-based configuration |
| `src/services/` | Enforces business rules, permissions, ownership, and assignment |
| `src/models/` | Defines Peewee entities and relationships |
| SQLite | Stores collaborators, clients, contracts, and events |
| Sentry | Receives unexpected exceptions and the controlled demonstration exception |

### JWT authentication flow

```text
auth login EMAIL
    |
    +--> password entered through a hidden prompt
    +--> bcrypt verification against SQLite
    +--> creation of an HS256-signed JWT
    +--> 60-minute expiration
    +--> storage in .epic_events_token.json
```

For every protected command:

```text
CLI command
    |
    +--> load the local token
    +--> validate signature and expiration
    +--> read the user identifier from the sub claim
    +--> reload the user from SQLite
    +--> confirm that the account exists and is active
    +--> enforce final authorization in the service layer
```

The department claim is not treated as the source of authorization. SQLite and the service layer remain the sources of truth.

---

## Project structure

```text
OC-Projet12-EpicEvents/
├── .env.example
├── .gitignore
├── README.md
├── README_EN.md
├── requirements.txt
├── docs/
│   ├── architecture/
│   ├── decisions/
│   │   ├── ADR-007-test-suite-organization.md
│   │   ├── ADR-008-cli-application-package-reorganization.md
│   │   └── ADR-009-jwt-authentication-and-local-session.md
│   ├── journal/
│   │   ├── Day-07.md
│   │   ├── Day-08.md
│   │   └── Day-09.md
│   └── uml/
│       ├── UML-v0.9.md
│       ├── UML-v1.0.md
│       └── UML-v1.1.md
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── common.py
│   │   ├── contract.py
│   │   ├── event.py
│   │   ├── monitoring.py
│   │   └── user.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── jwt_auth.py
│   │   └── monitoring.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── event.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── client_service.py
│   │   ├── contract_service.py
│   │   ├── event_service.py
│   │   └── user_service.py
│   └── utils/
│       ├── __init__.py
│       ├── create_db.py
│       └── create_user.py
└── tests/
    ├── conftest.py
    ├── functional/
    │   └── test_cli.py
    ├── integration/
    │   ├── test_auth.py
    │   ├── test_client_service.py
    │   ├── test_contract_service.py
    │   ├── test_database.py
    │   ├── test_event_service.py
    │   ├── test_jwt_auth.py
    │   └── test_user_service.py
    └── unit/
        └── test_monitoring.py
```

Historical journal or UML filenames may differ slightly in the repository. The latest versions are Day 09, ADR-009, and UML v1.1.

---

## Requirements

- Python 3.9 or later
- Git
- PowerShell, a macOS/Linux shell, or another compatible terminal
- An optional Sentry account for the monitoring demonstration

Development version:

```text
Python 3.12.2
```

---

## Clean environment installation

### 1. Clone the repository

```powershell
git clone https://github.com/AlNocquet/OC-Projet12-EpicEvents.git
cd OC-Projet12-EpicEvents
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

PowerShell on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
venv\Scripts\activate.bat
```

macOS or Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Create the `.env` file

PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

Generate a random JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into `.env`:

```text
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
JWT_SECRET_KEY=PASTE_THE_GENERATED_SECRET_HERE
```

Important rules:

- never publish the real `JWT_SECRET_KEY`;
- never publish a real `SENTRY_DSN`;
- never add `.env` to Git;
- use a long, random JWT secret.

Sentry is optional. The application works with an empty `SENTRY_DSN`, but the Sentry demonstration command requires a valid DSN.

### 6. Create the database

```powershell
python -m src.utils.create_db
```

Expected result:

```text
Database initialized successfully.
```

### 7. Create the initial management account

This command works only when the database does not contain any collaborator.

```powershell
python -m src.utils.create_user "Morgan Manager" manager@epicevents.com
```

The password is requested and confirmed through a hidden prompt.

Expected result:

```text
Initial management user created successfully. User ID: 1.
```

### 8. Verify the installation

```powershell
python -m src --help
```

The following groups must be displayed:

```text
auth
user
client
contract
event
monitoring
```

---

## Usage

### General workflow

1. Log in once with `auth login`.
2. Run business commands without entering the email address and password again.
3. Log out with `auth logout`.

The session expires automatically after 60 minutes.

### Display help

```powershell
python -m src --help
python -m src auth --help
python -m src user --help
python -m src client --help
python -m src contract --help
python -m src event --help
python -m src monitoring --help
```

Display help for a specific command:

```powershell
python -m src client create --help
```

---

## JWT authentication

### Log in

```powershell
python -m src auth login manager@epicevents.com
```

The password is requested through a hidden prompt.

A successful login creates the following local file:

```text
.epic_events_token.json
```

This file contains an access token, not the password.

### Check management access

```powershell
python -m src auth check-management
```

### Log out

```powershell
python -m src auth logout
```

Logging out removes the local session file.

### Protected command without a session

When no token is available, the application responds with:

```text
No authentication token found. Please log in.
```

---

## Collaborator management

Required session: `MANAGEMENT` collaborator.

### Create a collaborator

```powershell
python -m src user create "Camille Martin" camille@epicevents.com COMMERCIAL
```

The new password is requested and confirmed through a hidden prompt.

### Update a collaborator

```powershell
python -m src user update 2 "Camille Dupont" camille.dupont@epicevents.com COMMERCIAL
```

### Deactivate a collaborator

```powershell
python -m src user delete 2
```

Deletion is logical: the account becomes inactive, while its clients, contracts, and events remain in the CRM.

---

## Client management

### Create a client

Required session: `COMMERCIAL` collaborator.

```powershell
python -m src client create "Kevin Casey" kevin@startup.io "+33 6 12 34 56 78" "Cool Startup LLC"
```

The client is automatically assigned to the authenticated sales collaborator.

### List clients

Required session: any active collaborator.

```powershell
python -m src client list
```

### Update a client

Required session: sales collaborator responsible for the client.

```powershell
python -m src client update 1 "Kevin Casey" kevin@startup.io "+33 6 98 76 54 32" "Cool Startup LLC"
```

---

## Contract management

### Create a contract

Required session: `MANAGEMENT` collaborator.

```powershell
python -m src contract create 1 10000.00 4000.00 true
```

Argument order:

```text
CLIENT_ID TOTAL_AMOUNT AMOUNT_DUE IS_SIGNED
```

### List contracts

Required session: any active collaborator.

```powershell
python -m src contract list
```

### List unsigned contracts

Required session: `COMMERCIAL` collaborator.

```powershell
python -m src contract list-unsigned
```

### List contracts that are not fully paid

Required session: `COMMERCIAL` collaborator.

```powershell
python -m src contract list-unpaid
```

### Update a contract

Required session:

- management for every contract;
- sales for contracts linked to their own clients.

```powershell
python -m src contract update 1 10000.00 0.00 true
```

Argument order:

```text
CONTRACT_ID TOTAL_AMOUNT AMOUNT_DUE IS_SIGNED
```

---

## Event management

Dates use the following ISO format:

```text
YYYY-MM-DDTHH:MM
```

### Create an event

Required session: sales collaborator responsible for the client linked to a signed contract.

```powershell
python -m src event create 1 "Annual conference" "Paris" 100 "2026-09-10T14:00" "2026-09-10T18:00" "Reception starts at 1:30 PM."
```

Argument order:

```text
CONTRACT_ID EVENT_NAME LOCATION ATTENDEES EVENT_START EVENT_END [NOTES]
```

### List all events

Required session: any active collaborator.

```powershell
python -m src event list
```

### List events without support

Required session: `MANAGEMENT` collaborator.

```powershell
python -m src event list-unassigned
```

### Assign support to an event

Required session: `MANAGEMENT` collaborator.

```powershell
python -m src event assign-support 1 3
```

Argument order:

```text
EVENT_ID SUPPORT_USER_ID
```

### List events assigned to the authenticated support collaborator

Required session: `SUPPORT` collaborator.

```powershell
python -m src event list-mine
```

### Update an assigned event

Required session: support collaborator assigned to the event.

```powershell
python -m src event update 1 "Annual conference" "Paris - Horizon Room" 110 "2026-09-10T14:00" "2026-09-10T18:30" "Reception starts at 1:30 PM and equipment must be checked."
```

Argument order:

```text
EVENT_ID EVENT_NAME LOCATION ATTENDEES EVENT_START EVENT_END [NOTES]
```

---

## Permissions

| Action | Management | Sales | Support |
|---|:---:|:---:|:---:|
| Read clients, contracts, and events | Yes | Yes | Yes |
| Create, update, or deactivate a collaborator | Yes | No | No |
| Deactivate own account | No | No | No |
| Create a client | No | Yes | No |
| Update a client | No | Own clients | No |
| Create a contract | Yes | No | No |
| Update a contract | All | Own-client contracts | No |
| Filter unsigned or unpaid contracts | No | Yes | No |
| Create an event | No | Own client and signed contract | No |
| View unassigned events | Yes | No | No |
| Assign support | Yes | No | No |
| View assigned events | No | No | Yes |
| Update an event | No | No | Assigned events |
| Send the controlled Sentry exception | Yes | No | No |

---

## Sentry configuration and demonstration

No real DSN must be committed to the repository.

Variables in `.env`:

```text
SENTRY_DSN
SENTRY_ENVIRONMENT
```

Example:

```text
SENTRY_DSN=YOUR_SENTRY_DSN
SENTRY_ENVIRONMENT=development
JWT_SECRET_KEY=YOUR_JWT_SECRET
```

After adding a valid DSN and logging in as a management collaborator:

```powershell
python -m src monitoring test-sentry
```

Controlled exception:

```text
Epic Events controlled Sentry demonstration error.
```

Expected CLI output:

```text
Sentry test exception sent successfully. Event ID: <event-id>.
```

When no DSN is configured:

```text
Sentry is not configured. Set the SENTRY_DSN environment variable.
```

---

## Tests

The suite is organized into three categories.

### Unit tests

```powershell
python -m pytest tests/unit -v
```

Validated result:

```text
4 tests passed
```

### Integration tests

```powershell
python -m pytest tests/integration -v
```

Validated result:

```text
143 tests passed
```

These tests cover the business services, authentication, database, and JWT engine.

### Functional tests

```powershell
python -m pytest tests/functional -v
```

Validated result:

```text
9 tests passed
```

### Complete suite

```powershell
python -m pytest -q
```

Validated result:

```text
156 tests passed
0 failures
```

---

## Coverage

Generate the terminal coverage report:

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

Also generate the HTML report:

```powershell
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

Validated result:

```text
TOTAL 77%
src/core/jwt_auth.py 96%
Coverage HTML written to dir htmlcov
```

The HTML report is available at:

```text
htmlcov/index.html
```

---

## Security

- Passwords hashed and salted with bcrypt
- Passwords entered through hidden prompts
- JWT signed with HS256
- JWT secret read from the environment
- JWT expiration after 60 minutes
- Token stored locally without a password
- User reloaded from SQLite for every protected command
- Missing or inactive accounts rejected
- Permissions enforced by role, ownership, or assignment
- Principle of least privilege
- Validation of amounts, dates, emails, identifiers, and required fields
- Peewee parameterized queries against SQL injection
- Logical collaborator deactivation
- Relationships protected by SQLite foreign-key constraints
- `.env`, `.epic_events_token.json`, local database, and generated reports excluded from Git
- Personal data disabled by default in Sentry
- Tests executed against an isolated in-memory SQLite database
- Test secrets and token files isolated in temporary directories

---

## Local files that must never be published

```text
.env
.epic_events_token.json
epic_events.db
.coverage
htmlcov/
```

Recommended verification before committing:

```powershell
git status --short
git ls-files .env .epic_events_token.json epic_events.db
```

The second command must not return any file.

---

## Clean installation: final verification

Validate the project as a new user by following this sequence:

```text
clone the repository
→ create and activate the virtual environment
→ install requirements.txt
→ copy .env.example to .env
→ generate JWT_SECRET_KEY
→ create the database tables
→ create the initial management account
→ run python -m src --help
→ log in with auth login
→ run a protected command
→ log out with auth logout
→ run the test suite
```

---

## Documentation

Current documentation:

- `docs/journal/Day-09.md`
- `docs/decisions/ADR-009-jwt-authentication-and-local-session.md`
- `docs/uml/UML-v1.1.md`

Architecture and historical documents:

- `docs/architecture/`
- `docs/decisions/`
- `docs/journal/`
- `docs/uml/`

ADRs explain technical decisions. Journals record project progress. UML versions document the evolution of the architecture and authentication flow.

---

## Author

Alice Nocquet
