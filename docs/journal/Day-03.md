# Day 03

## Objectives

- Correct the remaining authentication and collaborator-management inconsistencies.
- Complete collaborator creation, update and deletion according to the specifications.
- Implement the client service layer.
- Add client-management CLI commands.
- Apply role-based and ownership-based permissions.
- Reorganize business services inside a dedicated `services` package.
- Add automated tests for client management.

## Work completed

### Authentication and authorization corrections

- Prevented inactive collaborators from authenticating.
- Prevented inactive collaborators from receiving permissions.
- Restricted collaborator management to active users from the management department.
- Secured CLI password entry with hidden prompts.
- Kept authentication and reusable authorization rules in the transversal `src/auth.py` module.

### Collaborator management

- Added creation of the initial management account.
- Added collaborator creation by management users.
- Added collaborator updates by management users.
- Added collaborator deletion through account deactivation.
- Prevented a management user from removing their own management role.
- Prevented a management user from deactivating their own account.
- Preserved related CRM records by using soft deletion through `is_active`.

### Client management

- Added client creation by commercial users.
- Automatically associated each new client with the authenticated commercial user.
- Added read-only access to all clients for active commercial, support and management users.
- Added client updates restricted to the assigned commercial user.
- Added client-data normalization and validation.
- Added duplicate-email protection.
- Updated the client's last-modification date during updates.
- Did not add client deletion because it is not required by the specifications.

### Project organization

- Created the `src/services` package.
- Moved `user_service.py` and `client_service.py` into the service layer.
- Kept `auth.py` at the root of `src` because authentication and authorization are transversal concerns.
- Kept business logic outside `main.py`.

### Tests

- Updated the existing authentication and collaborator tests.
- Added reusable client fixtures.
- Added client-service tests covering permissions, ownership, validation, inactive users and duplicate emails.
- Confirmed that the complete current test suite passes.

## Decisions

- Business services are grouped under `src/services`.
- Authentication remains outside the service package as a transversal security module.
- Authorization is enforced inside services, not only in the CLI.
- Collaborator deletion is implemented as deactivation.
- Client updates require both the commercial role and ownership of the client.
- Client deletion is excluded from the current scope because the specifications do not require it.
- Test classification into unit, integration and functional suites will be performed during final project organization, after all business branches are complete.

## Lessons learned

- Authentication verifies identity, while authorization verifies allowed actions.
- Role checks alone are not sufficient when ownership also matters.
- Security rules must be enforced in the business layer even when the CLI already authenticates the user.
- Soft deletion preserves relational integrity while preventing future access.
- A service package improves maintainability without forcing transversal modules into the same category.
- Existing tests can later be reorganized by type without rewriting the entire suite.

## Next steps

- Commit the documentation, code and tests separately.
- Merge the completed `feature/client-management` branch locally.
- Start `feature/contract-management`.
- Create a consolidated final architecture document in `docs/architecture/` during project finalization without replacing the historical UML and ADR files.
