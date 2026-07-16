# UML v0.9 – Test suite architecture

## Status

Validated

## Date

2026-07-16

## Evolution from UML v0.8

UML v0.9 does not modify the Epic Events production architecture.

It documents the new organization of the automated test suite into:

- unit tests;
- integration tests;
- functional tests.

The following remain unchanged:

- domain models;
- database relationships;
- service-layer responsibilities;
- authentication;
- role-based authorization;
- Typer CLI commands;
- Sentry monitoring;
- production database configuration.

## Test directory structure

```text
tests/
├── conftest.py
│
├── unit/
│   └── test_monitoring.py
│
├── integration/
│   ├── test_auth.py
│   ├── test_client_service.py
│   ├── test_contract_service.py
│   ├── test_database.py
│   ├── test_event_service.py
│   └── test_user_service.py
│
└── functional/
    └── test_cli.py
```

## Test pyramid

```text
                  ┌─────────────────────────────┐
                  │     FUNCTIONAL TESTS        │
                  │                             │
                  │ Typer CLI + CliRunner       │
                  │ 9 tests                     │
                  └──────────────┬──────────────┘
                                 │
                  ┌──────────────▼──────────────┐
                  │     INTEGRATION TESTS       │
                  │                             │
                  │ Services + Models + SQLite  │
                  │ Authentication + Permissions│
                  │ 134 tests                   │
                  └──────────────┬──────────────┘
                                 │
                  ┌──────────────▼──────────────┐
                  │        UNIT TESTS           │
                  │                             │
                  │ Monitoring with mocks       │
                  │ 4 tests                     │
                  └─────────────────────────────┘
```

The number of integration tests is larger because the core project behavior is based on interactions between business services, Peewee models and SQLite.

## Shared fixture flow

```text
tests/conftest.py
        │
        ├── in-memory SQLite database
        ├── model table creation
        ├── management user
        ├── commercial user
        ├── support user
        ├── client
        ├── contract
        └── event
        │
        ▼
tests/integration/
tests/functional/
```

Unit monitoring tests use mocks and environment manipulation, but the root fixture file remains discoverable without duplication.

## Unit-test architecture

```text
tests/unit/test_monitoring.py
        │
        ├── mock environment configuration
        ├── mock sentry_sdk.init
        ├── mock sentry_sdk.capture_exception
        └── mock sentry_sdk.flush
        │
        ▼
src/monitoring.py
```

Validated responsibilities:

```text
initialize_sentry()
capture_application_exception()
send_test_exception()
```

External Sentry delivery is not required during the unit tests.

A separate manual validation already confirmed real delivery to Sentry.

## Integration-test architecture

```text
Integration test
        │
        ▼
Authentication or service function
        │
        ▼
Peewee model
        │
        ▼
SQLite database in memory
```

Detailed flow:

```text
tests/integration/
        │
        ├── test_auth.py
        │       └── User model + password verification
        │
        ├── test_user_service.py
        │       └── User CRUD + management permissions
        │
        ├── test_client_service.py
        │       └── Client CRUD + ownership permissions
        │
        ├── test_contract_service.py
        │       └── Contract workflows + amount validation
        │
        ├── test_event_service.py
        │       └── Event workflows + support assignment
        │
        └── test_database.py
                └── table initialization
```

The temporary database binding is:

```text
Production model classes
        │
        ▼
bind_ctx(TEST_MODELS)
        │
        ▼
SqliteDatabase(":memory:")
```

This preserves the real ORM mappings while preventing access to `epic_events.db`.

## Functional-test architecture

```text
tests/functional/test_cli.py
        │
        ▼
Typer CliRunner
        │
        ▼
src.main.app
        │
        ├── input parsing
        ├── authentication prompt
        ├── command authorization
        ├── service invocation
        └── terminal response
```

Representative validated paths:

```text
CLI help
Authentication success
Authentication failure
Client consultation
Unauthorized client creation
Invalid event date
Unauthorized Sentry command
Missing Sentry configuration
Successful Sentry command
```

## Production security flow under test

```text
CLI input
    │
    ▼
Authentication
    │
    ▼
Role and activity checks
    │
    ▼
Service-layer authorization
    │
    ▼
Business validation
    │
    ▼
Peewee ORM
    │
    ▼
SQLite
```

The test reorganization does not move authorization rules into tests or into the CLI.

The service layer remains the source of truth.

## Execution matrix

```text
+----------------------+---------------------------------------------+
| Command              | Scope                                       |
+----------------------+---------------------------------------------+
| pytest tests/unit    | Isolated monitoring behavior                |
| pytest tests/integration | Services, models, auth and SQLite       |
| pytest tests/functional  | Public CLI workflows                    |
| pytest               | Complete regression suite                   |
| pytest --cov=src     | Complete suite with source-code coverage     |
+----------------------+---------------------------------------------+
```

## Validated results

```text
Unit tests:           4 passed
Integration tests: 134 passed
Functional tests:     9 passed
Complete suite:     147 passed
Failures:              0
Total coverage:       76%
```

Coverage remained identical after moving the files.

## Change boundary

```text
Modified by this branch:
    tests/ file locations
    branch documentation

Not modified by this branch:
    src/
    business rules
    database schema
    permissions
    dependencies
    Sentry configuration
```

## Final conclusion

The project now exposes three clear validation levels:

```text
isolated component behavior
        +
internal component collaboration
        +
user-facing application workflows
```

The complete regression suite remains green and coverage remains stable.
