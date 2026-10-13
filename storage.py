"""Backward-compatibility module forwarding to campusflow.storage."""

from campusflow.storage import load_tickets, save_tickets

__all__ = ["load_tickets", "save_tickets"]