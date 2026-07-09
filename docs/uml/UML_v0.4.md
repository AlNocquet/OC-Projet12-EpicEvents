# UML v0.4 - Domain model

## Status

Work in progress

## Date

2026-07-09

## Evolution

Compared to UML v0.3:

- Added the authentication workflow.
- Added the user creation workflow.
- Introduced the authentication and authorization modules.

---

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

- id
- contract -> Contract
- support_contact -> User
- event_name
- location
- attendees
- event_start
- event_end
- notes

Relationship:

- One Event belongs to one Contract.
- One Event can be assigned to one Support User.

---

## Current relationships

User (Sales)
      │
      ▼
+-----------+
|  Client   |
+-----------+
      │
      ▼
+-----------+
| Contract  |
+-----------+
      │
      ▼
+-----------+
|   Event   |
+-----------+
      ▲
      │
User (Support)

---

## Authentication workflow

CLI (Typer)
      │
      ▼
authenticate_user()
      │
      ▼
Authenticated User

---

## User creation workflow

CLI (Typer)
      │
      ▼
create_user_account_command()
      │
      ▼
create_user()
      │
      ▼
User

---

## Authorization workflow

Authenticated User
      │
      ▼
require_permission()
      │
      ▼
Access Granted
      │
      ▼
Protected Command