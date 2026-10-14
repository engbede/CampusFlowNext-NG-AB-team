"""CampusFlow ticket business logic and central validation."""

import re

VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
VALID_STATUSES = {"open", "in_progress", "resolved"}
VALID_URGENCIES = {"low", "medium", "high"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

BASE_REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}


def calculate_priority(urgency, affected_users):
    """Calculate ticket priority from urgency and affected-user count."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be low, medium, or high.")

    urgency = urgency.strip().lower()

    if urgency not in VALID_URGENCIES:
        raise ValueError("Urgency must be low, medium, or high.")

    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        raise ValueError("Affected users must be a positive integer.")

    if affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")

    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def _validate_title(title):
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title must not be blank.")
    return title.strip()


def _validate_category(category):
    if not isinstance(category, str):
        raise ValueError("Category must be Network, Hardware, Software, or Other.")

    normalized = category.strip().lower()
    categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }

    if normalized not in categories:
        raise ValueError("Category must be Network, Hardware, Software, or Other.")

    return categories[normalized]


def validate_note(note):
    """Validate the structure and fields of an individual note."""
    if not isinstance(note, dict):
        raise ValueError("Each note must be a dictionary.")

    if set(note) != {"note_id", "author", "message"}:
        raise ValueError("Note must contain exactly note_id, author, and message.")

    note_id = note["note_id"]
    if (
        not isinstance(note_id, str)
        or not re.fullmatch(r"N[0-9]{3,}", note_id)
        or int(note_id[1:]) < 1
    ):
        raise ValueError("Note ID must use the format N001.")

    author = note["author"]
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author must not be blank.")

    message = note["message"]
    if not isinstance(message, str) or not (5 <= len(message.strip()) <= 300):
        raise ValueError("Note message must be between 5 and 300 characters.")


def validate_ticket(ticket):
    """Validate the structure, fields, and consistency of a ticket."""
    if not isinstance(ticket, dict):
        raise ValueError("Each ticket must be a JSON object.")

    keys = set(ticket)
    if keys not in (BASE_REQUIRED_FIELDS, BASE_REQUIRED_FIELDS | {"notes"}):
        raise ValueError("Ticket must contain exactly the required fields.")

    ticket_id = ticket["id"]
    if (
        not isinstance(ticket_id, str)
        or not re.fullmatch(r"T[0-9]{3,}", ticket_id)
        or int(ticket_id[1:]) < 1
    ):
        raise ValueError("Ticket ID must use the format T001.")

    title = ticket["title"]
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title must not be blank.")

    category = ticket["category"]
    if not isinstance(category, str) or category not in VALID_CATEGORIES:
        raise ValueError("Ticket category is invalid.")

    urgency = ticket["urgency"]
    if not isinstance(urgency, str) or urgency not in VALID_URGENCIES:
        raise ValueError("Ticket urgency is invalid.")

    affected_users = ticket["affected_users"]
    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        raise ValueError("Affected users must be a positive integer.")
    if affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")

    expected_priority = calculate_priority(urgency, affected_users)
    if ticket["priority"] != expected_priority:
        raise ValueError("Ticket priority does not match its urgency and user count.")

    status = ticket["status"]
    if not isinstance(status, str) or status not in VALID_STATUSES:
        raise ValueError("Ticket status is invalid.")

    assigned_to = ticket["assigned_to"]
    if assigned_to is not None and (
        not isinstance(assigned_to, str) or not assigned_to.strip()
    ):
        raise ValueError("Assigned staff must be a nonblank name or None.")

    if status == "in_progress" and assigned_to is None:
        raise ValueError("An in-progress ticket must be assigned to a staff member.")

    if "notes" in ticket:
        notes = ticket["notes"]
        if not isinstance(notes, list):
            raise ValueError("Ticket notes must be a list.")
        seen_note_ids = set()
        for note in notes:
            validate_note(note)
            note_id = note["note_id"]
            if note_id in seen_note_ids:
                raise ValueError(f"Duplicate note ID: {note_id}")
            seen_note_ids.add(note_id)


def validate_tickets(tickets):
    """Validate a list of tickets, checking all records and ensuring unique IDs."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    seen_ids = set()
    for ticket in tickets:
        validate_ticket(ticket)
        ticket_id = ticket["id"]
        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")
        seen_ids.add(ticket_id)


