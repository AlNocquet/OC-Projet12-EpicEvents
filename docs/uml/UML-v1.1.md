# UML v1.1 — JWT authentication architecture

## Purpose

This document describes the Epic Events architecture after introducing JWT authentication and a persistent local CLI session.

It complements the domain model by showing:

- the login flow;
- local token persistence;
- token validation;
- database-backed user resolution;
- service-layer authorization;
- logout behavior;
- failure paths.

## Version history

| Version | Main change |
|---|---|
| v0.9 | Initial CRM domain and role model |
| v1.0 | CLI package reorganization and architectural separation |
| v1.1 | JWT authentication and persistent local session |

## Component architecture

```mermaid
flowchart LR
    USER[CLI user]

    subgraph CLI["CLI layer — src/cli"]
        MAIN["__main__.py"]
        AUTHCLI["auth.py"]
        COMMON["common.py"]
        BUSINESS["client.py / contract.py / event.py / user.py / monitoring.py"]
    end

    subgraph CORE["Core layer — src/core"]
        AUTH["auth.py<br/>Credential verification"]
        JWT["jwt_auth.py<br/>JWT lifecycle"]
        CONFIG["config.py<br/>Secret, algorithm, expiration, token path"]
        DATABASE["database.py<br/>Peewee connection"]
    end

    subgraph SERVICE["Service layer — src/services"]
        CLIENTSERVICE["client_service.py"]
        CONTRACTSERVICE["contract_service.py"]
        EVENTSERVICE["event_service.py"]
        USERSERVICE["user_service.py"]
    end

    subgraph MODEL["Model layer — src/models"]
        USERMODEL["User"]
        CLIENTMODEL["Client"]
        CONTRACTMODEL["Contract"]
        EVENTMODEL["Event"]
    end

    ENV[".env<br/>JWT_SECRET_KEY"]
    TOKEN[".epic_events_token.json<br/>Local bearer token"]
    SQLITE["SQLite database"]

    USER --> MAIN
    MAIN --> AUTHCLI
    MAIN --> BUSINESS

    AUTHCLI --> AUTH
    AUTHCLI --> JWT
    COMMON --> JWT
    BUSINESS --> COMMON
    BUSINESS --> CLIENTSERVICE
    BUSINESS --> CONTRACTSERVICE
    BUSINESS --> EVENTSERVICE
    BUSINESS --> USERSERVICE

    JWT --> CONFIG
    CONFIG --> ENV
    JWT --> TOKEN
    JWT --> USERMODEL

    AUTH --> USERMODEL

    CLIENTSERVICE --> CLIENTMODEL
    CLIENTSERVICE --> USERMODEL
    CONTRACTSERVICE --> CONTRACTMODEL
    CONTRACTSERVICE --> CLIENTMODEL
    CONTRACTSERVICE --> USERMODEL
    EVENTSERVICE --> EVENTMODEL
    EVENTSERVICE --> CONTRACTMODEL
    EVENTSERVICE --> USERMODEL
    USERSERVICE --> USERMODEL

    USERMODEL --> DATABASE
    CLIENTMODEL --> DATABASE
    CONTRACTMODEL --> DATABASE
    EVENTMODEL --> DATABASE
    DATABASE --> SQLITE
```

## Login sequence

```mermaid
sequenceDiagram
    actor Collaborator
    participant CLI as auth login
    participant Auth as core.auth
    participant DB as SQLite / User
    participant JWT as core.jwt_auth
    participant Config as core.config
    participant File as .epic_events_token.json

    Collaborator->>CLI: email + password
    CLI->>Auth: authenticate_user(email, password)
    Auth->>DB: find active user by email
    DB-->>Auth: persisted user
    Auth->>Auth: bcrypt password verification

    alt invalid credentials
        Auth-->>CLI: authentication error
        CLI-->>Collaborator: access denied
    else valid credentials
        Auth-->>CLI: authenticated user
        CLI->>JWT: create_access_token(user)
        JWT->>Config: get secret, algorithm, expiration
        Config-->>JWT: JWT configuration
        JWT->>JWT: create signed payload
        JWT-->>CLI: encoded token
        CLI->>JWT: save_token(token)
        JWT->>File: write JSON access_token
        JWT-->>CLI: session stored
        CLI-->>Collaborator: welcome message
    end
```

## Protected command sequence

```mermaid
sequenceDiagram
    actor Collaborator
    participant Command as Protected CLI command
    participant Common as cli.common
    participant JWT as core.jwt_auth
    participant File as Token file
    participant DB as SQLite / User
    participant Service as Business service
    participant Models as Domain models

    Collaborator->>Command: execute command
    Command->>Common: get_current_user_from_session()
    Common->>JWT: get_current_user_from_token()
    JWT->>File: load access_token

    alt token file missing or malformed
        JWT-->>Common: ValueError
        Common-->>Command: exit code 1
        Command-->>Collaborator: please log in
    else token loaded
        JWT->>JWT: verify signature and expiration

        alt invalid or expired token
            JWT-->>Common: ValueError
            Common-->>Command: exit code 1
            Command-->>Collaborator: invalid or expired session
        else valid token
            JWT->>DB: reload user from sub claim

            alt user missing
                DB-->>JWT: not found
                JWT-->>Common: user no longer exists
                Common-->>Command: exit code 1
            else inactive user
                DB-->>JWT: inactive user
                JWT-->>Common: account inactive
                Common-->>Command: exit code 1
            else active user
                DB-->>JWT: persisted active user
                JWT-->>Common: current user
                Common-->>Command: current user
                Command->>Service: execute business use case
                Service->>Service: authorize role, ownership and assignment

                alt permission denied
                    Service-->>Command: PermissionError
                    Command-->>Collaborator: permission denied
                else authorized
                    Service->>Models: read or update domain data
                    Models-->>Service: result
                    Service-->>Command: business result
                    Command-->>Collaborator: success output
                end
            end
        end
    end
```

