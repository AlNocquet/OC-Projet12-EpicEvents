# Day 02

## Objectives

- Implement the authentication module.
- Secure user authentication.
- Introduce role-based authorization.
- Create the user service layer.
- Add the first authentication CLI commands.

## Decisions

- Separate authentication from business logic.
- Delegate user creation to a dedicated service.
- Hash passwords before storing them in the database.
- Verify passwords using Passlib and bcrypt.

## Lessons learned

- Authentication and authorization are different concepts.
- Business logic should remain outside the CLI layer.
- Passwords must never be stored in plain text.
- Passlib simplifies secure password hashing and verification.

## Next steps

- Write authentication tests.
- Validate role-based permissions.
- Commit the authentication feature.