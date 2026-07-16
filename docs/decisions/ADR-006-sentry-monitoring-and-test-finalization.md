# ADR-006 – Sentry monitoring and test finalization

## Status

Accepted

---

## Date

2026-07-16

---

## Context

Epic Events must record application errors and exceptions with Sentry while keeping sensitive configuration outside the source code.

The finalization phase must also demonstrate that:

- unexpected exceptions can be captured and sent to Sentry;
- the Sentry DSN is not hard-coded or committed;
- monitoring can be disabled when no DSN is configured;
- the command-line interface remains functional;
- automated tests do not read, modify or delete production data;
- a coverage report can be generated;
- all previously implemented authentication, client, contract and event workflows remain operational.

---

## Problem

How should Sentry monitoring, command-line functional tests and test database isolation be added without weakening the existing security model or introducing regressions into the validated CRM features?

---

## Decision

A dedicated monitoring module is introduced:

```text
src/monitoring.py
```

It is responsible for:

- initializing the Sentry Python SDK;
- reading monitoring configuration through `src/config.py`;
- capturing unexpected application exceptions;
- flushing captured events before process termination;
- generating a controlled exception for demonstration purposes.

The configuration module now reads:

```text
SENTRY_DSN
SENTRY_ENVIRONMENT
```

from environment variables.

No DSN is stored in the Python source code.

The main application entry point initializes Sentry before running the Typer application and captures unexpected exceptions through a central `run_app()` function.

A management-only CLI command is added to generate a controlled Sentry demonstration event.

The pytest database fixture is replaced with an isolated in-memory SQLite database bound temporarily to all Peewee models.

Functional CLI tests are added using Typer's `CliRunner`.

Coverage support is added through `pytest-cov`.

---

## Monitoring architecture

### Initialization

```text
Environment variables
        │
        ▼
src.config
        │
        ▼
initialize_sentry()
        │
        ├── no DSN -> monitoring disabled
        └── DSN present -> Sentry SDK initialized
```

### Unexpected exception capture

```text
python -m src.main
        │
        ▼
run_app()
        │
        ▼
Typer application
        │
        ├── expected business error -> explicit CLI message
        └── unexpected exception
                    │
                    ▼
        capture_application_exception()
                    │
                    ▼
                  Sentry
```

### Demonstration event

```text
Authenticated management user
        │
        ▼
test_sentry_command()
        │
        ▼
send_test_exception()
        │
        ▼
Controlled RuntimeError
        │
        ▼
Sentry project
```

---

## Security choices

The Sentry SDK is initialized with:

```python
send_default_pii=False
include_local_variables=False
```

These options reduce the risk of unintentionally sending personal data or local variable contents.

The DSN is:

- read only from the process environment;
- absent from committed source files;
- absent from `.env.example`;
- protected from Git through `.gitignore`.

The controlled demonstration command is restricted to authenticated and active management collaborators.

Expected `ValueError` and `PermissionError` exceptions remain handled by the CLI and are not treated as unexpected application crashes.

---

## Test isolation

The test suite uses:

```python
SqliteDatabase(":memory:")
```

with Peewee's temporary model binding.

Consequences:

- `epic_events.db` is never opened by the automated tests;
- every test receives a clean database;
- tables and records cannot leak between tests;
- test execution remains independent from local demonstration data;
- previous service tests continue to use the same models and business logic.

---

## Functional CLI validation

Typer's `CliRunner` validates representative end-to-end command flows:

- CLI help and command registration;
- successful authentication;
- failed authentication;
- authorized client consultation;
- denied client creation by management;
- invalid event date input;
- denied Sentry demonstration by a commercial user;
- missing Sentry configuration;
- successful management Sentry command.

The service layer remains the authoritative location for permissions and business rules.

---

## Coverage decision

The project generates terminal and HTML coverage reports with `pytest-cov`.

Final measured coverage:

```text
TOTAL: 76%
```

The lower percentage in `src/main.py` is caused by the large number of CLI display and error branches.

The security-sensitive and business-critical layers remain strongly covered:

- models: 100%;
- client service: 100%;
- contract service: 100%;
- user service: 100%;
- authentication: 97%;
- event service: 97%;
- monitoring: 95%.

No artificial tests are added solely to inflate the global percentage.

---

## Consequences

### Positive

- Unexpected exceptions are centrally monitored.
- Monitoring secrets remain outside the repository.
- Sentry can be disabled safely when no DSN is available.
- A real Sentry event can be demonstrated during evaluation.
- Tests no longer risk modifying the local CRM database.
- CLI behavior is validated in addition to service-layer behavior.
- A terminal and HTML coverage report can be generated.
- All previous features remain protected by regression tests.

### Negative

- Sentry delivery requires an internet connection and a configured project.
- The in-memory database does not reproduce every file-system behavior of production SQLite.
- The CLI still prompts for authentication on each command because persistent sessions are outside the project scope.
- `src/main.py` remains less covered than the business services because of its many terminal branches.

---

## Alternatives considered

### Hard-code the Sentry DSN

Rejected because it would expose configuration in the repository.

### Store the DSN in `.env.example`

Rejected because an example file must never contain a real secret or project-specific value.

### Keep using `epic_events.db` during tests

Rejected because automated tests could destroy or alter local CRM data.

### Capture every expected business exception in Sentry

Rejected because permission refusals and validation errors are controlled application behavior, not unexpected failures.

### Add large numbers of superficial CLI tests to increase coverage

Rejected because test quality and protection of business rules are more important than an artificial percentage.

---

## Validation

Automated validation completed successfully:

```text
147 tests collected
147 tests passed
0 failures
```

Coverage validation completed successfully:

```text
TOTAL coverage: 76%
HTML report generated in htmlcov/
```

A live Sentry delivery was also verified:

- the SDK initialized successfully;
- a controlled `RuntimeError` was sent;
- the event appeared in the Sentry project dashboard.

No regression was detected in authentication, collaborator management, client management, contract management or event management.

---

## References

- OpenClassrooms Project 12 specifications.
- Project autoevaluation checklist.
- Existing Epic Events ADRs and UML documentation.
- Implemented Sentry Python SDK integration.
