import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets

VALID_TICKET = {
    "id": "T001",
    "title": "Network outage",
    "category": "Network",
    "urgency": "high",
    "affected_users": 10,
    "priority": "critical",
    "status": "open",
    "assigned_to": None,
}


class TestLoadTickets(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_valid_file_returns_tickets(self):
        self.path.write_text(json.dumps([VALID_TICKET]), encoding="utf-8")

        self.assertEqual(load_tickets(self.path), [VALID_TICKET])

    def test_malformed_json_raises_value_error(self):
        self.path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_json_object_instead_of_list_is_rejected(self):
        self.path.write_text(json.dumps({"ticket": VALID_TICKET}), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_ticket_missing_required_field_is_rejected(self):
        invalid_ticket = VALID_TICKET.copy()
        del invalid_ticket["title"]
        self.path.write_text(json.dumps([invalid_ticket]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_invalid_ticket_priority_is_rejected(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["priority"] = "low"
        self.path.write_text(json.dumps([invalid_ticket]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_duplicate_ticket_ids_are_rejected(self):
        second_ticket = VALID_TICKET.copy()
        second_ticket["title"] = "Another issue"

        self.path.write_text(
            json.dumps([VALID_TICKET, second_ticket]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_non_string_category_is_rejected(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["category"] = ["Network"]
        self.path.write_text(json.dumps([invalid_ticket]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_non_string_status_is_rejected(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["status"] = {"state": "open"}
        self.path.write_text(json.dumps([invalid_ticket]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_zero_ticket_id_is_rejected(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["id"] = "T000"
        self.path.write_text(json.dumps([invalid_ticket]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)


class TestSaveTickets(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_round_trip(self):
        tickets = [VALID_TICKET.copy()]

        save_tickets(tickets, self.path)

        self.assertEqual(load_tickets(self.path), tickets)

    def test_invalid_ticket_data_is_not_saved(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["affected_users"] = 0

        with self.assertRaises(ValueError):
            save_tickets([invalid_ticket], self.path)

        self.assertFalse(self.path.exists())

    def test_invalid_save_preserves_existing_file(self):
        original_tickets = [VALID_TICKET.copy()]
        save_tickets(original_tickets, self.path)
        original_content = self.path.read_text(encoding="utf-8")

        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["affected_users"] = 0

        with self.assertRaises(ValueError):
            save_tickets([invalid_ticket], self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            original_content,
        )


if __name__ == "__main__":
    unittest.main()