def _next_ticket_id(tickets):
    highest_id = 0

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isdigit()
        ):
            highest_id = max(highest_id, int(ticket_id[1:]))

    return f"T{highest_id + 1:03d}"


def _next_note_id(ticket):
    highest_id = 0
    notes = ticket.get("notes") or []

    for note in notes:
        note_id = note.get("note_id", "")
        if (
            isinstance(note_id, str)
            and note_id.startswith("N")
            and note_id[1:].isdigit()
        ):
            highest_id = max(highest_id, int(note_id[1:]))

    return f"N{highest_id + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Create and validate a new ticket, appending it to the ticket list."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    normalized_title = _validate_title(title)
    normalized_category = _validate_category(category)
    normalized_urgency = (
        urgency.strip().lower() if isinstance(urgency, str) else urgency
    )

    priority = calculate_priority(normalized_urgency, affected_users)
    ticket_id = _next_ticket_id(tickets)

    ticket = {
        "id": ticket_id,
        "title": normalized_title,
        "category": normalized_category,
        "urgency": normalized_urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    tickets.append(ticket)
    return ticket


def _find_ticket(tickets, ticket_id):
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    for ticket in tickets:
        if isinstance(ticket, dict) and ticket.get("id") == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign an open or in-progress ticket to a support staff member."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise ValueError(
            "A resolved ticket must be explicitly reopened before further changes."
        )

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    """Change ticket status according to lifecycle transition rules."""
    if not isinstance(new_status, str) or new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")

    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved" and new_status != "open":
        raise ValueError(
            "A resolved ticket must be explicitly reopened before further changes."
        )

    if new_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError(
            "A ticket must be assigned before it can move to in_progress."
        )

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Explicitly reopen a resolved ticket to open status."""
    ticket = _find_ticket(tickets, ticket_id)
    ticket["status"] = "open"
    return ticket


def add_note(tickets, ticket_id, author, message):
    """Add a validated note to an open or in-progress ticket."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author must not be blank.")

    if not isinstance(message, str) or not (5 <= len(message.strip()) <= 300):
        raise ValueError("Note message must be between 5 and 300 characters.")

    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise ValueError("Cannot add notes to a resolved ticket.")

    if "notes" not in ticket or not isinstance(ticket["notes"], list):
        ticket["notes"] = []

    note_id = _next_note_id(ticket)
    note = {
        "note_id": note_id,
        "author": author.strip(),
        "message": message.strip(),
    }
    ticket["notes"].append(note)
    return note


def _extract_numeric_note_id(note_id):
    if (
        isinstance(note_id, str)
        and note_id.startswith("N")
        and note_id[1:].isdigit()
    ):
        return int(note_id[1:])
    return float("inf")


def get_notes(tickets, ticket_id):
    """Return notes for a ticket in sequential note-ID order."""
    ticket = _find_ticket(tickets, ticket_id)
    notes = ticket.get("notes") or []
    return sorted(
        notes, key=lambda note: _extract_numeric_note_id(note.get("note_id", ""))
    )


def _extract_numeric_id(ticket_id):
    if (
        isinstance(ticket_id, str)
        and ticket_id.startswith("T")
        and ticket_id[1:].isdigit()
    ):
        return int(ticket_id[1:])
    return float("inf")


def get_work_queue(tickets):
    """Return unresolved tickets ordered by priority and numeric ticket ID."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    unresolved_tickets = [
        ticket
        for ticket in tickets
        if isinstance(ticket, dict) and ticket.get("status") != "resolved"
    ]

    return sorted(
        unresolved_tickets,
        key=lambda ticket: (
            PRIORITY_ORDER.get(
                str(ticket.get("priority", "")).lower(), len(PRIORITY_ORDER)
            ),
            _extract_numeric_id(ticket.get("id", "")),
        ),
    )
