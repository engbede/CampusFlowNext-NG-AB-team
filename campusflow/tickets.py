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
