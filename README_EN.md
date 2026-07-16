# Epic Events CRM

---

## Overview

Epic Events is a secure command-line CRM application built with Python.

It allows the **management**, **sales**, and **support** departments to manage collaborators, clients, contracts, and events according to precise access permissions.

The project implements:

- a relational SQLite database;
- the Peewee ORM;
- a Typer command-line interface;
- secure authentication;
- role-based authorization;
- the principle of least privilege;
- error monitoring with Sentry;
- unit, integration, and functional tests.

---

## Features

### Collaborators

- Create the initial management account
- Authenticate with email and password
- Create collaborator accounts
- Update collaborators
- Logically deactivate accounts
- Assign a department:
  - `MANAGEMENT`
  - `COMMERCIAL`
  - `SUPPORT`

### Clients

- Create a client as a sales collaborator
- Automatically assign the client to the authenticated sales collaborator
- Allow all active collaborators to read client information
- Allow only the responsible sales collaborator to update a client

### Contracts

- Create contracts as a management collaborator
- Associate contracts with clients and their sales contacts
- Allow all active collaborators to read contracts
- Allow updates:
  - by management for every contract;
  - by sales collaborators for contracts linked to their own clients
- Filter contracts:
  - unsigned;
  - not fully paid

### Events

- Create an event as the responsible sales collaborator
- Allow creation only for a signed contract
- Allow all active collaborators to read events
- List events without an assigned support collaborator
- Assign a support collaborator as management
- List events assigned to the authenticated support collaborator
- Allow only the assigned support collaborator to update an event

### Security and monitoring

- Password hashing with Passlib and bcrypt
- Hidden password prompts
- Service-layer permissions
- Parameterized queries through Peewee
- Input validation before persistence
- Sensitive variables excluded from Git
- Unexpected exception monitoring with Sentry

---

## Architecture

The application follows a layered architecture:

```text
User
    |
    v
Typer CLI
src/main.py
    |
    +--> Authentication and authorization
    |    src/auth.py
    |
    +--> Business services
         src/services/
              |
              v
         Peewee models
         src/models/
              |
              v
         SQLite database

Unexpected exceptions
    |
    v
src/monitoring.py
    |
    v
Sentry
```

The relationship diagram is available at:

```text
docs/architecture/diagramme-des-relations.png
```

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
│   │   ├── architecture-summary-fr.md
│   │   ├── architecture-summary-en.md
│   │   ├── EpicEvents-architecture-technique.pdf
│   │   └── diagramme-des-relations.png
│   ├── decisions/
│   ├── journal/
│   └── uml/
├── src/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── monitoring.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   └── event.py
│   └── services/
│       ├── __init__.py
│       ├── user_service.py
│       ├── client_service.py
│       ├── contract_service.py
│       └── event_service.py
└── tests/
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

---

## Requirements

- Python 3.9 or later
- Git
- A compatible terminal
- An optional Sentry account for the monitoring demonstration

Development version:

```text
Python 3.12.2
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/AlNocquet/OC-Projet12-EpicEvents.git
cd OC-Projet12-EpicEvents
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Git Bash on Windows:

```bash
source venv/Scripts/activate
```

PowerShell on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Database initialization

Create the tables:

```bash
python -m src.main initialize-database
```

Expected result:

```text
Database initialized successfully.
```

Create the initial management account:

```bash
python -m src.main create-initial-management-user-command \
  "Morgan Manager" \
  manager@epicevents.com
```

The password is requested and confirmed through a hidden prompt.

---

## Usage

Display all available commands:

```bash
python -m src.main --help
```

Display command-specific help:

```bash
python -m src.main create-client-command --help
```

### Authentication

```bash
python -m src.main authenticate-user-command manager@epicevents.com
```

### Collaborator management

Create a collaborator:

```bash
python -m src.main create-user-account-command \
  manager@epicevents.com \
  "Camille Martin" \
  camille@epicevents.com \
  COMMERCIAL
```

Update a collaborator:

```bash
python -m src.main update-user-account-command \
  manager@epicevents.com \
  2 \
  "Camille Dupont" \
  camille.dupont@epicevents.com \
  COMMERCIAL
```

Deactivate a collaborator:

```bash
python -m src.main delete-user-account-command \
  manager@epicevents.com \
  2
```

### Client management

Create a client:

```bash
python -m src.main create-client-command \
  camille@epicevents.com \
  "Kevin Casey" \
  kevin@startup.io \
  "+33 6 12 34 56 78" \
  "Cool Startup LLC"
