# UML v0.8 - Monitoring and test architecture

## Status

Validated

## Date

2026-07-16

## Evolution

Compared to UML v0.7:

- Added `src/monitoring.py`.
- Added environment-based Sentry configuration.
- Added monitored application startup through `run_app()`.
- Added centralized unexpected-exception capture.
- Added a management-only Sentry demonstration command.
- Added an isolated in-memory SQLite test database.
- Added functional CLI tests with `CliRunner`.
- Added monitoring tests.
- Added coverage generation.
- Preserved all existing domain entities, relationships and permissions.

---

## Current project structure

```text
.
├── .env.example
├── .gitignore
├── requirements.txt
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
    ├── test_auth.py
    ├── test_cli.py
    ├── test_client_service.py
    ├── test_contract_service.py
    ├── test_database.py
    ├── test_event_service.py
    ├── test_monitoring.py
    └── test_user_service.py
```

---

## Component responsibilities

### `src/config.py`

```text
Configuration
├── DATABASE_PATH
├── get_sentry_dsn()
└── get_sentry_environment()
```

Responsibilities:

- centralize application configuration;
- read the Sentry DSN from the environment;
- provide a default monitoring environment;
- keep monitoring values outside source code.

### `src/monitoring.py`

```text
Monitoring
├── initialize_sentry()
├── capture_application_exception()
└── send_test_exception()
```

Responsibilities:

- initialize the Sentry SDK conditionally;
- capture unexpected exceptions;
- flush queued events;
- generate a controlled demonstration exception.

### `src/main.py`

Responsibilities:

- expose Typer commands;
- authenticate CLI users;
- delegate business rules to services;
- display expected errors;
- initialize monitoring;
- capture unexpected top-level exceptions.

### Service layer

```text
Services
├── user_service.py
├── client_service.py
├── contract_service.py
└── event_service.py
```

Responsibilities:

- validate business data;
- enforce role, ownership and assignment permissions;
- perform ORM operations;
- remain independent from terminal presentation.

### Models

```text
User -> Client -> Contract -> Event
                         Event -> optional Support User
```

The domain model is unchanged from UML v0.7.

---

## Monitoring initialization sequence

```text
Operating-system environment
        │
        ├── SENTRY_DSN
        └── SENTRY_ENVIRONMENT
        │
        ▼
src.config
        │
        ▼
initialize_sentry()
        │
        ├── DSN missing
        │       └── return False
        │
        └── DSN present
                │
                ▼
        sentry_sdk.init()
                │
                ├── send_default_pii=False
                ├── include_local_variables=False
                ├── traces_sample_rate=None
                └── enable_logs=True
```

---

## Application execution sequence

```text
python -m src.main
        │
        ▼
run_app()
        │
        ├── initialize_sentry()
        │
        ▼
Typer app()
        │
        ├── normal command completion
        │       └── return result
        │
        ├── expected ValueError / PermissionError
        │       └── command prints explicit message
        │
        └── unexpected Exception
                │
                ▼
        capture_application_exception()
                │
                ▼
        generic terminal error
                │
                ▼
            SystemExit(1)
```

---

## Controlled Sentry demonstration sequence

```text
test-sentry-command
        │
        ▼
_authenticate_current_user()
        │
        ▼
require_permission(MANAGEMENT)
        │
        ├── denied -> PermissionError
        │
        ▼
initialize_sentry()
        │
        ├── not configured -> CLI error
        │
        ▼
send_test_exception()
        │
        ▼
RuntimeError
"Epic Events controlled Sentry demonstration error."
        │
        ▼
capture_application_exception()
        │
        ▼
Sentry event identifier
```

---

## Test database architecture

### Production

```text
src.database.database
        │
        ▼
epic_events.db
```

### Automated tests

```text
pytest fixture
        │
        ▼
SqliteDatabase(":memory:")
        │
        ▼
bind_ctx(TEST_MODELS)
        │
        ▼
User / Client / Contract / Event
        │
        ▼
fresh tables for each test
```

Isolation properties:

- no automated test opens `epic_events.db`;
- every test starts with an empty schema;
- records cannot leak between tests;
- production and demonstration data remain protected;
- the same Peewee models and service functions are exercised.

---

## Automated test layers

```text
+--------------------------------------+
| Functional CLI tests                 |
| Typer CliRunner                      |
+--------------------------------------+
                  │
                  ▼
+--------------------------------------+
| Service and authorization tests      |
| user / client / contract / event     |
+--------------------------------------+
                  │
                  ▼
+--------------------------------------+
| Authentication and monitoring tests  |
+--------------------------------------+
                  │
                  ▼
+--------------------------------------+
| Peewee models + in-memory SQLite      |
+--------------------------------------+
```

### Functional CLI tests

Validate:

- application command registration;
- authentication success and failure;
- CLI-to-service delegation;
- explicit permission refusals;
- event-date parsing;
- Sentry command behavior.

### Service tests

Validate:

- role-based permissions;
- ownership restrictions;
- support assignment restrictions;
- input validation;
- database persistence.

### Monitoring tests

Validate:

- disabled monitoring without a DSN;
- environment-based SDK initialization;
- exception capture;
- event queue flushing;
- controlled exception generation.

---

## Security boundaries

```text
User input
    │
    ▼
Typer CLI
    │ authentication
    ▼
Service layer
    │ authorization + validation
    ▼
Peewee ORM
    │ parameterized SQL
    ▼
SQLite
```

Unexpected technical exceptions follow a separate path:

```text
Unexpected Exception
    │
    ▼
Monitoring module
    │ PII disabled
    │ local variables disabled
    ▼
Sentry
```

Sensitive configuration boundary:

```text
SENTRY_DSN
    │
    ├── process environment only
    ├── not committed
    ├── absent from .env.example
    └── ignored local .env file
```

---

## Coverage architecture

Command:

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

Generated outputs:

```text
Terminal report
.coverage
htmlcov/index.html
```

Repository policy:

```text
.coverage     ignored
htmlcov/      ignored
```

Validated result:

```text
147 tests passed
76% total coverage
```

Critical-layer coverage:

```text
models                    100%
client_service.py         100%
contract_service.py       100%
user_service.py           100%
auth.py                    97%
event_service.py           97%
monitoring.py              95%
```

---

## Live monitoring validation

```text
Controlled RuntimeError
        │
        ▼
Sentry SDK initialized: True
        │
        ▼
Event identifier returned
        │
        ▼
Issue visible in Sentry dashboard
```

Visible issue title:

```text
Epic Events controlled Sentry demonstration error.
```

This confirms that monitoring works beyond mocked automated tests.

---

## Final validation

```text
147 collected
147 passed
0 failed
76% total coverage
HTML coverage report generated
Live Sentry event received
```

No regression was detected in:

- authentication;
- collaborator management;
- client management;
- contract management;
- event management;
- database initialization;
- role-based authorization.
