VALID_CATEGORIES = ["Network", "Hardware", "Software", "Other"]


def generate_report(tickets):
    """Generate a summary report of ticket totals and distributions."""
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

    category_counts = {
        category: 0 for category in VALID_CATEGORIES
    }

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        status = ticket.get("status")
        priority = ticket.get("priority")
        category = ticket.get("category")

        if status in status_counts:
            status_counts[status] += 1

        if priority in priority_counts:
            priority_counts[priority] += 1

        if isinstance(category, str):
            normalized_category = category.strip().lower()

            for valid_category in VALID_CATEGORIES:
                if normalized_category == valid_category.lower():
                    category_counts[valid_category] += 1
                    break

    resolved_tickets = status_counts["resolved"]
    unresolved_tickets = (
        status_counts["open"] + status_counts["in_progress"]
    )

    resolution_percentage = (
        resolved_tickets / total * 100 if total else 0.0
    )

    return {
        "total_tickets": total,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "unresolved_tickets": unresolved_tickets,
        "resolved_tickets": resolved_tickets,
        "resolution_percentage": resolution_percentage,
    }