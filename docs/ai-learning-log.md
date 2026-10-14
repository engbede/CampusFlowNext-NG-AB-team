# CampusFlow Next — AI Assistance and Learning Log (Engineer A)

## Entry 1: Pre-Implementation Baseline and Role Boundaries
- **Date/Time**: 2026-10-14 12:35:00 +01:00
- **Context**: Reviewing project constraints, role allocation between Engineer A and Engineer B, and baseline state.
- **Inquiry**: How should responsibilities be separated so that Engineer A does not implement Engineer B's scope, and how should backward compatibility be handled for existing ticket records?
- **Guidance Received**:
  - Engineer A owns validation, ticket/note mutations, persistence, ID continuity, and core tests.
  - Engineer B owns title search, combined filters, analytics/reporting, and CLI interactive menus.
  - Public interfaces (`add_note`, `get_notes`) should be defined in business modules without CLI UI logic.
  - Legacy records without notes must be supported gracefully rather than rejected or discarded.
- **Independent Verification**:
  - Inspected existing CLI (`campusflow/cli.py`) and reports (`campusflow/reports.py`) to confirm no CLI display logic touches notes yet.
  - Checked baseline test suite (78 tests passing).
  - Documented findings in `docs/baseline-check.md`.

## Entry 2: Note Data Model and Sequential ID Continuity Strategy
- **Date/Time**: 2026-10-14 12:40:00 +01:00
- **Context**: Designing `add_note` and next note ID generation.
- **Inquiry**: Should note IDs be global or scoped per ticket, and what strategy prevents ID collisions when tickets are saved and loaded?
- **Guidance Received**:
  - Note IDs must be sequential independently for each ticket (e.g. `T001` has `N001`, `N002`; `T002` also starts at `N001`).
  - Next note ID generation should scan the ticket's existing notes and compute `highest_numeric_id + 1`. This guarantees ID continuity even after save/load round trips or if legacy data has non-contiguous IDs.
  - Failed note creations (e.g. invalid author or message length) must abort before allocating an ID or mutating state.
- **Independent Verification**:
  - Implemented `_next_note_id` using regex extraction of numeric suffixes.
  - Added unit test `test_independent_note_id_sequencing_across_tickets`.
  - Added unit test `test_ticket_and_note_id_continuity_after_reload`.
  - Added bug-hunter test `test_non_contiguous_note_ids_continuity`.

## Entry 3: Centralized Validation vs. Duplication in Persistence
- **Date/Time**: 2026-10-14 12:43:00 +01:00
- **Context**: Consolidating validation logic between `tickets.py` and `storage.py`.
- **Inquiry**: How can ticket and note validation be unified without introducing circular imports or breaking existing `storage.py` tests?
- **Guidance Received**:
  - Implement `validate_ticket`, `validate_note`, and `validate_tickets` inside `campusflow/tickets.py`.
  - Import these validators in `campusflow/storage.py` and keep `_validate_ticket = validate_ticket` alias for backward compatibility.
  - Support backward compatibility by accepting ticket dictionaries with exactly `BASE_REQUIRED_FIELDS` or `BASE_REQUIRED_FIELDS | {"notes"}`.
- **Independent Verification**:
  - Executed tests in `test_tickets.py` and `test_storage.py`.
  - Verified that all legacy tests in `test_storage.py` (which use `VALID_TICKET` without `notes`) continue to pass without modification.
  - Added test cases for note schema validation, duplicate note IDs, and invalid field rejection.

## Entry 4: Atomic Save and Mutation Integrity
- **Date/Time**: 2026-10-14 12:45:00 +01:00
- **Context**: Verifying atomic write guarantees and absence of partial mutations.
- **Inquiry**: What tests demonstrate that disk state and memory state are never partially mutated when save or load operations fail?
- **Guidance Received**:
  - For saves: Test that invalid collection data (e.g., invalid priority on the 3rd ticket) aborts save before touching disk, preserving existing files and cleaning up temporary files.
  - For loads: Test that corrupt JSON raises `ValueError` and that the caller's in-memory ticket list remains untouched.
  - For notes: Test that invalid note additions do not mutate existing notes or increment sequence counters.
- **Independent Verification**:
  - Added `test_batch_save_partial_failure_preserves_disk_and_cleans_temp`.
  - Added `test_failed_load_preserves_valid_in_memory_state`.
  - Added `test_invalid_author_does_not_mutate_or_consume_id`.
  - Full test suite passed with 133 tests passing.
