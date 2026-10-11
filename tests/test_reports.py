import unittest

from reports import generate_report


class TestGenerateReport(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Server outage",
                "priority": "critical",
                "status": "open",
            },
            {
                "id": "T002",
                "title": "Login failure",
                "priority": "high",
                "status": "in_progress",
            },
            {
                "id": "T003",
                "title": "Printer problem",
                "priority": "low",
                "status": "resolved",
            },
        ]

    def test_report_counts_total_tickets(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["total_tickets"], 3)

    def test_report_counts_statuses(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["status_counts"],
            {
                "open": 1,
                "in_progress": 1,
                "resolved": 1,
            },
        )

    def test_report_counts_priorities(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["priority_counts"],
            {
                "critical": 1,
                "high": 1,
                "medium": 0,
                "low": 1,
            },
        )

    def test_empty_ticket_list(self):
        report = generate_report([])

        self.assertEqual(report["total_tickets"], 0)
        self.assertEqual(
            report["status_counts"],
            {
                "open": 0,
                "in_progress": 0,
                "resolved": 0,
            },
        )

        self.assertEqual(
            report["priority_counts"],
            {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()