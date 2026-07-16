# ADR-007 – Test suite organization

## Status

Accepted

## Date

2026-07-16

## Context

The Epic Events project has a complete automated test suite covering authentication, business services, persistence, monitoring and the Typer command-line interface.

Before this decision, all test files were stored directly in the `tests/` directory. Although the suite was functional, the test level of each file was not immediately visible.

The project now needs a clearer separation between:

- unit tests;
- integration tests;
- functional tests.

The reorganization must not change application behavior, business rules, fixtures or test assertions.

## Decision

The test suite is divided into three explicit directories:

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

`tests/conftest.py` remains at the root of the test directory so its fixtures remain available to all three categories.

No production source file is modified by this branch.

## Test classification

### Unit tests

Unit tests validate a component in isolation from external systems.

Current unit-test scope:

```text
tests/unit/test_monitoring.py
```

The monitoring functions are tested by replacing Sentry SDK calls and environment configuration with controlled test doubles.

Validated behaviors include:

- monitoring disabled without a DSN;
- Sentry initialization with environment configuration;
- exception capture;
- controlled demonstration exception.

### Integration tests

Integration tests validate collaboration between several internal components.

Current integration-test scope:

```text
tests/integration/test_auth.py
tests/integration/test_client_service.py
tests/integration/test_contract_service.py
tests/integration/test_database.py
tests/integration/test_event_service.py
tests/integration/test_user_service.py
```

These tests combine:

- Peewee models;
- service functions;
- authentication and authorization rules;
- an isolated in-memory SQLite database;
- shared pytest fixtures.

`test_auth.py` is classified as an integration test because authentication queries persisted `User` records through Peewee.

### Functional tests

Functional tests validate application behavior through its public command-line interface.

Current functional-test scope:

```text
tests/functional/test_cli.py
```

The Typer application is executed with `CliRunner`.

Validated flows include:

- command discovery;
- successful authentication;
- failed authentication;
- authorized data consultation;
- denied operations;
- invalid user input;
- Sentry command authorization and execution.

## Test execution

Each category can be run independently:

```bash
python -m pytest tests/unit -v
python -m pytest tests/integration -v
python -m pytest tests/functional -v
```

The complete suite is run with:

```bash
python -m pytest -v
```

Coverage is generated with:

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

## Validation results

The reorganized test suite produced the following results:

```text
Unit tests:          4 passed
Integration tests: 134 passed
Functional tests:    9 passed
Complete suite:    147 passed
Failures:             0
```

Coverage remained unchanged:

```text
TOTAL: 76%
```

Main coverage results:

```text
auth.py                       97%
config.py                    100%
database.py                  100%
models                       100%
monitoring.py                 95%
client_service.py            100%
contract_service.py          100%
event_service.py              97%
user_service.py              100%
main.py                       41%
```

The HTML report was generated successfully in:

```text
htmlcov/
```

## Consequences

### Positive

- The test level of each file is immediately understandable.
- Each category can be executed independently.
- The distinction between isolated components, integrated business logic and user-facing workflows is explicit.
- The structure is easier to explain during project evaluation.
- Shared fixtures remain centralized.
- Test count and coverage remain unchanged.
- No business rule or application behavior is altered.

### Negative

- File paths in documentation and future commands must use the new directories.
- New contributors must classify each new test correctly.
- The integration category remains larger because most project behavior relies on the ORM, services and database together.

## Alternatives considered

### Keep every test at the root of `tests/`

Rejected because the suite would remain less readable and test levels would remain implicit.

### Use pytest markers without moving files

Rejected for this stage because directories provide immediate visual organization and require no marker maintenance.

### Duplicate `conftest.py` in each subdirectory

Rejected because duplicated fixtures would increase maintenance and create a risk of inconsistent test data.

### Classify authentication as a unit test

Rejected because current authentication tests use persisted `User` records and the Peewee ORM.

## Compliance

This decision improves test readability and maintainability while preserving:

- the isolated SQLite test database;
- authentication and authorization coverage;
- business-service validation;
- CLI workflow validation;
- Sentry monitoring validation;
- the complete regression suite.

## References

- ADR-006 – Sentry monitoring and test finalization.
- UML v0.8 – Monitoring and test architecture.
- Epic Events automated test suite.
