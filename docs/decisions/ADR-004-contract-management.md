# ADR-004 - Contract management and authorization

## Status

Accepted

---

## Date

2026-07-14

---

## Context

The application now contains authentication, collaborator management and client management.

Epic Events must also store and update contracts associated with clients. According to the project specifications, a contract contains:

- a unique identifier;
- the related client;
- the commercial contact associated with that client;
- the total contract amount;
- the remaining amount due;
- the contract creation date;
- the contract signature status.

The specifications define the following permissions:

- every authenticated collaborator can consult all contracts in read-only mode;
- management collaborators can create contracts;
- management collaborators can modify every contract;
- commercial collaborators can modify contracts belonging to clients for whom they are responsible;
- commercial collaborators can filter contracts that are unsigned or not fully paid.

The contract feature must preserve the existing separation between the CLI, transversal authentication and authorization rules, business services and Peewee models.

---

## Problem

How should contract operations be implemented so that:

- the contract remains consistent with its associated client;
- financial information is validated before persistence;
- every department receives only the permissions required by the specifications;
- commercial ownership is enforced during updates;
- business rules remain outside the CLI;
- unauthorized departments cannot use update operations to discover whether a contract identifier exists?

---

## Decision

Contract business logic is implemented in:

```text
src/services/contract_service.py
```

Contract CLI commands are implemented in:

```text
src/main.py
```

The existing Peewee entity remains in:

```text
src/models/contract.py
```

### Contract creation

Only an authenticated and active management collaborator can create a contract.

The service receives:

- a client identifier;
- a total amount;
- a remaining amount due;
- a signature status.

The commercial contact is not selected manually. It is automatically derived from:

```text
client.sales_contact
```

This ensures that the commercial collaborator stored on the contract is the collaborator responsible for the related client.

### Contract consultation

All authenticated and active collaborators from the following departments can consult all contracts:

- `COMMERCIAL`;
- `SUPPORT`;
- `MANAGEMENT`.

This access is read-only.

### Contract update

An authenticated and active management collaborator can update every contract.

An authenticated and active commercial collaborator can update a contract only when the related client is assigned to them.

Commercial ownership is verified using:

```text
contract.client.sales_contact_id == current_user.id
```

Whenever a contract is updated, its stored commercial contact is synchronized with the commercial contact currently assigned to the related client.

### Contract filters

Authenticated and active commercial collaborators can filter the complete contract list to display:

- contracts that have not yet been signed;
- contracts with an amount still due.

These filters grant visibility only. They do not allow a commercial collaborator to modify contracts belonging to another commercial collaborator's clients.

### Financial validation

Contract amounts are converted to `Decimal` values before persistence.

The following rules are enforced:

- the total amount must be a valid finite number;
- the total amount must be greater than zero;
- the remaining amount due must be a valid finite number;
- the remaining amount due cannot be negative;
- the remaining amount due cannot exceed the total amount.

The signature status must be a Boolean value.

### Authorization order

For contract updates, the service first verifies that the current user belongs to either the management or commercial department.

The contract is loaded only after this role check succeeds.

This prevents support users and other unauthorized callers from using different error messages to determine whether a contract identifier exists.

### Contract deletion

Contract deletion is not implemented because it is not required by the project specifications.

---

## Rationale

### Dedicated contract service

Keeping contract business rules inside a dedicated service:

- prevents business logic from being duplicated in CLI commands;
- makes authorization rules reusable;
- simplifies automated testing;
- preserves the service-layer architecture;
- keeps `main.py` focused on terminal input and output.

### Commercial contact derived from the client

The specifications define the contract commercial contact as the commercial collaborator associated with the client.

Allowing an unrelated commercial collaborator to be selected manually could create inconsistent data.

Deriving the value from the client prevents this inconsistency.

### Decimal monetary values

Using `Decimal` avoids binary floating-point inaccuracies when storing and comparing monetary values.

### Role and ownership checks

A department check alone is insufficient for commercial updates.

Commercial collaborators must also own the client related to the contract.

This combines:

- role-based authorization;
- ownership-based authorization;
- the principle of least privilege.

### Global commercial filters

The specifications allow commercial collaborators to display contracts that are unsigned or not fully paid.

The filters therefore apply to the complete contract list.

Modification permissions remain separately restricted to contracts belonging to the commercial collaborator's own clients.

---

## Consequences

### Positive

- Contract permissions comply with the project specifications.
- Financial values are validated before database persistence.
- Contract and client commercial contacts remain consistent.
- Every active collaborator retains read-only access to all contracts.
- Commercial ownership is enforced for contract updates.
- Business rules remain independent from the CLI.
- Peewee queries remain parameterized, limiting SQL injection risks.
- The service can be tested independently from terminal interaction.

### Negative

- The commercial contact is stored on both the client and the contract.
- The contract service must synchronize that value during updates.
- Contract updates currently receive the complete mutable financial state instead of partial changes.
- Contract deletion is unavailable.

---

## Alternatives considered

### Allow management to select the contract commercial contact

Rejected because the specifications define the contract commercial contact as the commercial collaborator associated with the client.

Manual selection could introduce inconsistent relationships.

### Allow commercial collaborators to create contracts

Rejected because contract creation belongs to the management department.

### Restrict commercial filters to their own contracts

Rejected because the specifications describe filters displaying all contracts that are unsigned or not fully paid.

The filters provide visibility only and do not change contract modification permissions.

### Implement authorization only in the CLI

Rejected because service functions could then be called directly without applying the required permissions.

Authorization must be enforced in the business layer.

### Use floating-point values for monetary data

Rejected because binary floating-point arithmetic is unsuitable for reliable monetary calculations.

### Implement contract deletion

Rejected because contract deletion is not required by the project specifications.

---

## References

- OpenClassrooms Project 12 specifications.
- ADR-001 - Project architecture.
- ADR-002 - Authentication architecture.
- ADR-003 - Service layer organization and client authorization.
- UML v0.5 - Client management and service organization.
- Principle of least privilege.
