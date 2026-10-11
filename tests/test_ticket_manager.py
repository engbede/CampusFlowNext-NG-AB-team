import unittest

from ticket_manager import assign_ticket, change_status, get_work_queue


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


class TestChangeStatus(unittest.TestCase):
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

    def test_change_status_to_in_progress(self):
        result = change_status(self.tickets, "T001", "in_progress")

        self.assertEqual(result["status"], "in_progress")

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

    def test_empty_ticket_list_returns_empty_queue(self):
        self.assertEqual(get_work_queue([]), [])

    def test_queue_does_not_modify_original_list(self):
        original_ids = [
            ticket["id"] for ticket in self.tickets
        ]

        get_work_queue(self.tickets)

        updated_ids = [
            ticket["id"] for ticket in self.tickets
        ]

        self.assertEqual(updated_ids, original_ids)


if __name__ == "__main__":
    unittest.main()