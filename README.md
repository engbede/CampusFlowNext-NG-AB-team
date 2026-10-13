# CampusFlow Helpdesk CLI

CampusFlow is a Python command-line helpdesk application being developed
during a collaborative engineering sprint. It helps a support team create,
prioritize, assign, track, and report on support tickets.

## Project goals

- Validate ticket information consistently.
- Calculate ticket priority using deterministic business rules.
- Assign tickets to support staff and manage their lifecycle.
- Present an ordered work queue.
- Report ticket totals and breakdowns.
- Persist ticket data in JSON.
- Verify behavior with automated unit tests.
- Practice Git branches, pull requests, peer reviews, and integration.

## Ticket data model

Each ticket uses the following fields:

| Field | Purpose |
|---|---|
| `id` | Unique sequential identifier, such as `T001` |
| `title` | Nonblank summary of the issue |
| `category` | `Network`, `Hardware`, `Software`, or `Other` |
| `urgency` | `low`, `medium`, or `high` |
| `affected_users` | Positive integer count of affected users |
| `priority` | Calculated priority: `low`, `medium`, `high`, or `critical` |
| `status` | `open`, `in_progress`, or `resolved` |
| `assigned_to` | Staff member's name, or `None` if unassigned |

## Priority rules

Priority is calculated in this order:

1. `critical`: urgency is `high` and at least 10 users are affected.
2. `high`: urgency is `high`, or at least 10 users are affected.
3. `medium`: urgency is `medium`, or at least 3 users are affected.
4. `low`: none of the conditions above apply.

Urgency input should be normalized to lowercase. Invalid values and
non-positive or non-integer user counts must be rejected.

## Ticket lifecycle and work queue

The agreed lifecycle is:

`open` -> `in_progress` -> `resolved`

A ticket must be assigned before it can move to `in_progress`.
A resolved ticket must be explicitly reopened before further changes
that require it to be open.

The work queue should contain open tickets ordered by priority
(`critical`, `high`, `medium`, `low`), then by numeric ticket ID.

## JSON persistence requirements

The persistence layer should:

- Return an empty ticket list when the data file does not exist.
- Load valid JSON ticket collections.
- Reject malformed JSON and structurally invalid ticket data clearly.
- Reject duplicate ticket IDs and inconsistent priority values.
- Avoid overwriting existing data when the proposed data is invalid.
- Save through a temporary file and replace the destination atomically.

## Development setup

Use Python 3 and a virtual environment.

Activate the virtual environment in your shell, then run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

Format the ticket and storage modules with Black when changing them:

```bash
python3 -m black campusflow tests
```

## Current repository structure

```text
campusflow/
    __init__.py
    tickets.py
    storage.py
    reports.py
    cli.py
    __main__.py
tests/
    __init__.py
    test_tickets.py
    test_storage.py
    test_reports.py
    test_ticket_manager.py
    test_cli.py
main.py
ticket_manager.py
reports.py
storage.py
README.md
```

This structure describes the fully implemented files across the package, CLI,
and test suite. Assignment, lifecycle, reporting, work queue, persistence, and
CLI integration are all implemented and verified by automated unit tests.

## Running the CLI

You can start the interactive CLI helpdesk application using either:

```bash
python3 main.py
```

or:

```bash
python3 -m campusflow
```

## Team workflow

1. Create a focused branch from `main`.
2. Implement a small, well-defined change with tests.
3. Run the relevant tests and then the full test suite.
4. Format the code and inspect the Git diff.
5. Commit and push the feature branch.
6. Open a pull request targeting `main`.
7. Obtain genuine peer review and approval before merging.
8. Synchronize local `main` after the merge.

Do not claim a feature is merged or tested unless the repository and test
results provide evidence for that claim.
