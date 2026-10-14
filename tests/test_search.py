import unittest

from campusflow.search import search_tickets


class TestSearchTickets(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T003",
                "title": "Login server failure",
                "category": "Software",
                "priority": "high",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T001",
                "title": "Login page error",
                "category": "Software",
                "priority": "high",
                "status": "open",
                "assigned_to": "Ada",
            },
            {
                "id": "T002",
                "title": "Network connection failure",
                "category": "Network",
                "priority": "critical",
                "status": "in_progress",
                "assigned_to": "John",
            },
        ]

    def test_search_is_case_insensitive(self):
        results = search_tickets(self.tickets, query="LOGIN")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T003", "T001"],
        )

    def test_search_matches_title_substring(self):
        results = search_tickets(self.tickets, query="server")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T003"],
        )

    def test_filters_combine_using_and(self):
        results = search_tickets(
            self.tickets,
            query="login",
            category="software",
            status="open",
            priority="high",
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T003", "T001"],
        )

    def test_nonmatching_combined_filters_return_empty_list(self):
        results = search_tickets(
            self.tickets,
            query="login",
            category="Network",
        )

        self.assertEqual(results, [])

    def test_empty_filters_do_not_filter_results(self):
        results = search_tickets(
            self.tickets,
            category="",
            status="",
            priority="",
        )

        self.assertEqual(len(results), 3)

    def test_search_results_can_be_sorted(self):
        results = search_tickets(
            self.tickets,
            sort_by_priority=True,
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T002", "T001", "T003"],
        )

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, category="Finance")

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, status="waiting")

    def test_invalid_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, priority="urgent")

    def test_non_list_tickets_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets("invalid")


if __name__ == "__main__":
    unittest.main()