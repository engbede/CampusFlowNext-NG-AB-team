# CampusFlow Next — Baseline and Inspection Record (Engineer A)

## 1. Verified Baseline Commit and Working Tree
- **Baseline Commit**: `c50c1f75916dd84041bddf5144fa75dbf39defd5`
- **Commit Message**: `feat: implement ticket workflow, lifecycle, reporting, CLI, and comprehensive test suite`
- **Branch at Start**: `main`
- **Feature Branch Created**: `feat/engineer-a-validation-notes-persistence`
- **Working Tree Status**: Clean (no uncommitted modifications or untracked changes at baseline).

## 2. Baseline Test Execution
- **Test Command**: `python3 -m unittest discover -s tests -v`
- **Execution Timestamp**: 2026-10-14 12:34:08 +01:00
- **Test Results**:
  - Ran 78 tests across 5 test modules (`test_cli.py`, `test_reports.py`, `test_storage.py`, `test_ticket_manager.py`, `test_tickets.py`).
  - Result: `OK` (78 tests passed, 0 failures, 0 errors, 0 skipped).
  - Runtime: 0.381s.

## 3. Inspected Modules and Public Functions

### `campusflow/tickets.py`
- `calculate_priority(urgency, affected_users)`: Deterministic priority calculation based on urgency (`high`, `medium`, `low`) and affected user count (rejecting booleans and non-integers).
- `create_ticket(tickets, title, category, urgency, affected_users)`: Validates title, category, urgency, users, generates sequential ID `Txxx`, and appends ticket record (currently without `notes` field).
- `assign_ticket(tickets, ticket_id, staff_name)`: Validates staff name, rejects assignment if ticket status is `resolved`.
- `change_status(tickets, ticket_id, new_status)`: Validates status against `VALID_STATUSES`, requires assignment before `in_progress`, rejects transitioning a `resolved` ticket without explicit reopening.
- `reopen_ticket(tickets, ticket_id)`: Reopens a ticket, changing its status to `open`.
- `get_work_queue(tickets)`: Filters out `resolved` tickets, sorts unresolved by priority order and numeric ID.

### `campusflow/storage.py`
- `load_tickets(path)`: Loads JSON array of tickets, validating required fields, categories, urgency, affected user count, priority calculation, statuses, assignments, and ticket ID uniqueness. Returns `[]` if path does not exist.
- `save_tickets(tickets, path)`: Validates collection, writes to atomic temporary file in destination directory, flushes/syncs, and replaces destination.

### `campusflow/reports.py`
- `generate_report(tickets)`: Aggregates total tickets, status counts, and priority counts.

### `campusflow/cli.py`
- `main(data_file=None)`: Interactive CLI loop.
- Individual menu actions: `create_ticket_menu`, `display_tickets`, `show_work_queue`, `assign_ticket_menu`, `change_status_menu`, `reopen_ticket_menu`, `show_report`, `format_ticket`.

### Root Forwarding Shims
- `ticket_manager.py`: Forwards to `campusflow.tickets`.
- `storage.py`: Forwards to `campusflow.storage`.
- `reports.py`: Forwards to `campusflow.reports`.
- `main.py`: Forwards to `campusflow.cli.main`.

## 4. Manual Verification Checks
- Verified CLI entry points: `python3 main.py` and `python3 -m campusflow`.
- Checked data storage paths: `data/tickets.json` and fallback `tickets.json` (neither existed initially; safe from accidental overwrite).
- Formatter check: Checked for `black` (`python3 -m black --version`); black is not installed in the standard environment. PEP 8 standard style matching existing code will be strictly followed.

## 5. Audit Evidence Limitations
- **No external audit report was provided or present in the repository.**
- Findings recorded here are strictly grounded in direct inspection of the codebase, Git history (`git log`), working tree status (`git status`), and test runner output (`python3 -m unittest discover -s tests -v`).
- No claims of prior external audits, external security assessments, or imaginary historical reviews are made.
