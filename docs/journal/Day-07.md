# Day 07

## Objective

Reorganize the Epic Events automated test suite into explicit unit, integration and functional categories without modifying application behavior.

## Branch

```text
feature/test-suite-reorganization
```

## Initial situation

The complete suite contained 147 passing tests, but every test file was stored directly in `tests/`.

The test type had to be inferred from file contents rather than from the project structure.

## Work completed

### Directory creation

Created:

```text
tests/unit/
tests/integration/
tests/functional/
```

### Unit tests

Moved:

```text
tests/test_monitoring.py
```

to:

```text
tests/unit/test_monitoring.py
```

The monitoring tests isolate Sentry configuration and SDK calls.

### Integration tests

Moved:

```text
tests/test_auth.py
tests/test_client_service.py
tests/test_contract_service.py
tests/test_database.py
tests/test_event_service.py
tests/test_user_service.py
```

to:

```text
tests/integration/
```

These tests exercise several internal layers together:

- services;
- Peewee models;
- authentication and authorization;
- the isolated in-memory SQLite database;
- shared fixtures.

### Functional tests

Moved:

```text
tests/test_cli.py
```

to:

```text
tests/functional/test_cli.py
```

These tests execute the Typer CLI through `CliRunner`.

### Shared fixtures

Kept:

```text
tests/conftest.py
```

at the root of `tests/`.

This allows pytest to expose the same fixtures to unit, integration and functional tests.

## Final structure

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

## Validation

### Unit tests

Command:

```bash
python -m pytest tests/unit -v
```

Result:

```text
4 passed
```

### Integration tests

Command:

```bash
python -m pytest tests/integration -v
```

Result:

```text
134 passed
```

### Functional tests

Command:

```bash
python -m pytest tests/functional -v
```

Result:

```text
9 passed
```

### Complete regression suite

Command:

```bash
python -m pytest -v
```

Result:

```text
147 passed
0 failed
```

### Coverage

Command:

```bash
python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```

Result:

```text
147 passed
TOTAL coverage: 76%
Coverage HTML written to dir htmlcov
```

Detailed results:

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
TOTAL                         76%
```

## Decisions

- Use directories rather than pytest markers as the primary classification mechanism.
- Keep shared fixtures in one root `conftest.py`.
- Classify monitoring tests as unit tests because Sentry interactions are replaced by mocks.
- Classify authentication tests as integration tests because they query persisted users.
- Classify service tests as integration tests because they combine services, models and SQLite.
- Classify CLI tests as functional tests because they exercise the public application interface.
- Do not add artificial tests solely to change the test count or coverage percentage.
- Do not change production code in this branch.

## Result

The test suite is now easier to understand and demonstrate.

The reorganization caused:

```text
0 lost tests
0 new failures
0 coverage regression
0 production-code changes
```

## Next steps

- Add ADR-007 documenting the test strategy.
- Add UML v0.9 showing the three test layers.
- Commit the branch documentation separately from the file reorganization.
- Push `feature/test-suite-reorganization`.
- Merge the branch locally into `main`.
- Keep the remote feature branch.
- Create `feature/final-documentation`.
- Finalize the README and the `docs/architecture/` directory.
