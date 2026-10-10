VALID_STATUSES = {"open", "in_progress", "resolved"}

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def assign_ticket(tickets, ticket_id, staff_name):
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["assigned_to"] = staff_name.strip()
            return ticket

    raise ValueError(f"Ticket {ticket_id} not found.")


def change_status(tickets, ticket_id, new_status):
    if not isinstance(new_status, str) or new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = new_status
            return ticket

    raise ValueError(f"Ticket {ticket_id} not found.")


def get_work_queue(tickets):
    unresolved_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] != "resolved"
    ]

    return sorted(
        unresolved_tickets,
        key=lambda ticket: PRIORITY_ORDER.get(
            ticket["priority"], len(PRIORITY_ORDER)
        ),
    )