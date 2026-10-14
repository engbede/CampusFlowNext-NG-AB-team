import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import add_note, create_ticket

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
        second_ticket["id"] = "T002"
        second_ticket["title"] = "Another issue"

        self.path.write_text(
            json.dumps([VALID_TICKET, second_ticket]),
            encoding="utf-8",
        )

        self.assertEqual(load_tickets(self.path), [VALID_TICKET, second_ticket])

        duplicate_ticket = VALID_TICKET.copy()
        duplicate_ticket["title"] = "Duplicate issue"
        self.path.write_text(
            json.dumps([VALID_TICKET, duplicate_ticket]),
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

    def test_legacy_record_without_notes_is_loaded(self):
        legacy_ticket = VALID_TICKET.copy()
        self.assertNotIn("notes", legacy_ticket)
        self.path.write_text(json.dumps([legacy_ticket]), encoding="utf-8")

        loaded = load_tickets(self.path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], "T001")
        self.assertEqual(loaded[0].get("notes", []), [])

    def test_ticket_with_valid_notes_is_loaded(self):
        ticket_with_notes = VALID_TICKET.copy()
        ticket_with_notes["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "Investigating switch port."},
            {"note_id": "N002", "author": "Bob", "message": "Port 3 reset successfully."},
        ]
        self.path.write_text(json.dumps([ticket_with_notes]), encoding="utf-8")

        loaded = load_tickets(self.path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(len(loaded[0]["notes"]), 2)
        self.assertEqual(loaded[0]["notes"][0]["note_id"], "N001")
        self.assertEqual(loaded[0]["notes"][1]["note_id"], "N002")

    def test_duplicate_note_ids_within_ticket_rejected_on_load(self):
        ticket_with_dupe_notes = VALID_TICKET.copy()
        ticket_with_dupe_notes["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "First note."},
            {"note_id": "N001", "author": "Bob", "message": "Duplicate ID note."},
        ]
        self.path.write_text(json.dumps([ticket_with_dupe_notes]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_invalid_note_structure_rejected_on_load(self):
        ticket_with_bad_note = VALID_TICKET.copy()
        ticket_with_bad_note["notes"] = [
            {"note_id": "N001", "author": "", "message": "Blank author"}
        ]
        self.path.write_text(json.dumps([ticket_with_bad_note]), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_failed_load_preserves_valid_in_memory_state(self):
        in_memory_tickets = [VALID_TICKET.copy()]
        original_tickets = in_memory_tickets.copy()
        self.path.write_text("{corrupt json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

        self.assertEqual(in_memory_tickets, original_tickets)
        self.assertEqual(in_memory_tickets[0]["id"], "T001")

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

    def test_save_creates_parent_directories(self):
        nested_file = self.path.parent / "data" / "tickets.json"
        tickets = [VALID_TICKET.copy()]

        save_tickets(tickets, nested_file)

        self.assertTrue(nested_file.exists())
        self.assertEqual(load_tickets(nested_file), tickets)

    def test_saving_non_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            save_tickets({}, self.path)

    def test_in_progress_ticket_without_assignee_is_rejected(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["status"] = "in_progress"
        invalid_ticket["assigned_to"] = None

        with self.assertRaises(ValueError):
            save_tickets([invalid_ticket], self.path)

    def test_save_ticket_with_notes(self):
        ticket_with_notes = VALID_TICKET.copy()
        ticket_with_notes["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "Investigating server rack."},
            {"note_id": "N002", "author": "Bob", "message": "Power cycle confirmed."},
        ]

        save_tickets([ticket_with_notes], self.path)
        loaded = load_tickets(self.path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(len(loaded[0]["notes"]), 2)
        self.assertEqual(loaded[0]["notes"][0]["note_id"], "N001")
        self.assertEqual(loaded[0]["notes"][1]["note_id"], "N002")

    def test_save_rejects_duplicate_note_ids(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "Note one."},
            {"note_id": "N001", "author": "Bob", "message": "Note two."},
        ]

        with self.assertRaises(ValueError):
            save_tickets([invalid_ticket], self.path)

        self.assertFalse(self.path.exists())

    def test_save_rejects_invalid_note_message(self):
        invalid_ticket = VALID_TICKET.copy()
        invalid_ticket["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "bad"}
        ]

        with self.assertRaises(ValueError):
            save_tickets([invalid_ticket], self.path)

        self.assertFalse(self.path.exists())

    def test_invalid_save_with_bad_note_preserves_existing_file(self):
        original_tickets = [VALID_TICKET.copy()]
        save_tickets(original_tickets, self.path)
        original_content = self.path.read_text(encoding="utf-8")

        bad_ticket = VALID_TICKET.copy()
        bad_ticket["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "bad"}
        ]

        with self.assertRaises(ValueError):
            save_tickets([bad_ticket], self.path)

        self.assertEqual(self.path.read_text(encoding="utf-8"), original_content)


class TestStorageNotesAndContinuity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_notes_survive_save_load_round_trip(self):
        tickets = []
        t1 = create_ticket(tickets, "Network outage", "Network", "high", 10)
        add_note(tickets, "T001", "Alice", "First diagnostic step.")
        add_note(tickets, "T001", "Bob", "Router replaced successfully.")

        t2 = create_ticket(tickets, "Software license", "Software", "low", 1)
        add_note(tickets, "T002", "Charlie", "Contacted vendor for key.")

        save_tickets(tickets, self.path)
        loaded = load_tickets(self.path)

        self.assertEqual(len(loaded), 2)
        self.assertEqual(len(loaded[0]["notes"]), 2)
        self.assertEqual(loaded[0]["notes"][0]["note_id"], "N001")
        self.assertEqual(loaded[0]["notes"][1]["note_id"], "N002")
        self.assertEqual(len(loaded[1]["notes"]), 1)
        self.assertEqual(loaded[1]["notes"][0]["note_id"], "N001")

    def test_ticket_and_note_id_continuity_after_reload(self):
        tickets = []
        create_ticket(tickets, "Ticket 1", "Network", "low", 1)
        create_ticket(tickets, "Ticket 2", "Software", "low", 1)
        add_note(tickets, "T001", "Alice", "Initial note on T001.")
        add_note(tickets, "T001", "Alice", "Second note on T001.")

        save_tickets(tickets, self.path)

        # Simulate reloading application state from disk
        reloaded_tickets = load_tickets(self.path)

        # Creating next ticket must continue sequential ID
        t3 = create_ticket(reloaded_tickets, "Ticket 3", "Other", "low", 1)
        self.assertEqual(t3["id"], "T003")

        # Adding note to T001 must continue from highest note ID (N003)
        n3 = add_note(reloaded_tickets, "T001", "Bob", "Third note on T001 after reload.")
        self.assertEqual(n3["note_id"], "N003")

        # Adding note to T002 must start at N001
        n_t2 = add_note(reloaded_tickets, "T002", "Charlie", "First note on T002 after reload.")
        self.assertEqual(n_t2["note_id"], "N001")

        # Adding note to T003 must start at N001
        n_t3 = add_note(reloaded_tickets, "T003", "David", "First note on T003 after reload.")
        self.assertEqual(n_t3["note_id"], "N001")

    def test_non_contiguous_note_ids_continuity(self):
        """Bug-hunter test: ticket with non-contiguous legacy note IDs generates safe next ID."""
        ticket = VALID_TICKET.copy()
        ticket["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "First note."},
            {"note_id": "N007", "author": "Bob", "message": "Historical note jumping to 7."},
        ]
        save_tickets([ticket], self.path)

        reloaded = load_tickets(self.path)
        next_note = add_note(reloaded, "T001", "Charlie", "New note added after gap.")
        self.assertEqual(next_note["note_id"], "N008")

    def test_batch_save_partial_failure_preserves_disk_and_cleans_temp(self):
        """Bug-hunter test: failure deep in batch save does not corrupt disk or leave stray temp files."""
        initial_ticket = VALID_TICKET.copy()
        save_tickets([initial_ticket], self.path)
        original_mtime = self.path.stat().st_mtime_ns

        # Batch with valid tickets followed by one ticket with invalid priority
        batch = [
            VALID_TICKET.copy(),
            VALID_TICKET.copy(),
            VALID_TICKET.copy(),
        ]
        batch[1]["id"] = "T002"
        batch[2]["id"] = "T003"
        batch[2]["priority"] = "low"  # Invalid: high urgency + 10 users must be critical

        with self.assertRaises(ValueError):
            save_tickets(batch, self.path)

        # Original file must remain untouched
        self.assertEqual(self.path.stat().st_mtime_ns, original_mtime)
        reloaded = load_tickets(self.path)
        self.assertEqual(len(reloaded), 1)

        # No temporary files should linger in directory
        temp_files = list(self.path.parent.glob(".*.tmp"))
        self.assertEqual(temp_files, [])


if __name__ == "__main__":
    unittest.main()
