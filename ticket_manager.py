"""Backward-compatibility module forwarding to campusflow.tickets."""

from campusflow.tickets import (
    PRIORITY_ORDER,
    VALID_STATUSES,
    assign_ticket,
    change_status,
    get_work_queue,
    reopen_ticket,
)

__all__ = [
    "PRIORITY_ORDER",
    "VALID_STATUSES",
    "assign_ticket",
    "change_status",
    "get_work_queue",
    "reopen_ticket",
]