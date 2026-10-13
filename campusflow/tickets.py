VALID_STATUSES = {"open", "in_progress", "resolved"}

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def calculate_priority(urgency, affected_users):
    """Calculate ticket priority from urgency and affected-user count."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be low, medium, or high.")

    urgency = urgency.strip().lower()

    if urgency not in {"low", "medium", "high"}:
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
