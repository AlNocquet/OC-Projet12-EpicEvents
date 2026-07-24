# ADR-008 – CLI and application package reorganization

## Status

Accepted

## Date

2026-07-24

## Context

The Epic Events CRM was already functional and covered by 147 automated tests.

However, the command-line interface and technical structure were concentrated around `src/main.py`.

The main module contained:

- Typer application creation;
- authentication helpers;
- user commands;
- client commands;
- contract commands;
- event commands;
- monitoring commands;
- database initialization;
- initial management-user creation;
- application startup.

This structure worked, but it created several problems:

- command names were long and difficult to use;
- the main help output mixed every operation in one flat list;
- responsibilities were not clearly separated;
- application startup was coupled to business and setup commands;
- technical modules were stored directly under `src/`;
- the structure was harder to explain and maintain;
- the upcoming JWT authentication change would have increased the size and coupling of the main module.

During the mentor review, the following improvements were requested:

- rename `main.py` to `__main__.py`;
- use `app.add_typer`;
- split CLI commands by domain;
- remove suffixes such as `command`;
- keep the main module limited to application initialization;
- move database setup scripts into `utils` or `tools`.

## Decision

### Package entry point

Use:

```text
src/__main__.py
```

as the application entry point.

The application is launched with:

```powershell
python -m src
```

`src/__main__.py` is limited to:

- creating the root Typer application;
- registering domain Typer applications;
- initializing Sentry;
- handling unexpected application exceptions;
- running the application.

### Domain-oriented CLI modules

Create:

```text
src/cli/
```

with one module per command domain:

```text
auth.py
user.py
client.py
contract.py
event.py
monitoring.py
```

Each module owns a dedicated:

```python
app = typer.Typer(...)
```

The root application registers them through:

```python
app.add_typer(...)
```

### Grouped command names

Replace flat command names with domain groups.

Examples:

```text
authenticate-user-command
```

becomes:

```text
auth login
```

```text
create-client-command
```

becomes:

```text
client create
```

```text
list-unsigned-contracts-command
```

becomes:

```text
contract list-unsigned
```

```text
assign-support-to-event-command
```

becomes:

```text
event assign-support
```

### Shared CLI helpers

Create:

```text
src/cli/common.py
```

for helpers shared by several CLI modules.

Current responsibilities:

- hidden password prompt;
- current-user authentication.

This module contains CLI-specific helper behavior only. It does not contain service-layer business rules.

### Core package

Create:

```text
src/core/
```

for cross-cutting technical concerns:

```text
auth.py
config.py
database.py
monitoring.py
```

The package contains:

- credential verification and role checks;
- environment-based configuration;
- shared database configuration;
- Sentry initialization and exception capture.

### Utility package

Create:

```text
src/utils/
```

for setup scripts that do not belong to the normal CRM interface.

Current scripts:

```text
create_db.py
create_user.py
```

They are executed independently:

```powershell
python -m src.utils.create_db
python -m src.utils.create_user FULL_NAME EMAIL
```

### Business-rule boundary

Keep authorization and business validation in the service layer.

The CLI:

- collects input;
- resolves the current user;
- calls services;
- displays results and expected errors.

The CLI does not become the source of truth for permissions.

## Resulting structure

```text
src/
├── __init__.py
├── __main__.py
├── cli/
│   ├── __init__.py
│   ├── auth.py
│   ├── client.py
│   ├── common.py
│   ├── contract.py
│   ├── event.py
│   ├── monitoring.py
│   └── user.py
├── core/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   └── monitoring.py
├── models/
├── services/
└── utils/
    ├── __init__.py
    ├── create_db.py
    └── create_user.py
```

## Command architecture

```text
python -m src
      │
      ▼
src/__main__.py
      │
      ├── auth
      ├── user
      ├── client
      ├── contract
      ├── event
      └── monitoring
            │
            ▼
      domain CLI module
            │
            ▼
         service layer
            │
            ▼
      Peewee models / SQLite
```

Authentication helpers are shared through:

```text
domain CLI module
        │
        ▼
src/cli/common.py
        │
        ▼
src/core/auth.py
        │
        ▼
User model / SQLite
```

## Consequences

### Positive

- The application can be launched with the concise command `python -m src`.
- Root help output contains clear domain groups.
- Commands are shorter and easier to discover.
- Each CLI file has a focused responsibility.
- `__main__.py` remains small and readable.
- Cross-cutting technical modules are grouped consistently.
- Setup scripts are separated from regular CRM use.
- The structure is easier to test, explain and maintain.
- The architecture provides a clean base for JWT authentication.
- Existing business rules remain unchanged.
- The full regression suite remains green with 147 passing tests.

### Negative

- Many imports had to be updated.
- Existing functional tests had to be rewritten to use grouped commands.
- Previous architecture documents contain historical paths such as `src.main` and `src.monitoring`.
- New contributors must understand the distinction between:
  - `src/cli/auth.py`;
  - `src/core/auth.py`.
- Setup scripts are not displayed in the regular CRM help because they are executed independently.
- Future refactoring must avoid circular imports between CLI, core, services and models.

## Alternatives considered

### Keep all commands in one main module

Rejected because the main module would remain large, command discovery would remain flat, and JWT authentication would increase coupling.

### Create one CLI module without domain subpackages

Rejected because a single CLI module would reproduce most of the original maintainability problem.

### Move business authorization into CLI decorators

Rejected because the service layer must remain the source of truth for permissions and the principle of least privilege.

### Put database setup commands in the regular CLI

Rejected for this stage because initialization and bootstrap operations are technical setup tasks, not recurring CRM workflows.

### Keep technical modules directly under `src`

Rejected because `auth`, `config`, `database` and `monitoring` are cross-cutting technical components that form a coherent `core` package.

### Convert every service to class methods during the same refactoring

Rejected because this was a mentor preference rather than a required correction and would have expanded the change boundary without functional benefit.

## Validation

The following commands were validated:

```powershell
python -m src --help
python -m src auth --help
python -m src user --help
python -m src client --help
python -m src contract --help
python -m src event --help
python -m src monitoring --help
python -m src.utils.create_db --help
python -m src.utils.create_user --help
```

Complete regression suite:

```powershell
python -m pytest
```

Result:

```text
147 passed
0 failed
```

## Compliance

This decision preserves:

- the command-line application requirement;
- authenticated access;
- role-based authorization;
- service-layer enforcement;
- the principle of least privilege;
- Peewee parameterized queries;
- Sentry monitoring;
- the isolated SQLite test database;
- functional, integration and unit test coverage.

## Historical boundary

This ADR does not replace ADR-007.

ADR-007 remains the accepted record for test-suite organization.

This ADR documents the later production-architecture refactoring.

## References

- Day 07 – Test suite reorganization.
- ADR-007 – Test suite organization.
- UML v0.9 – Test suite architecture.
- Day 08 – CLI and application package reorganization.
- UML v1.0 – Application package and CLI architecture.
- Epic Events mentor review.
