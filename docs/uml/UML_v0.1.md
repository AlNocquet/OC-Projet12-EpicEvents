# UML v0.1 - Domain model

## Status

Draft

## Date

2026-07-01

## Purpose

Initial business domain identification before implementation.

## Entities

### User
- id
- full_name
- email
- password_hash
- department
- is_active

### Client
- id
- full_name
- email
- phone
- company_name
- created_at
- updated_at
- sales_contact -> User

## Relationships

- One User (Sales) can manage several Clients.

## Current relationships

User (Sales)
      │
      ▼
+-----------+
|  Client   |
+-----------+