"""CampusFlow JSON persistence module with strict collection validation."""

import json
import os
import tempfile
from pathlib import Path

from campusflow.tickets import (
    calculate_priority,
    validate_note,
    validate_ticket,
    validate_tickets,
)

# Export for backward compatibility with external importers and tests
_validate_ticket = validate_ticket
_validate_tickets = validate_tickets


def load_tickets(path):
    """Load and validate tickets from a JSON file path.

    Returns an empty list if the file does not exist.
    Rejects malformed JSON and invalid ticket structures.
    Treats missing notes fields on legacy records as empty lists.
    """
    path = Path(path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"Ticket file contains invalid JSON: {path}") from error

    validate_tickets(tickets)
    return tickets


def save_tickets(tickets, path):
    """Validate the entire collection and atomically save tickets to a JSON file.

    Preserves existing files if validation or write operations fail.
    Uses atomic replacement via temporary file.
    """
    validate_tickets(tickets)

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
