# Day 08

## Objective

Refactor the Epic Events application structure so the command-line interface is organized by domain, the package can be launched with `python -m src`, technical concerns are isolated in a `core` package, and database setup scripts are separated from the regular CRM commands.

## Initial situation

The application was functional and the complete automated test suite already passed with:

```text
147 passed
0 failed
```

However:

- all Typer commands were concentrated in `src/main.py`;
- command names were long and difficult to use;
- the main module mixed application startup, CLI commands, authentication helpers, monitoring and database initialization;
- technical modules were stored directly under `src/`;
- database setup operations were exposed through the main CLI;
- the architecture did not yet match the organization requested during the mentor review.

## Mentor feedback addressed

The following points were implemented:

- rename `main.py` to `__main__.py`;
- allow the application to run with `python -m src`;
- split CLI commands into thematic modules;
- register subcommands with `app.add_typer`;
- remove suffixes such as `command` from CLI function names;
- keep `__main__.py` limited to application initialization;
- move database setup scripts into `utils` or `tools`;
- preserve dynamic permissions as a future improvement rather than implementing them now;
- prepare the codebase for JWT authentication in the next branch.

## Work completed

### Package entry point

Renamed:

```text
src/main.py
```

to:

```text
src/__main__.py
```

The application can now be launched with:

```powershell
python -m src
```

`src/__main__.py` now contains only:

- Typer application initialization;
- registration of domain-specific CLI applications;
- Sentry initialization;
- global exception handling;
- application execution.

### CLI package

Created:

```text
src/cli/
```

with the following modules:

```text
src/cli/
├── __init__.py
├── auth.py
├── client.py
├── common.py
├── contract.py
├── event.py
├── monitoring.py
└── user.py
```

Each domain exposes its own Typer application.

### Grouped commands

The previous flat commands were replaced with grouped commands.

Examples:

```text
authenticate-user-command
```

became:

```text
auth login
```

```text
create-client-command
```

became:

```text
client create
```

```text
list-contracts-command
```

became:

```text
contract list
```

```text
assign-support-to-event-command
```

became:

```text
event assign-support
```

The main CLI help now displays only the domain groups:

```text
auth
user
client
contract
event
monitoring
```

### Shared CLI helpers

Created:

```text
src/cli/common.py
```

This module centralizes:

- secure password prompting;
- current-user authentication shared by several CLI modules.

The helper will be adapted during the JWT authentication branch so subsequent commands can use the locally stored token instead of prompting for credentials repeatedly.

### Core package

Created:

```text
src/core/
```

with:

```text
src/core/
├── __init__.py
├── auth.py
├── config.py
├── database.py
└── monitoring.py
```

Moved:

```text
src/auth.py
src/config.py
src/database.py
src/monitoring.py
```

into `src/core/`.

The `core` package now contains cross-cutting technical concerns:

- authentication and authorization;
- environment-based configuration;
- shared Peewee database connection;
- Sentry initialization and exception capture.

### Utility scripts

Created:

```text
src/utils/
├── __init__.py
├── create_db.py
└── create_user.py
```

`create_db.py` safely creates the application tables:

```powershell
python -m src.utils.create_db
```

`create_user.py` creates the first management collaborator when the database contains no user:

```powershell
python -m src.utils.create_user FULL_NAME EMAIL
```

These setup operations are intentionally separated from the regular CRM CLI.

### Import updates

Updated imports across:

- `src/__main__.py`;
- CLI modules;
- models;
- services;
- utility scripts;
- functional, integration and unit tests.

Examples:

```python
from src.auth import require_permission
```

became:

```python
from src.core.auth import require_permission
```

```python
from src.database import database
```

became:

```python
from src.core.database import database
```

### Test updates

Updated tests to use:

```python
from src.__main__ import app
```

instead of:

```python
from src.main import app
```

Updated CLI functional tests to execute grouped commands such as:

```text
auth login
client list
client create
event create
monitoring test-sentry
```

Updated Sentry monkeypatch targets to use:

```text
src.core.monitoring
src.cli.monitoring
```

## Final source structure

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
│   ├── client.py
│   ├── contract.py
│   ├── event.py
│   └── user.py
├── services/
│   ├── client_service.py
│   ├── contract_service.py
│   ├── event_service.py
│   └── user_service.py
└── utils/
    ├── __init__.py
    ├── create_db.py
    └── create_user.py
```

## Validation

### CLI discovery

Validated:

```powershell
python -m src --help
python -m src auth --help
python -m src user --help
python -m src client --help
python -m src contract --help
python -m src event --help
python -m src monitoring --help
```

### Utility scripts

Validated help output:

```powershell
python -m src.utils.create_db --help
python -m src.utils.create_user --help
```

The existing local database was not reinitialized and the initial-user script was not executed because collaborators already existed.

### Complete regression suite

Command:

```powershell
python -m pytest
```

Result:

```text
147 passed
0 failed
```

No business-rule regression was introduced.

## Git history

The refactoring was split into two commits.

### Architecture and CLI

```text
bdb44e1 refactor: reorganize application architecture and CLI commands
```

### Utility scripts

```text
b736bb9 feat: add database setup utility scripts
```

Both commits were pushed to `main`.

## Next branch

Created and pushed:

```text
feature/jwt-authentication
```

The working tree was clean before starting the next feature.

## Decisions

- Keep `__main__.py` at the root of `src` so Python can execute the package with `python -m src`.
- Keep `__main__.py` limited to application initialization.
- Use one Typer application per domain.
- Use `app.add_typer` to expose grouped commands.
- Keep shared CLI-only helpers in `cli/common.py`.
- Store cross-cutting technical concerns in `core/`.
- Store setup and maintenance scripts in `utils/`.
- Keep business rules and permissions in the service layer.
- Preserve previous journal, ADR and UML versions as historical records.
- Document this architecture with a new ADR and a new UML version.
- Postpone service class methods because they were suggested but not required.
- Keep dynamic permissions as a possible future improvement, as requested by the mentor.

## Result

The application now has:

```text
a clean package entry point
+
domain-oriented CLI modules
+
shorter and clearer commands
+
isolated technical components
+
separate setup scripts
+
147 passing tests
```

## Next steps

- Add ADR-008 documenting the package and CLI reorganization.
- Add UML v1.0 documenting the current application architecture.
- Implement JWT authentication with local JSON token storage.
- Adapt and extend automated tests for JWT authentication.
- Create the next journal, ADR and UML version after the JWT work.
- Update the final README and living architecture documentation once the authentication flow is complete.
