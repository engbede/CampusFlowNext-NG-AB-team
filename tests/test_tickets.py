import unittest

from campusflow.tickets import calculate_priority, create_ticket


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


if __name__ == "__main__":
    unittest.main()
