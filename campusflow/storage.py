import json
import os
import re
import tempfile
from pathlib import Path

from campusflow.tickets import calculate_priority

_REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}

_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
_STATUSES = {"open", "in_progress", "resolved"}
_PRIORITIES = {"low", "medium", "high", "critical"}


def _validate_ticket(ticket):
    if not isinstance(ticket, dict):
        raise ValueError("Each ticket must be a JSON object.")

    if set(ticket) != _REQUIRED_FIELDS:
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
    if not isinstance(category, str) or category not in _CATEGORIES:
        raise ValueError("Ticket category is invalid.")

    urgency = ticket["urgency"]
    if not isinstance(urgency, str) or urgency not in {"low", "medium", "high"}:
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
    if not isinstance(status, str) or status not in _STATUSES:
        raise ValueError("Ticket status is invalid.")

    assigned_to = ticket["assigned_to"]
    if assigned_to is not None and (
        not isinstance(assigned_to, str) or not assigned_to.strip()
    ):
        raise ValueError("Assigned staff must be a nonblank name or None.")

    if status == "in_progress" and assigned_to is None:
        raise ValueError("An in-progress ticket must be assigned to a staff member.")


def _validate_tickets(tickets):
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    seen_ids = set()

    for ticket in tickets:
        _validate_ticket(ticket)

        ticket_id = ticket["id"]
        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")
        seen_ids.add(ticket_id)


def load_tickets(path):
    path = Path(path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"Ticket file contains invalid JSON: {path}") from error

    _validate_tickets(tickets)
    return tickets


def save_tickets(tickets, path):
    _validate_tickets(tickets)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(tickets, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, path)
    except OSError:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise
