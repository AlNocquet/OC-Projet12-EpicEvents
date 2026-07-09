# UML v0.2 - Domain model

## Status

Work in progress

## Date

2026-07-01

## Evolution

Compared to UML v0.1:

- Added the Contract entity.
- Added the relationship between Client and Contract.
- Added the relationship between User and Contract.
- Event entity postponed to UML v0.3.


## Entities

### User
- id
- full_name
- email
- password_hash
- department
- is_active

Relationship:
- One User (Sales) can manage several Clients.
- One User (Sales) can manage several Contracts.

---

### Client
- id
- full_name
- email
- phone
- company_name
- created_at
- updated_at
- sales_contact -> User

Relationship:
- One Client belongs to one Sales User.
- One Client can have several Contracts.

---

### Contract
- id
- client -> Client
- sales_contact -> User
- total_amount
- amount_due
- created_at
- is_signed

Relationship:
- One Contract belongs to one Client.
- One Contract belongs to one Sales User.

---

### Event

(To be implemented in UML v0.3)

## Current relationships

User (Sales)
      │
      │ manages
      ▼
+-----------+
|  Client   |
+-----------+
      │
      │ owns
      ▼
+-----------+
| Contract  |
+-----------+

(Event → UML v0.3)