```

List clients:

```bash
python -m src.main list-clients-command manager@epicevents.com
```

Update a client:

```bash
python -m src.main update-client-command \
  camille@epicevents.com \
  1 \
  "Kevin Casey" \
  kevin@startup.io \
  "+33 6 98 76 54 32" \
  "Cool Startup LLC"
```

### Contract management

Create a contract:

```bash
python -m src.main create-contract-command \
  manager@epicevents.com \
  1 \
  10000.00 \
  4000.00 \
  true
```

List contracts:

```bash
python -m src.main list-contracts-command manager@epicevents.com
```

List unsigned contracts:

```bash
python -m src.main list-unsigned-contracts-command camille@epicevents.com
```

List unpaid contracts:

```bash
python -m src.main list-unpaid-contracts-command camille@epicevents.com
```

Update a contract:

```bash
python -m src.main update-contract-command \
  manager@epicevents.com \
  1 \
  10000.00 \
  0.00 \
  true
```

### Event management

Create an event:

```bash
python -m src.main create-event-command \
  camille@epicevents.com \
  1 \
  "Annual conference" \
  "Paris" \
  100 \
  "2026-09-10T14:00" \
  "2026-09-10T18:00" \
  "Reception starts at 1:30 PM."
```

List all events:

```bash
python -m src.main list-events-command manager@epicevents.com
```

List unassigned events:

```bash
python -m src.main list-unassigned-events-command manager@epicevents.com
```

Assign a support collaborator:

```bash
python -m src.main assign-support-to-event-command \
  manager@epicevents.com \
  1 \
  3
```

List events assigned to the authenticated support collaborator:

```bash
python -m src.main list-my-events-command support@epicevents.com
```

Update an assigned event:

```bash
python -m src.main update-event-command \
  support@epicevents.com \
  1 \
  "Annual conference" \
  "Paris - Horizon Room" \
  110 \
  "2026-09-10T14:00" \
  "2026-09-10T18:30" \
  "Reception starts at 1:30 PM and equipment must be checked."
```

---

## Permissions

| Action | Management | Sales | Support |
|---|:---:|:---:|:---:|
| Read clients, contracts, and events | Yes | Yes | Yes |
| Create, update, or deactivate a collaborator | Yes | No | No |
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

## Sentry configuration

No real DSN must be committed to the repository.

Environment variables:

```text
SENTRY_DSN
SENTRY_ENVIRONMENT
```

Git Bash:

```bash
export SENTRY_DSN="your-sentry-dsn"
export SENTRY_ENVIRONMENT="development"

python -m src.main test-sentry-command manager@epicevents.com
```

PowerShell:

```powershell
$env:SENTRY_DSN="your-sentry-dsn"
$env:SENTRY_ENVIRONMENT="development"

python -m src.main test-sentry-command manager@epicevents.com
```

Expected controlled issue:

```text
Epic Events controlled Sentry demonstration error.
```

---

## Tests

The test suite is organized into three categories.

### Unit tests

```bash
python -m pytest tests/unit -v
```

Validated result:

```text
4 tests passed
```

### Integration tests

```bash
python -m pytest tests/integration -v
```

Validated result:

```text
134 tests passed
```

### Functional tests

```bash
python -m pytest tests/functional -v
```

Validated result:

```text
9 tests passed
```

### Complete suite

```bash
python -m pytest -v
```

Validated result:

```text
147 tests passed
0 failures
```

---

## Coverage

Generate the coverage report:

```bash
python -m pytest \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html
```

Validated result:

```text
TOTAL 76%
Coverage HTML written to dir htmlcov
```

The HTML report is available at:

```text
htmlcov/index.html
```

---

## Security

- Passwords hashed with Passlib and bcrypt
- Passwords entered through hidden prompts
- Inactive accounts rejected during authentication
- Permissions enforced by role, ownership, or assignment
- Validation of amounts, dates, emails, and required fields
- Parameterized queries through Peewee
- Logical collaborator deactivation
- Local database, `.env` files, and generated reports excluded from Git
- Personal data disabled by default in Sentry
- Tests executed against an in-memory SQLite database

---

## Documentation

- `docs/architecture/architecture-summary-fr.md`
- `docs/architecture/architecture-summary-en.md`
- `docs/architecture/EpicEvents-architecture-technique.pdf`
- `docs/architecture/diagramme-des-relations.png`

Technical decisions, development journals, and UML versions are available in the other `docs/` subdirectories.

---

## Author

Alice Nocquet
