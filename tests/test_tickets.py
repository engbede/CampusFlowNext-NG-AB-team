import unittest

from campusflow.tickets import (
    calculate_priority,
    create_ticket,
    validate_note,
    validate_ticket,
    validate_tickets,
)


class TestCalculatePriority(unittest.TestCase):
    def test_high_urgency_and_ten_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_high_urgency_and_fewer_than_ten_users_is_high(self):
        self.assertEqual(calculate_priority("high", 9), "high")

    def test_ten_users_with_medium_urgency_is_high(self):
        self.assertEqual(calculate_priority("medium", 10), "high")

    def test_low_urgency_and_three_users_is_medium(self):
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_urgency_and_two_users_is_low(self):
        self.assertEqual(calculate_priority("low", 2), "low")

    def test_urgency_is_case_insensitive(self):
        self.assertEqual(calculate_priority(" HIGH ", 10), "critical")

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_priority("urgent", 2)

    def test_zero_users_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", 0)

    def test_negative_users_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", -1)

    def test_decimal_user_count_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", 2.5)

    def test_text_user_count_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", "3")

    def test_boolean_user_count_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", True)


class TestCreateTicket(unittest.TestCase):
    def test_create_ticket_returns_expected_fields(self):
        tickets = []

        ticket = create_ticket(tickets, "Wi-Fi unavailable", "Network", "high", 10)

        self.assertEqual(
            ticket,
            {
                "id": "T001",
                "title": "Wi-Fi unavailable",
                "category": "Network",
                "urgency": "high",
                "affected_users": 10,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            },
        )
        self.assertEqual(len(tickets), 1)

    def test_create_ticket_normalizes_title_and_category(self):
        tickets = []

        ticket = create_ticket(tickets, "  Broken keyboard  ", " hArDwArE ", "LOW", 1)

        self.assertEqual(ticket["title"], "Broken keyboard")
        self.assertEqual(ticket["category"], "Hardware")
        self.assertEqual(ticket["urgency"], "low")

    def test_ticket_ids_increment(self):
        tickets = []

        first = create_ticket(tickets, "First", "Other", "low", 1)
        second = create_ticket(tickets, "Second", "Other", "low", 1)

        self.assertEqual(first["id"], "T001")
        self.assertEqual(second["id"], "T002")

    def test_ticket_id_uses_highest_existing_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T003"},
            {"id": "T002"},
        ]

        ticket = create_ticket(tickets, "Fourth", "Other", "low", 1)

        self.assertEqual(ticket["id"], "T004")

    def test_blank_title_is_rejected_without_mutation(self):
        tickets = []

        with self.assertRaises(ValueError):
            create_ticket(tickets, "   ", "Other", "low", 1)

        self.assertEqual(tickets, [])

    def test_invalid_category_is_rejected_without_mutation(self):
        tickets = []

        with self.assertRaises(ValueError):
            create_ticket(tickets, "Broken router", "Appliances", "low", 1)

        self.assertEqual(tickets, [])

    def test_invalid_priority_input_does_not_create_ticket(self):
        tickets = []

        with self.assertRaises(ValueError):
            create_ticket(tickets, "Broken router", "Network", "urgent", 1)

        self.assertEqual(tickets, [])

    def test_non_list_tickets_is_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket({}, "Valid title", "Network", "low", 1)

    def test_non_string_title_is_rejected_without_mutation(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, 12345, "Network", "low", 1)
        self.assertEqual(tickets, [])

    def test_non_string_category_is_rejected_without_mutation(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Valid title", None, "low", 1)
        self.assertEqual(tickets, [])

    def test_boolean_and_float_users_rejected_without_mutation(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Title", "Network", "low", True)
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Title", "Network", "low", 3.14)
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Title", "Network", "low", 0)
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Title", "Network", "low", -5)
        self.assertEqual(tickets, [])


class TestValidateNote(unittest.TestCase):
    def test_valid_note_passes(self):
        note = {"note_id": "N001", "author": "Alice", "message": "Investigating the network switch."}
        validate_note(note)

    def test_note_must_be_dict(self):
        with self.assertRaises(ValueError):
            validate_note("not a dict")

    def test_note_missing_required_field(self):
        note = {"note_id": "N001", "author": "Alice"}
        with self.assertRaises(ValueError):
            validate_note(note)

    def test_note_extra_fields_rejected(self):
        note = {"note_id": "N001", "author": "Alice", "message": "Valid message", "extra": 123}
        with self.assertRaises(ValueError):
            validate_note(note)

    def test_note_id_format_invalid(self):
        for bad_id in ["001", "N00", "N000", "Nabc", "T001", 123]:
            with self.assertRaises(ValueError):
                validate_note({"note_id": bad_id, "author": "Alice", "message": "Valid note message"})

    def test_note_author_blank_or_invalid(self):
        for bad_author in ["", "   ", None, 42]:
            with self.assertRaises(ValueError):
                validate_note({"note_id": "N001", "author": bad_author, "message": "Valid note message"})

    def test_note_message_length_boundaries(self):
        with self.assertRaises(ValueError):
            validate_note({"note_id": "N001", "author": "Alice", "message": "tiny"})
        with self.assertRaises(ValueError):
            validate_note({"note_id": "N001", "author": "Alice", "message": "   four   "[0:4]})
        validate_note({"note_id": "N001", "author": "Alice", "message": "12345"})
        validate_note({"note_id": "N001", "author": "Alice", "message": "a" * 300})
        with self.assertRaises(ValueError):
            validate_note({"note_id": "N001", "author": "Alice", "message": "a" * 301})

    def test_note_message_non_string_rejected(self):
        with self.assertRaises(ValueError):
            validate_note({"note_id": "N001", "author": "Alice", "message": 12345})


class TestCentralValidation(unittest.TestCase):
    def setUp(self):
        self.valid_ticket = {
            "id": "T001",
            "title": "Wi-Fi outage",
            "category": "Network",
            "urgency": "high",
            "affected_users": 10,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "notes": [
                {"note_id": "N001", "author": "Alice", "message": "First note on ticket"}
            ],
        }

    def test_valid_ticket_passes(self):
        validate_ticket(self.valid_ticket)

    def test_legacy_ticket_without_notes_passes(self):
        legacy = self.valid_ticket.copy()
        del legacy["notes"]
        validate_ticket(legacy)

    def test_ticket_must_be_dict(self):
        with self.assertRaises(ValueError):
            validate_ticket(["not a dict"])

    def test_ticket_id_must_be_positive_format(self):
        for bad_id in ["T000", "001", "T01", "Txyz", None]:
            bad = self.valid_ticket.copy()
            bad["id"] = bad_id
            with self.assertRaises(ValueError):
                validate_ticket(bad)

    def test_invalid_category_rejected(self):
        bad = self.valid_ticket.copy()
        bad["category"] = "UnknownCategory"
        with self.assertRaises(ValueError):
            validate_ticket(bad)

    def test_invalid_urgency_rejected(self):
        bad = self.valid_ticket.copy()
        bad["urgency"] = "extreme"
        with self.assertRaises(ValueError):
            validate_ticket(bad)

    def test_priority_mismatch_rejected(self):
        bad = self.valid_ticket.copy()
        bad["priority"] = "low"
        with self.assertRaises(ValueError):
            validate_ticket(bad)

    def test_in_progress_without_assignee_rejected(self):
        bad = self.valid_ticket.copy()
        bad["status"] = "in_progress"
        bad["assigned_to"] = None
        with self.assertRaises(ValueError):
            validate_ticket(bad)

    def test_duplicate_notes_within_ticket_rejected(self):
        bad = self.valid_ticket.copy()
        bad["notes"] = [
            {"note_id": "N001", "author": "Alice", "message": "First note here"},
            {"note_id": "N001", "author": "Bob", "message": "Duplicate ID note"},
        ]
        with self.assertRaises(ValueError):
            validate_ticket(bad)

    def test_validate_tickets_duplicate_ids_rejected(self):
        second = self.valid_ticket.copy()
        with self.assertRaises(ValueError):
            validate_tickets([self.valid_ticket, second])

    def test_validate_tickets_non_list_rejected(self):
        with self.assertRaises(ValueError):
            validate_tickets("not a list")


if __name__ == "__main__":
    unittest.main()
