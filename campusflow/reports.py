def generate_report(tickets):
    """Generate a summary report of ticket totals, statuses, and priorities."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    total = len(tickets)

    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
    }

    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        status = ticket.get("status")
        priority = ticket.get("priority")

        if status in status_counts:
            status_counts[status] += 1

        if priority in priority_counts:
            priority_counts[priority] += 1

    return {
        "total_tickets": total,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
    }

