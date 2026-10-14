from campusflow.tickets import PRIORITY_ORDER, VALID_STATUSES


VALID_CATEGORIES = {
    "network": "Network",
    "hardware": "Hardware",
    "software": "Software",
    "other": "Other",
}


def _numeric_ticket_id(ticket_id):
    if (
        isinstance(ticket_id, str)
        and ticket_id.startswith("T")
        and ticket_id[1:].isdigit()
    ):
        return int(ticket_id[1:])

    return float("inf")


def search_tickets(
    tickets,
    query="",
    category=None,
    status=None,
    priority=None,
    sort_by_priority=False,
):
    """Search tickets by title and combine optional filters."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    if not isinstance(query, str):
        raise ValueError("Search text must be a string.")

    query = query.strip().casefold()

    if category is not None and category.strip():
        category_key = category.strip().casefold()

        if category_key not in VALID_CATEGORIES:
            raise ValueError(
                "Category must be Network, Hardware, Software, or Other."
            )

        category = VALID_CATEGORIES[category_key]
    else:
        category = None

    if status is not None and status.strip():
        status = status.strip().lower()

        if status not in VALID_STATUSES:
            raise ValueError(
                "Status must be open, in_progress, or resolved."
            )
    else:
        status = None

    if priority is not None and priority.strip():
        priority = priority.strip().lower()

        if priority not in PRIORITY_ORDER:
            raise ValueError(
                "Priority must be critical, high, medium, or low."
            )
    else:
        priority = None

    results = []

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        title = ticket.get("title", "")

        if not isinstance(title, str):
            continue

        if query and query not in title.casefold():
            continue

        if category and ticket.get("category") != category:
            continue

        if status and ticket.get("status") != status:
            continue

        if priority and ticket.get("priority") != priority:
            continue

        results.append(ticket)

    if sort_by_priority:
        results.sort(
            key=lambda ticket: (
                PRIORITY_ORDER.get(
                    ticket.get("priority"), len(PRIORITY_ORDER)
                ),
                _numeric_ticket_id(ticket.get("id", "")),
            )
        )

    return results