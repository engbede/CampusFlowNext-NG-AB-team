# CampusFlow Next — Architecture and Design Decisions (Engineer A)

## 1. Centralized Validation Architecture

### Problem
Previously, validation logic was fragmented between `campusflow/tickets.py` and `campusflow/storage.py`. Both modules independently validated categories, urgency levels, user count constraints, priority calculations, statuses, and staff assignment rules. This duplication risked divergence when adding new entities like ticket notes.

### Decision
- Consolidate canonical validation rules inside `campusflow/tickets.py`:
  - `validate_note(note)`: Strictly checks dictionary structure, required keys `{"note_id", "author", "message"}`, regex format `N[0-9]{3,}`, nonblank author string, and trimmed message length between 5 and 300 characters.
  - `validate_ticket(ticket)`: Validates the 8 core ticket fields plus optional `notes`, verifies regex format `T[0-9]{3,}`, nonblank title, canonical category and urgency, strictly positive integer user count (explicitly rejecting booleans and floats), priority consistency with `calculate_priority`, status/assignment invariants (in-progress requires assignee), and note array structure.
  - `validate_tickets(tickets)`: Validates the entire list collection, checking each ticket and enforcing uniqueness of ticket IDs across the collection and note IDs within each ticket.
- `campusflow/storage.py` delegates all ticket and note structure validation to these centralized validators, eliminating duplication.

## 2. Note Data Model, Container Integrity, and Sequential ID Continuity

### Data Model
```python
{
    "note_id": "N001",
    "author": "Alice",
    "message": "Investigating switch port 3."
}
```

### Decision & Invariants
- **Independent Per-Ticket Scope**: Note IDs are scoped to individual tickets rather than globally across the system. Ticket `T001` has its own sequence (`N001`, `N002`, ...), and Ticket `T002` independently starts at `N001`.
- **Note Container and Entry Integrity**:
  - Legacy tickets lacking a `"notes"` field are accepted for backward compatibility, and `add_note` initializes `ticket["notes"] = []`.
  - If a ticket contains a `"notes"` field that is not a list (e.g. malformed string or dictionary), `add_note` raises `ValueError("Ticket notes must be a list.")` without mutating or overwriting the existing ticket state.
  - Prior to appending a new note, `add_note` validates all existing notes in `ticket["notes"]` using `validate_note` and checks for duplicate note IDs. If any existing note is corrupt, `add_note` raises `ValueError`, preventing silent corruption of sequence counters or masking of defective data.
  - `get_notes` validates that `ticket["notes"]` is a list and each entry satisfies `validate_note(note)` before sorting and returning, preventing uncontrolled `AttributeError` or concealment of malformed note records.
- **High-Water-Mark Sequencing**: Next note ID generation (`_next_note_id`) calculates `max(existing_numeric_ids) + 1`. This safely accommodates non-contiguous legacy IDs (e.g. if a note was removed or historical data was imported with gaps).
- **ID Continuity Across Reload**: When tickets and notes are reloaded from JSON persistence, existing IDs are scanned dynamically. Subsequent calls to `add_note` continue seamlessly from the highest existing ID without collision.
- **Ordered Retrieval**: Notes are returned in note-ID order via `get_notes(tickets, ticket_id)` by sorting on numeric suffix.

## 3. Assignment and Lifecycle Mutation Safety

### Problem
Operations must never partially mutate ticket state when inputs or preconditions are invalid.

### Decision & Invariants
- **Precondition Check Ordering**: Input sanitization and precondition checks (valid ticket existence, nonblank staff name, lifecycle status eligibility) occur prior to any dictionary mutation.
- **Resolved Ticket Protection**:
  - `assign_ticket`: Resolved tickets cannot have their assignee modified unless explicitly reopened first.
  - `change_status`: Resolved tickets cannot transition directly to `in_progress`; they must transition to `open` (or via `reopen_ticket`).
  - `add_note`: Notes cannot be added to resolved tickets; attempting to do so raises `ValueError("Cannot add notes to a resolved ticket.")`.
- **Zero Mutation & Zero ID Consumption on Failure**:
  - If note parameters fail validation (e.g. author is empty, message is under 5 characters) or preconditions fail, `add_note` raises `ValueError` before generating a note or touching `ticket["notes"]`. The next valid note invocation receives the unconsumed ID.

## 4. JSON Persistence and Backward Compatibility

### Problem
Storage must safely handle existing ticket files generated prior to the notes sprint, reject corrupt data, and ensure atomic writes.

### Decision
- **Backward Compatibility for Legacy Records**:
  - The persistence layer recognizes both `BASE_REQUIRED_FIELDS` (8 fields) and `BASE_REQUIRED_FIELDS | {"notes"}` (9 fields).
  - Legacy records loaded without a `"notes"` field are accepted without error and treated as having empty notes (`[]`).
  - When notes are added to a legacy record, `"notes"` is dynamically initialized on the ticket dictionary.
- **Whole-Collection Pre-Validation**:
  - `save_tickets` executes `validate_tickets(tickets)` on the entire collection before touching the filesystem. If any record or note is invalid, saving is aborted.
- **Atomic Replacement & Robust Cleanup**:
  - `save_tickets` writes JSON to a hidden temporary file (`.{path.name}.tmp`) in the destination directory, forces write to storage via `os.fsync`, and atomically replaces the destination file via `os.replace`.
  - In the event of any exception during save (including I/O errors and serialization errors), the temporary file is guaranteed to be unlinked and the existing file is preserved completely unchanged.
- **Fail-Safe Loading**:
  - If a file contains invalid JSON or schema violations, `load_tickets` raises `ValueError` without modifying caller memory.

## 5. Coordination Interfaces with Engineer B

- **`add_note(tickets, ticket_id, author, message) -> dict`**:
  - Returns the newly created note dictionary (`{"note_id": ..., "author": ..., "message": ...}`).
  - Directly usable by Engineer B's CLI menus to print confirmation output.
- **`get_notes(tickets, ticket_id) -> list[dict]`**:
  - Exposes sorted notes in sequential order for CLI display and inspection menus.
- **Forwarding Shims**:
  - Maintained in `ticket_manager.py` and `campusflow/__init__.py` for seamless imports across the project.
