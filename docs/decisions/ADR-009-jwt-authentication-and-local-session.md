# ADR-009 — JWT authentication and local CLI session

## Status

Accepted.

## Date

2026-07-25

## Context

Epic Events is a command-line CRM application used by collaborators from the management, sales and support departments.

Before this decision, each protected CLI command required the collaborator to provide an email address and password again. This approach validated credentials correctly but created several problems:

- repeated password entry for every command;
- poor user experience;
- duplicated authentication logic across CLI modules;
- difficulty demonstrating a realistic authenticated session;
- greater risk of coupling authentication concerns to business commands.

The application already enforced authorization rules in the service layer. The new authentication mechanism therefore had to improve session management without moving business permissions into the token or weakening the principle of least privilege.

The solution also had to satisfy the following security constraints:

- no secret committed to Git;
- no plaintext password stored locally;
- short-lived authentication;
- rejection of invalid or expired sessions;
- immediate refusal when a user is deleted or deactivated;
- continued database-backed authorization;
- compatibility with a local Python CLI.

## Decision

Use a signed JSON Web Token as the local CLI authentication session.

The user authenticates once with an email address and password. After successful bcrypt verification, the application creates a signed JWT and stores it in a local JSON file.

Subsequent protected commands load and validate this token instead of requesting credentials again.

### Token configuration

The JWT is configured with:

```text
Algorithm: HS256
Expiration: 60 minutes
Secret source: JWT_SECRET_KEY environment variable
Local file: .epic_events_token.json
```

The real secret and local token file are excluded from version control.

### Token claims

The token contains:

```text
sub
email
department
iat
exp
```

The standard `sub` claim contains the user identifier.

The `email` and `department` claims provide useful session context, but they are not treated as the authoritative source for permissions.

### User validation after token decoding

For every protected command, the application:

1. loads the local token;
2. validates its signature;
3. checks its expiration;
4. reads the user identifier from `sub`;
5. reloads the user from SQLite;
6. confirms that the account exists;
7. confirms that the account is active;
8. sends the persisted user object to the service layer.

The database remains the source of truth for the user account and department.

### Authorization

The JWT proves that the session was issued by the application and has not expired.

It does not replace authorization.

The existing service layer continues to enforce:

- department-based permissions;
- ownership restrictions;
- collaborator assignment rules;
- management-only operations;
- commercial and support scopes;
- least-privilege rules.

### Responsibility separation

Authentication responsibilities are divided as follows:

```text
src/core/auth.py
    Credential verification and bcrypt password checking

src/core/jwt_auth.py
    Token creation, validation, storage, loading and deletion

src/cli/common.py
    Retrieval of the authenticated CLI session

src/cli/auth.py
    Login, logout and authentication-related commands

src/services/*
    Business authorization and permission enforcement
```

## Alternatives considered

### Re-enter credentials for every command

Rejected.

Advantages:

- no persistent session file;
- simple mental model.

Disadvantages:

- poor user experience;
- repetitive password handling;
- duplicated CLI arguments;
- authentication logic repeated throughout the application;
- less realistic usage during the defense demonstration.

### Store the email address only

Rejected.

An email address stored locally would not prove that authentication had occurred and could be modified trivially.

### Store the password locally

Rejected.

Persisting a password would create an unacceptable security risk, even if the file were ignored by Git.

### Use a server-side session database

Rejected for this project.

The application is a local CLI without an application server. A server-side session store would add infrastructure and complexity without a proportional benefit.

### Use asymmetric JWT signing

Not selected.

Asymmetric signing is valuable when token creation and token verification are performed by different systems. Epic Events has one trusted local issuer and verifier, so HS256 is sufficient for the current architecture.

### Trust the department stored in the JWT

Rejected.

A token may remain valid after a user's department, status or existence changes. Reloading the user from SQLite ensures that current persisted data controls authorization.

## Consequences

### Positive consequences

- users authenticate once per session;
- protected commands no longer request credentials repeatedly;
- passwords are never written to the local session file;
- tokens expire automatically;
- invalid or corrupted tokens are rejected;
- deleted and inactive users lose access even when holding an unexpired token;
- the database remains the source of truth;
- existing service-layer permissions remain unchanged;
- authentication logic is centralized;
- CLI commands become simpler;
- functional tests can reproduce the real login workflow;
- the architecture is easier to explain during the defense.

### Negative consequences

- the token file is a bearer credential and must be protected by the operating system;
- a copied token can be used until it expires unless the related account is deleted or deactivated;
- HS256 requires the signing secret to remain confidential;
- local clock errors may affect token expiration;
- logout only removes the local file and does not maintain a centralized revocation list.

### Accepted risks

The application is a local educational CLI with a 60-minute token lifetime and no remote API.

The following risks are accepted for the current scope:

- no centralized token revocation list;
- no refresh token;
- no asymmetric key pair;
- no encrypted token file.

These mechanisms would add complexity without being required by the project specifications.

## Security controls

The decision relies on the following controls:

- bcrypt password hashing;
- environment-based secret configuration;
- `.env` excluded from Git;
- `.epic_events_token.json` excluded from Git;
- HS256 signature verification;
- token expiration;
- malformed-token rejection;
- database reload on every protected command;
- active-account validation;
- service-layer authorization;
- automated tests with isolated secrets and temporary token files.

## Validation

The implementation is validated by:

```text
156 passing tests
77% total coverage
96% coverage for src/core/jwt_auth.py
```

Dedicated tests cover:

- creation and decoding;
- local storage and deletion;
- missing session;
- invalid token;
- expired token;
- malformed JSON;
- missing access token;
- deleted user;
- inactive user;
- complete authenticated session flow.

## Follow-up

- Document the authentication flow in UML v1.1.
- Update the README with JWT configuration and command usage.
- Validate installation and execution from a clean environment.
- Review file permissions and token-handling explanations for the defense.
