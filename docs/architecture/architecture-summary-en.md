# Architecture Summary - Epic Events CRM

Epic Events is a secure command-line CRM built with Python 3.12. The application runs with `python -m src`, and its architecture clearly separates the CLI, cross-cutting core functions, business services, and persistence.

## Current architecture

- **Entry point (`src/__main__.py`)**: composes Typer groups with `app.add_typer`, initializes Sentry, and catches unexpected exceptions.
- **CLI (`src/cli/`)**: `auth`, `user`, `client`, `contract`, `event`, and `monitoring` groups. The CLI collects arguments and displays responses; it does not own business rules.
- **Core (`src/core/`)**: bcrypt authentication, configuration, SQLite connection, JWT lifecycle, and Sentry monitoring.
- **Services (`src/services/`)**: validation, permissions, client and contract ownership, event assignment, and least privilege.
- **Models (`src/models/`)**: Peewee `User`, `Client`, `Contract`, and `Event` entities.
- **Utilities (`src/utils/`)**: database-table creation and initial management-account creation.

## JWT authentication

`python -m src auth login EMAIL` verifies the password through a hidden prompt, creates an HS256-signed JWT valid for 60 minutes, and stores it in `.epic_events_token.json`.

Each protected command:

1. loads and validates the token;
2. verifies its signature and expiration;
3. reads the user identifier from the `sub` claim;
4. reloads the user from SQLite;
5. rejects missing or inactive accounts;
6. delegates authorization to the service layer.

The department claim is therefore not the source of truth for permissions.

## Relational model

- one sales `User` may be responsible for multiple `Client` and `Contract` records;
- one `Client` may have multiple `Contract` records;
- one `Contract` may cover multiple `Event` records;
- one `Event` may have zero or one support collaborator, while one support collaborator may manage multiple events;
- sensitive relationships use `RESTRICT`, while the optional support relationship uses `SET NULL`;
- logical collaborator deactivation preserves CRM records.

## Security

- passwords hashed with Passlib and bcrypt;
- signed, expiring JWT with the secret read from the environment;
- `.env`, `.epic_events_token.json`, and `epic_events.db` excluded from Git;
- parameterized Peewee queries against SQL injection;
- permissions based on department, ownership, and assignment;
- SQLite revalidation for every protected command;
- Sentry configured with `send_default_pii=False` and `include_local_variables=False`.

## Validation

- **156 tests passed**, 0 failures;
- **4 unit tests**, **143 integration tests**, **9 functional tests**;
- **77% total coverage**;
- **96% coverage for `src/core/jwt_auth.py`**;
- isolated in-memory SQLite test database and temporary JWT test files.

## Main commands

```powershell
python -m src.utils.create_db
python -m src.utils.create_user "Morgan Manager" manager@epicevents.com
python -m src auth login manager@epicevents.com
python -m src client list
python -m src monitoring test-sentry
python -m src auth logout
python -m pytest -q
python -m pytest --cov=src --cov-report=term-missing
```
