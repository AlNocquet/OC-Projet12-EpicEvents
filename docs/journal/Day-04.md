# Day 04

## Objectives

- Start the `feature/contract-management` branch from the validated `main` branch.
- Implement contract business logic in a dedicated service.
- Add contract-management CLI commands without removing previous features.
- Apply role-based and ownership-based permissions.
- Validate monetary values and signature status.
- Document the contract architecture and authorization decisions.
- Prepare the automated test scope for contract management.

## Work completed

### Branch preparation

- Created the local `feature/contract-management` branch from the synchronized `main` branch.
- Kept the remote branches from previous features available for project evaluation.
- Preserved the existing authentication, collaborator-management and client-management implementation.

### Contract service

- Created `src/services/contract_service.py`.
- Added contract creation restricted to active management collaborators.
- Automatically derived the contract commercial contact from the related client's `sales_contact`.
- Added read-only access to all contracts for active commercial, support and management collaborators.
- Added contract updates for active management collaborators.
- Added contract updates for active commercial collaborators only when they are responsible for the related client.
- Synchronized the contract commercial contact with the related client's current commercial contact during updates.
- Added commercial filters for unsigned contracts and contracts that are not fully paid.
- Excluded contract deletion because it is not required by the specifications.

### Data validation

- Converted monetary input to `Decimal`.
- Rejected invalid and non-finite monetary values.
- Required the total amount to be greater than zero.
- Prevented a negative remaining amount.
- Prevented the remaining amount from exceeding the total amount.
- Required the signature status to be a Boolean value.
- Rejected unknown client and contract identifiers.

### Authorization and security

- Enforced permissions inside the contract service rather than only in the CLI.
- Checked the authorized department before loading a contract for an update.
- Combined role-based authorization with client ownership for commercial updates.
- Preserved Peewee parameterized queries to limit SQL injection risks.
- Kept business rules outside `main.py`.

### CLI integration

- Added contract service imports to `src/main.py`.
- Added a reusable contract-display helper.
- Added contract creation for management collaborators.
- Added consultation of all contracts for every authenticated collaborator.
- Added commercial filters for unsigned and unpaid contracts.
- Added contract updates for management and responsible commercial collaborators.
- Preserved all commands from the authentication, collaborator and client branches.

### Documentation

- Added `ADR-004-contract-management.md`.
- Added `UML_v0.6.md`.
- Created this separate `Day-04.md` journal entry without modifying `Day-03.md`.

## Decisions

- Contract business rules remain in `src/services/contract_service.py`.
- Authentication and reusable authorization remain in `src/auth.py`.
- The CLI delegates contract operations to the service layer.
- Contract creation is restricted to management collaborators.
- Commercial ownership is determined from the client linked to the contract.
- The contract commercial contact is derived from and synchronized with the client commercial contact.
- Commercial filters apply to all contracts, while update permissions remain ownership-restricted.
- Contract deletion remains outside the project scope.

## Testing status

The complete automated test suite was executed successfully with:

- Python 3.12.2;
- pytest 9.1.1;
- 96 tests collected;
- 96 tests passed;
- 0 failures;
- execution time: 131.39 seconds.

The contract test suite validates:

- contract creation by management;
- automatic association with the client's commercial contact;
- rejection of unauthorized and inactive users;
- rejection of unknown client and contract identifiers;
- validation of finite monetary values;
- validation of positive total amounts;
- validation of non-negative remaining amounts;
- prevention of a remaining amount greater than the total amount;
- strict Boolean validation of the signature status;
- read access for commercial, support and management collaborators;
- commercial filters for unsigned and unpaid contracts;
- management updates of all contracts;
- commercial updates restricted to contracts belonging to their clients;
- authorization checks before contract lookup;
- synchronization of the contract commercial contact after client reassignment.

All authentication, collaborator, client and database tests also continue to pass, confirming that the contract feature introduces no regression.

## Lessons learned

- Visibility permissions and modification permissions must remain separate.
- Role checks do not replace ownership checks.
- Monetary data requires explicit decimal validation.
- A duplicated relationship must be synchronized to prevent inconsistent data.
- Authorization order can reduce information disclosure through error differences.
- Incremental documentation must preserve previous UML, ADR and journal versions.

## Next steps

- Commit documentation, code and tests separately.
- Push `feature/contract-management` while keeping the remote branch visible.
- Merge the branch locally into `main`.
- Push the updated `main` branch.
- Delete only the local feature branch.
- Start `feature/event-management`.
