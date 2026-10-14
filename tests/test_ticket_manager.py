import unittest

from ticket_manager import (
    add_note,
    assign_ticket,
    change_status,
    get_notes,
    get_work_queue,
    reopen_ticket,
)


class TestAssignTicket(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T002",
                "title": "Printer problem",
                "priority": "low",
                "status": "open",
                "assigned_to": None,
            },
        ]

    def test_assign_ticket_to_staff_member(self):
        result = assign_ticket(self.tickets, "T001", "David")

        self.assertEqual(result["assigned_to"], "David")

    def test_assign_ticket_trims_whitespace(self):
        result = assign_ticket(self.tickets, "T001", "  David  ")

        self.assertEqual(result["assigned_to"], "David")

    def test_empty_staff_name_raises_error(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "")

    def test_whitespace_staff_name_raises_error(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")

    def test_unknown_ticket_raises_error(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T999", "David")

    def test_invalid_assignment_does_not_change_ticket(self):
        original_assignee = self.tickets[0]["assigned_to"]

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "")

        self.assertEqual(
            self.tickets[0]["assigned_to"],
            original_assignee,
        )

    def test_resolved_ticket_cannot_be_assigned_without_reopening(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "David")

    def test_non_string_staff_name_raises_error_without_mutation(self):
        original = self.tickets[0]["assigned_to"]
        for bad_name in [None, 123, ["David"]]:
            with self.assertRaises(ValueError):
                assign_ticket(self.tickets, "T001", bad_name)
            self.assertEqual(self.tickets[0]["assigned_to"], original)

    def test_reopened_ticket_can_be_assigned(self):
        self.tickets[0]["status"] = "resolved"
        reopen_ticket(self.tickets, "T001")
        result = assign_ticket(self.tickets, "T001", "David")
        self.assertEqual(result["assigned_to"], "David")


class TestChangeStatus(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "priority": "critical",
                "status": "open",
                "assigned_to": "David",
            },
            {
                "id": "T002",
                "title": "Printer problem",
                "priority": "low",
                "status": "open",
                "assigned_to": None,
            },
        ]

    def test_change_status_to_in_progress(self):
        result = change_status(self.tickets, "T001", "in_progress")

        self.assertEqual(result["status"], "in_progress")

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T002", "in_progress")

    def test_change_status_to_resolved(self):
        result = change_status(self.tickets, "T001", "resolved")

        self.assertEqual(result["status"], "resolved")

    def test_invalid_status_raises_error(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "pending")

    def test_invalid_status_does_not_modify_ticket(self):
        original_status = self.tickets[0]["status"]

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "pending")

        self.assertEqual(self.tickets[0]["status"], original_status)

    def test_unknown_ticket_raises_error(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T999", "resolved")

    def test_resolved_ticket_cannot_move_to_in_progress_without_reopening(self):
        change_status(self.tickets, "T001", "resolved")

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")

    def test_resolved_ticket_can_be_reopened_to_open(self):
        change_status(self.tickets, "T001", "resolved")
        result = change_status(self.tickets, "T001", "open")

        self.assertEqual(result["status"], "open")

    def test_reopen_ticket_function(self):
        change_status(self.tickets, "T001", "resolved")
        result = reopen_ticket(self.tickets, "T001")

        self.assertEqual(result["status"], "open")

    def test_reopen_already_open_ticket_remains_open(self):
        result = reopen_ticket(self.tickets, "T001")
        self.assertEqual(result["status"], "open")

    def test_reopen_unknown_ticket_raises_error(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T999")

    def test_change_status_non_string_status_raises_without_mutation(self):
        original_status = self.tickets[0]["status"]
        for bad_status in [None, 123, ["open"]]:
            with self.assertRaises(ValueError):
                change_status(self.tickets, "T001", bad_status)
            self.assertEqual(self.tickets[0]["status"], original_status)

    def test_unassigned_in_progress_does_not_modify_ticket(self):
        original_status = self.tickets[1]["status"]
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T002", "in_progress")
        self.assertEqual(self.tickets[1]["status"], original_status)


class TestGetWorkQueue(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Printer problem",
                "priority": "low",
                "status": "open",
            },
            {
                "id": "T002",
                "title": "Server outage",
                "priority": "critical",
                "status": "in_progress",
            },
            {
                "id": "T003",
                "title": "Login failure",
                "priority": "high",
                "status": "resolved",
            },
            {
                "id": "T004",
                "title": "Wi-Fi problem",
                "priority": "high",
                "status": "open",
            },
        ]

    def test_queue_excludes_resolved_tickets(self):
        result = get_work_queue(self.tickets)
        ticket_ids = [ticket["id"] for ticket in result]

        self.assertNotIn("T003", ticket_ids)

    def test_queue_sorts_by_priority(self):
        result = get_work_queue(self.tickets)
        ticket_ids = [ticket["id"] for ticket in result]

        self.assertEqual(ticket_ids, ["T002", "T004", "T001"])

    def test_queue_preserves_order_for_equal_priorities(self):
        result = get_work_queue(self.tickets)
        ticket_ids = [ticket["id"] for ticket in result]

        self.assertLess(
            ticket_ids.index("T002"),
            ticket_ids.index("T004"),
        )

    def test_queue_sorts_by_numeric_id_for_equal_priorities(self):
        equal_priority_tickets = [
            {
                "id": "T010",
                "title": "DNS failure",
                "priority": "high",
                "status": "open",
            },
            {
                "id": "T002",
                "title": "Email server slow",
                "priority": "high",
                "status": "open",
            },
            {
                "id": "T005",
                "title": "Switch down",
                "priority": "high",
                "status": "open",
            },
        ]

        result = get_work_queue(equal_priority_tickets)
        ids = [t["id"] for t in result]

        self.assertEqual(ids, ["T002", "T005", "T010"])

    def test_empty_ticket_list_returns_empty_queue(self):
        self.assertEqual(get_work_queue([]), [])

    def test_queue_does_not_modify_original_list(self):
        original_ids = [ticket["id"] for ticket in self.tickets]

        get_work_queue(self.tickets)

        updated_ids = [ticket["id"] for ticket in self.tickets]

        self.assertEqual(updated_ids, original_ids)


class TestTicketNotes(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Network outage",
                "priority": "critical",
                "status": "open",
                "assigned_to": "Alice",
                "notes": [],
            },
            {
                "id": "T002",
                "title": "Printer broken",
                "priority": "low",
                "status": "in_progress",
                "assigned_to": "Bob",
                "notes": [],
            },
            {
                "id": "T003",
                "title": "Software license expired",
                "priority": "medium",
                "status": "resolved",
                "assigned_to": "Charlie",
                "notes": [],
            },
        ]

    def test_add_note_to_open_ticket(self):
        note = add_note(self.tickets, "T001", "Alice", "Investigating switch port.")
        self.assertEqual(
            note,
            {
                "note_id": "N001",
                "author": "Alice",
                "message": "Investigating switch port.",
            },
        )
        self.assertEqual(len(self.tickets[0]["notes"]), 1)
        self.assertEqual(self.tickets[0]["notes"][0], note)

    def test_add_note_to_in_progress_ticket(self):
        note = add_note(self.tickets, "T002", "Bob", "Replaced the toner cartridge.")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(len(self.tickets[1]["notes"]), 1)

    def test_sequential_note_ids(self):
        note1 = add_note(self.tickets, "T001", "Alice", "First diagnostic step.")
        note2 = add_note(self.tickets, "T001", "Bob", "Second diagnostic step.")
        note3 = add_note(self.tickets, "T001", "Alice", "Third diagnostic step.")
        self.assertEqual(note1["note_id"], "N001")
        self.assertEqual(note2["note_id"], "N002")
        self.assertEqual(note3["note_id"], "N003")

    def test_independent_note_id_sequencing_across_tickets(self):
        t1_note1 = add_note(self.tickets, "T001", "Alice", "Note 1 for Ticket 1.")
        t1_note2 = add_note(self.tickets, "T001", "Alice", "Note 2 for Ticket 1.")
        t2_note1 = add_note(self.tickets, "T002", "Bob", "Note 1 for Ticket 2.")

        self.assertEqual(t1_note1["note_id"], "N001")
        self.assertEqual(t1_note2["note_id"], "N002")
        self.assertEqual(t2_note1["note_id"], "N001")

    def test_add_note_to_resolved_ticket_rejected(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T003", "Charlie", "Trying to add note to resolved ticket.")
        self.assertEqual(self.tickets[2]["notes"], [])

    def test_reopening_resolved_ticket_permits_future_notes(self):
        # Add note to T001, resolve T001, ensure notes preserved
        add_note(self.tickets, "T001", "Alice", "Initial investigation.")
        change_status(self.tickets, "T001", "resolved")
        self.assertEqual(len(self.tickets[0]["notes"]), 1)

        # Adding note while resolved fails
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Alice", "Should fail while resolved.")

        # Reopen ticket and add note
        reopen_ticket(self.tickets, "T001")
        note2 = add_note(self.tickets, "T001", "Bob", "Issue recurred after reboot.")
        self.assertEqual(note2["note_id"], "N002")
        self.assertEqual(len(self.tickets[0]["notes"]), 2)

    def test_invalid_author_does_not_mutate_or_consume_id(self):
        for bad_author in ["", "   ", None, 123]:
            with self.assertRaises(ValueError):
                add_note(self.tickets, "T001", bad_author, "Valid message here.")
            self.assertEqual(self.tickets[0]["notes"], [])

        # Successful note should still receive N001
        valid_note = add_note(self.tickets, "T001", "Alice", "Valid message here.")
        self.assertEqual(valid_note["note_id"], "N001")

    def test_invalid_message_length_does_not_mutate_or_consume_id(self):
        # Less than 5 chars
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Alice", "tiny")
        self.assertEqual(self.tickets[0]["notes"], [])

        # More than 300 chars
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Alice", "x" * 301)
        self.assertEqual(self.tickets[0]["notes"], [])

        # Non-string message
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Alice", 12345)
        self.assertEqual(self.tickets[0]["notes"], [])

        # First valid note still gets N001
        valid_note = add_note(self.tickets, "T001", "Alice", "Valid message.")
        self.assertEqual(valid_note["note_id"], "N001")

    def test_unknown_ticket_in_add_note_raises_error(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T999", "Alice", "Valid message.")

    def test_add_note_to_legacy_ticket_without_notes_key(self):
        legacy_ticket = {
            "id": "T004",
            "title": "Legacy ticket",
            "priority": "low",
            "status": "open",
            "assigned_to": None,
        }
        tickets = [legacy_ticket]
        note = add_note(tickets, "T004", "Alice", "Note on legacy ticket.")
        self.assertEqual(note["note_id"], "N001")
        self.assertIn("notes", legacy_ticket)
        self.assertEqual(len(legacy_ticket["notes"]), 1)

    def test_get_notes_returns_notes_in_id_order(self):
        # Insert notes out of order
        self.tickets[0]["notes"] = [
            {"note_id": "N003", "author": "Alice", "message": "Third note"},
            {"note_id": "N001", "author": "Alice", "message": "First note"},
            {"note_id": "N002", "author": "Alice", "message": "Second note"},
        ]
        notes = get_notes(self.tickets, "T001")
        self.assertEqual([n["note_id"] for n in notes], ["N001", "N002", "N003"])

    def test_get_notes_on_ticket_without_notes_returns_empty_list(self):
        legacy = {"id": "T010", "status": "open"}
        self.assertEqual(get_notes([legacy], "T010"), [])

    def test_get_notes_unknown_ticket_raises_error(self):
        with self.assertRaises(ValueError):
            get_notes(self.tickets, "T999")

    def test_add_note_non_list_notes_field_raises_error_without_mutation(self):
        corrupt_ticket = {
            "id": "T005",
            "title": "Corrupt notes ticket",
            "priority": "low",
            "status": "open",
            "assigned_to": None,
            "notes": "not a list",
        }
        tickets = [corrupt_ticket]
        with self.assertRaises(ValueError):
            add_note(tickets, "T005", "Alice", "Valid note message.")
        self.assertEqual(corrupt_ticket["notes"], "not a list")

    def test_add_note_malformed_existing_notes_rejected_without_mutation(self):
        bad_existing = {
            "id": "T006",
            "title": "Malformed existing notes",
            "priority": "low",
            "status": "open",
            "assigned_to": None,
            "notes": [{"note_id": "bad_id", "author": "Alice", "message": "Valid"}],
        }
        tickets = [bad_existing]
        with self.assertRaises(ValueError):
            add_note(tickets, "T006", "Bob", "Valid note message.")
        self.assertEqual(len(bad_existing["notes"]), 1)
        self.assertEqual(bad_existing["notes"][0]["note_id"], "bad_id")

    def test_get_notes_non_list_container_raises_value_error(self):
        bad_ticket = {"id": "T007", "status": "open", "notes": "corrupted"}
        with self.assertRaises(ValueError):
            get_notes([bad_ticket], "T007")

    def test_get_notes_non_dict_element_raises_value_error(self):
        bad_ticket = {"id": "T008", "status": "open", "notes": ["not a dict"]}
        with self.assertRaises(ValueError):
            get_notes([bad_ticket], "T008")


if __name__ == "__main__":
    unittest.main()