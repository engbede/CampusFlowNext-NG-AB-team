"""Backward-compatibility module forwarding to campusflow.tickets."""

from campusflow.tickets import (
    PRIORITY_ORDER,
    VALID_STATUSES,
    add_note,
    assign_ticket,
    change_status,
    get_notes,
    get_work_queue,
    reopen_ticket,
)

__all__ = [
    "PRIORITY_ORDER",
    "VALID_STATUSES",
    "add_note",
    "assign_ticket",
    "change_status",
    "get_notes",
    "get_work_queue",
    "reopen_ticket",
]