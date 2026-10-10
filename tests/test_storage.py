import json
import tempfile
import unittest
from pathlib import Path

from storage import load_tickets, save_tickets


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.filename = Path(self.temp_dir.name) / "tickets.json"

        self.tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_tickets(self):
        save_tickets(self.tickets, self.filename)

        result = load_tickets(self.filename)

        self.assertEqual(result, self.tickets)

    def test_missing_file_returns_empty_list(self):
        result = load_tickets(self.filename)

        self.assertEqual(result, [])

    def test_invalid_json_raises_value_error(self):
        self.filename.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.filename)

    def test_non_list_json_raises_value_error(self):
        self.filename.write_text(
            json.dumps({"id": "T001"}),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets(self.filename)

    def test_save_creates_parent_directories(self):
        nested_file = (
            Path(self.temp_dir.name) / "data" / "tickets.json"
        )

        save_tickets(self.tickets, nested_file)

        self.assertTrue(nested_file.exists())
        self.assertEqual(load_tickets(nested_file), self.tickets)

    def test_saving_non_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            save_tickets({}, self.filename)


if __name__ == "__main__":
    unittest.main()