## Logout sequence

```mermaid
sequenceDiagram
    actor Collaborator
    participant CLI as auth logout
    participant JWT as core.jwt_auth
    participant File as .epic_events_token.json

    Collaborator->>CLI: logout
    CLI->>JWT: delete_token()

    alt token file exists
        JWT->>File: delete file
        JWT-->>CLI: true
        CLI-->>Collaborator: logged out successfully
    else no token file
        JWT-->>CLI: false
        CLI-->>Collaborator: no active session
    end
```

## Authentication state model

```mermaid
stateDiagram-v2
    [*] --> LoggedOut

    LoggedOut --> Authenticated: valid login
    LoggedOut --> LoggedOut: invalid credentials

    Authenticated --> Authenticated: protected command + valid token + active user
    Authenticated --> LoggedOut: logout
    Authenticated --> Expired: expiration reached
    Authenticated --> Invalid: token altered or malformed
    Authenticated --> RevokedByState: user deleted or deactivated

    Expired --> LoggedOut: new login required
    Invalid --> LoggedOut: new login required
    RevokedByState --> LoggedOut: new authorization required
```

## Security boundary

```mermaid
flowchart TD
    INPUT["Untrusted CLI input"]
    LOGIN["Credential authentication"]
    SIGNED["Signed JWT"]
    LOCAL["Local token file"]
    VERIFY["Signature and expiration validation"]
    RELOAD["Reload user from SQLite"]
    ACTIVE["Check account active"]
    AUTHORIZE["Service-layer authorization"]
    ACTION["Business action"]

    INPUT --> LOGIN
    LOGIN --> SIGNED
    SIGNED --> LOCAL
    LOCAL --> VERIFY
    VERIFY --> RELOAD
    RELOAD --> ACTIVE
    ACTIVE --> AUTHORIZE
    AUTHORIZE --> ACTION
```

The token crosses the authentication boundary but does not cross the authorization boundary by itself.

Authorization requires current persisted data and service-layer rules.

## JWT payload

```text
{
  "sub": "<user_id>",
  "email": "<user_email>",
  "department": "<user_department>",
  "iat": "<issued_at>",
  "exp": "<expiration>"
}
```

### Authoritative data

| Data | Source of truth |
|---|---|
| Token integrity | JWT signature |
| Token validity period | `iat` and `exp` |
| User identifier | `sub` claim, confirmed in SQLite |
| Account existence | SQLite |
| Account active status | SQLite |
| Current department | SQLite |
| Business permissions | Service layer |
| Ownership and assignment | Service layer and database relations |

## Domain model reminder

```mermaid
classDiagram
    class User {
        +id
        +full_name
        +email
        +password_hash
        +department
        +is_active
    }

    class Client {
        +id
        +full_name
        +email
        +phone
        +company_name
        +created_at
        +updated_at
        +sales_contact_id
    }

    class Contract {
        +id
        +client_id
        +sales_contact_id
        +total_amount
        +remaining_amount
        +created_at
        +is_signed
    }

    class Event {
        +id
        +contract_id
        +support_contact_id
        +name
        +start_date
        +end_date
        +location
        +attendees
        +notes
    }

    User "1" --> "0..*" Client : sales_contact
    User "1" --> "0..*" Contract : sales_contact
    User "1" --> "0..*" Event : support_contact
    Client "1" --> "0..*" Contract
    Contract "1" --> "0..*" Event
```

## Role and authorization summary

| Department | Main permissions |
|---|---|
| Management | Manage collaborators; broad access; assign responsibilities |
| Sales | Manage owned clients and contracts; create related events within authorized scope |
| Support | View assigned information; update assigned events |

The JWT does not grant these permissions directly.

Each service checks the current persisted user's department and the relevant entity relationships.

## Failure paths

The authentication layer rejects access when:

- no token file exists;
- the JSON file is corrupted;
- the `access_token` field is missing;
- the JWT format is invalid;
- the signature is invalid;
- the token is expired;
- the user identifier is invalid;
- the user no longer exists;
- the user account is inactive.

The authorization layer rejects access when:

- the authenticated department lacks the required permission;
- a sales collaborator does not own the relevant resource;
- a support collaborator is not assigned to the event;
- a protected management operation is attempted by another department.

## Test mapping

| Architecture behavior | Test coverage |
|---|---|
| Successful login and protected command | Functional CLI tests |
| Local token isolation | Autouse temporary-path fixtures |
| Complete JWT session flow | `test_jwt_complete_session_flow` |
| Missing token | `test_load_token_rejects_missing_session` |
| Invalid token | `test_decode_access_token_rejects_invalid_token` |
| Expired token | `test_decode_access_token_rejects_expired_token` |
| Inactive user | `test_get_current_user_rejects_inactive_account` |
| Deleted user | `test_get_current_user_rejects_deleted_account` |
| Corrupted JSON | `test_load_token_rejects_invalid_json_file` |
| Missing access token | `test_load_token_rejects_missing_access_token` |
| Logout without session | `test_delete_token_returns_false_when_session_is_missing` |

## Validated state

```text
156 passing tests
77% total coverage
96% coverage for src/core/jwt_auth.py
0 regressions
```

## Next architectural version

A future UML version may document:

- final README execution workflow;
- deployment or packaging choices;
- centralized logging and monitoring flow;
- any final changes made during clean-install validation.
