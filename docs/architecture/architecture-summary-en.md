# Architecture Summary — Epic Events CRM

Epic Events is a command-line CRM application built with **Python**. Its architecture is organized around four main layers:

- **CLI (`src/main.py`)**: user entry point implemented with Typer;
- **Services (`src/services/`)**: business logic and access control;
- **Models (`src/models/`)**: business entities persisted with Peewee;
- **Configuration / monitoring**: database setup, environment variables, and Sentry.

## Business model
The main entities are:

- **User**: collaborator assigned to a department (management, sales, support);
- **Client**: customer managed by a sales collaborator;
- **Contract**: contract linked to a client;
- **Event**: event linked to a client and handled by a support collaborator.

The relational model notably represents:

- one sales collaborator managing multiple clients;
- one client having multiple contracts;
- one client having multiple events.

## Security and permissions
The application implements:

- **secure authentication** with hashed passwords;
- **role- / department-based permissions**;
- input validation for sensitive and business data;
- clear separation between the CLI layer and business logic.

## Monitoring
Unexpected errors can be sent to **Sentry** through environment variables (`SENTRY_DSN`, `SENTRY_ENVIRONMENT`) without exposing secrets in the source code.

## Tests
The project is validated by a test suite organized into:

- **unit tests**;
- **integration tests**;
- **functional tests**.

This structure verifies business logic, database interactions, and CLI behavior.
