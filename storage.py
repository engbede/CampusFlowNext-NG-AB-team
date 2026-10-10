import json
from pathlib import Path


def load_tickets(filename):
    path = Path(filename)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError("Ticket file contains invalid JSON.") from error

    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")

    return tickets


def save_tickets(tickets, filename):
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)
        file.write("\n")