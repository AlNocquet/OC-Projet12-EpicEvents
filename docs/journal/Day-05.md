# Day 05

## Objectives

- Start the `feature/event-management` branch from the validated `main` branch.
- Implement event business logic in a dedicated service.
- Add event-management commands to the Typer CLI.
- Apply role-based, ownership-based and assignment-based permissions.
- Validate event text, attendees and dates.
- Document the event architecture and authorization decisions.
- Add complete automated coverage for event workflows.

## Work completed

### Branch preparation

- Created `feature/event-management` from the synchronized `main` branch.
- Preserved all previous authentication, collaborator, client and contract features.
- Kept previous remote feature branches visible for evaluation.

### Event service

- Created `src/services/event_service.py`.
- Added event creation for active commercial collaborators.
- Restricted creation to contracts belonging to the commercial collaborator's own clients.
- Required the selected contract to be signed.
- Added read-only access to all events for active commercial, support and management collaborators.
- Added a management filter for events without an assigned support contact.
- Added a support filter for events assigned to the authenticated support collaborator.
- Added support assignment restricted to active management collaborators.
- Required the selected support collaborator to exist, be active and belong to the support department.
- Added event updates restricted to the support collaborator assigned to the event.

### Data validation

- Required a non-empty event name.
- Required a non-empty location.
- Required a positive integer attendee count.
- Rejected Boolean and non-integer attendee values.
- Required valid `datetime` values.
- Required the event end date to occur after the start date.
- Normalized optional notes and stored empty notes as `None`.
- Rejected unknown contracts, events and collaborators.

### Authorization and security

- Enforced permissions inside the event service rather than only in the CLI.
- Combined department checks with client ownership for event creation.
- Combined department checks with event assignment for support updates.
- Checked management permission before protected support-assignment lookups.
- Preserved parameterized Peewee queries to limit SQL injection risks.
- Applied the principle of least privilege to every event write operation.

### CLI integration

- Added event service imports to `src/main.py`.
- Added ISO datetime parsing for terminal input.
- Added a reusable event-display helper.
- Added commands for event creation and global consultation.
- Added the management filter for unassigned events.
- Added the support filter for assigned events.
- Added the management support-assignment command.
- Added the support event-update command.
- Preserved all previous CLI commands.

### Tests

- Updated `tests/conftest.py` with reusable signed-contract, second-support and event fixtures.
- Added `tests/test_event_service.py`.
- Covered normal workflows, invalid data, inactive users, unauthorized roles, ownership restrictions and assignment restrictions.
- Executed the complete regression suite successfully.

### Documentation

- Added `ADR-005-event-management.md`.
- Added `UML_v0.7.md`.
- Added this separate `Day-05.md` journal entry.

## Decisions

- Event business logic remains in `src/services/event_service.py`.
- Authentication and reusable department checks remain in `src/auth.py`.
- The CLI parses input and delegates all business decisions to the service.
- Commercial collaborators create events but do not update them.
- Management collaborators assign support contacts but do not receive broader event-update permissions.
- Support collaborators update only the events assigned to them.
- Event deletion remains outside the project scope because it is not required by the specifications.

## Testing status

The complete automated test suite was executed successfully with:

- Python 3.12.2;
- pytest 9.1.1;
- 134 tests collected;
- 134 tests passed;
- 0 failures;
- execution time: 131.47 seconds.

The event test suite validates:

- successful event creation;
- optional-note normalization;
- rejection of unauthorized, inactive and unauthenticated users;
- rejection of unknown and unsigned contracts;
- commercial client-ownership restrictions;
- required event fields;
- attendee validation;
- event-date ordering;
- read access for all three departments;
- management filtering of unassigned events;
- support filtering of assigned events;
- management-only support assignment;
- rejection of unknown, inactive or non-support assignees;
- support updates of assigned events;
- rejection of unassigned or differently assigned event updates;
- authorization checks before protected event lookups;
- validation during event updates.

All authentication, collaborator, client, contract and database tests continue to pass, confirming that the event feature introduces no regression.

## Lessons learned

- A role check alone is insufficient when ownership or assignment also determines access.
- Creation and update permissions can legitimately belong to different departments.
- Authorization order can reduce information disclosure.
- Date and attendee validation must be explicit before persistence.
- Optional data should be normalized consistently.
- A thin CLI makes business rules easier to test and defend during the presentation.

## Next steps

- Commit documentation, code and tests separately.
- Push `feature/event-management` while keeping the remote branch visible.
- Merge the branch locally into `main`.
- Push the updated `main` branch.
- Delete only the local feature branch.
- Start `feature/sentry-and-finalization`.
