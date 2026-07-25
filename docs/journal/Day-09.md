# Day 09 — JWT authentication and persistent CLI session

## Objectives

- Replace repeated credential prompts with JWT-based authentication.
- Create a persistent local CLI session after login.
- Authenticate subsequent commands from the stored JWT.
- Preserve service-layer authorization and the principle of least privilege.
- Prevent stale tokens from granting access to deleted or inactive users.
- Adapt the functional CLI tests to the new session workflow.
- Add dedicated integration tests for JWT creation, validation and storage.

## Work completed

### JWT configuration

- Added PyJWT to the project dependencies.
- Added JWT configuration values to `src/core/config.py`.
- Added a secret-key getter using the `JWT_SECRET_KEY` environment variable.
- Configured the HS256 signing algorithm.
- Configured a token lifetime of 60 minutes.
- Added the local token-file path to the centralized configuration.
- Added an empty `JWT_SECRET_KEY` variable to `.env.example`.
- Kept the real JWT secret outside version control.
- Added `.epic_events_token.json` to `.gitignore`.

### JWT engine

Created:

```text
src/core/jwt_auth.py
```

The module now handles:

- JWT creation;
- issued-at and expiration timestamps;
- token signing with HS256;
- token decoding and validation;
- expired-token rejection;
- invalid-token rejection;
- local JSON token storage;
- local token loading;
- local token deletion;
- authenticated-user retrieval from SQLite.

The JWT payload contains:

```text
sub
email
department
iat
exp
```

The `sub` claim stores the collaborator identifier.

### Secure user resolution

The application does not authorize commands solely from the role stored inside the JWT.

After validating the token, the application:

1. reads the collaborator identifier from `sub`;
2. reloads the corresponding user from SQLite;
3. confirms that the account still exists;
4. confirms that the account is still active;
5. passes the current persisted user to the service layer.

This prevents an old but technically valid token from granting access after a collaborator has been deleted or deactivated.

### CLI authentication workflow

Updated:

```text
src/cli/auth.py
src/cli/common.py
```

The login command now:

1. requests the collaborator password;
2. validates the credentials;
3. creates a signed JWT;
4. stores the token in the local session file;
5. confirms successful authentication.

The logout command now removes the local token file.

The management-access demonstration command now reads the authenticated collaborator from the JWT session instead of requesting credentials again.

### Business command migration

Updated:

```text
src/cli/client.py
src/cli/contract.py
src/cli/event.py
src/cli/monitoring.py
src/cli/user.py
```

Removed the repeated authenticated-email argument from protected business commands.

Each protected command now:

1. loads the stored JWT;
2. validates the token;
3. reloads the active collaborator from SQLite;
4. delegates the operation to the appropriate service.

The service layer remains responsible for business permissions, ownership rules and assignment restrictions.

### Session behavior

Without a stored token, protected commands stop with:

```text
No authentication token found. Please log in.
```

A successful login creates:

```text
.epic_events_token.json
```

A successful logout removes that file.

The token file and the real JWT secret are excluded from Git.

## Tests

### Functional tests

Updated:

```text
tests/functional/test_cli.py
```

The functional tests now:

- isolate the JWT secret;
- isolate the local token file inside a temporary directory;
- authenticate through the public login command;
- execute protected commands without passing credentials repeatedly;
- validate role-based CLI refusals through the active JWT session;
- preserve the existing Sentry command scenarios.

Functional validation:

```text
9 passed
```

### JWT integration tests

Created:

```text
tests/integration/test_jwt_auth.py
```

The integration tests validate:

- complete token creation and session-storage flow;
- JWT decoding;
- persisted-user resolution;
- missing token-file rejection;
- invalid-token rejection;
- expired-token rejection;
- inactive-user rejection;
- deleted-user rejection;
- corrupted JSON-file rejection;
- missing `access_token` rejection;
- safe logout when no session exists.

JWT integration validation:

```text
9 passed
```

### Complete regression suite

Command:

```powershell
python -m pytest -q
```

Result:

```text
156 passed
0 failed
```

No regression was introduced in:

- credential authentication;
- collaborator management;
- client management;
- contract management;
- event management;
- authorization;
- database access;
- Sentry monitoring.

### Coverage

Command:

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

Result:

```text
TOTAL: 77%
src/core/jwt_auth.py: 96%
```

The previous complete suite contained 147 tests with 76% coverage.

The JWT branch now contains 156 tests with 77% coverage.

No superficial tests were added solely to inflate the coverage percentage.

## Decisions

- Use JWT for persistent CLI authentication.
- Use HS256 because the application is a local CLI with one trusted token issuer.
- Keep the JWT secret in the environment.
- Never commit the real secret or local token file.
- Store the local session as JSON outside the source packages.
- Limit token lifetime to 60 minutes.
- Store the collaborator identifier in the standard `sub` claim.
- Reload the collaborator from SQLite for every protected command.
- Do not trust the department claim as the source of authorization.
- Keep service-layer permission checks unchanged.
- Keep login credential validation inside the existing authentication module.
- Keep token lifecycle responsibilities inside `src/core/jwt_auth.py`.
- Keep CLI session retrieval inside `src/cli/common.py`.
- Isolate JWT configuration and token files during automated tests.

## Security properties

The implementation now provides:

```text
password authentication
+
bcrypt password verification
+
signed JWT session
+
token expiration
+
local secret management
+
active-user verification
+
database-backed role verification
+
service-layer authorization
+
least-privilege enforcement
```

A copied or stale token cannot authenticate a collaborator when:

- its signature is invalid;
- it has expired;
- its local JSON file is corrupted;
- its user no longer exists;
- its user account has been deactivated.

## Lessons learned

- Authentication state and authorization rules are separate concerns.
- A signed JWT proves token integrity but does not prove that the account is still authorized.
- Persisted user data must remain the source of truth.
- Claims can assist identification without replacing database-backed permissions.
- Test isolation is essential when authentication creates local files.
- Functional tests must reproduce the real login workflow instead of bypassing it.
- A persistent CLI session improves usability without weakening service-layer controls.

## Result

The application now supports:

```text
one credential-based login
+
one locally stored signed JWT
+
multiple authenticated CLI commands
+
database-backed authorization
+
explicit logout
```

Validated status:

```text
156 passing tests
77% total coverage
96% JWT module coverage
0 regressions
```

## Next steps

- Add ADR-009 documenting the JWT and local-session decision.
- Add UML v1.1 documenting the complete authentication flow.
- Update the README installation, configuration and command examples.
- Validate a clean installation from the README.
- Prepare the final architecture documentation for the project defense.
