import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.cli import (
    assign_ticket_menu,
    change_status_menu,
    create_ticket_menu,
    display_search_results,
    display_tickets,
    format_ticket,
    main,
    reopen_ticket_menu,
    search_tickets_menu,
    show_report,
    show_work_queue,
)
from campusflow.storage import save_tickets


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "tickets.json"

        self.tickets = [
            {
                "id": "T001",
                "title": "DNS failure",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T002",
                "title": "Broken mouse",
                "category": "Hardware",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
            },
        ]

        save_tickets(self.tickets, self.data_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_format_ticket(self):
        output = format_ticket(self.tickets[0])

        self.assertIn("T001", output)
        self.assertIn("DNS failure", output)
        self.assertIn("Network", output)
        self.assertIn("critical", output)

    def test_display_tickets(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_tickets(self.tickets)
            output = fake_out.getvalue()

        self.assertIn("DNS failure", output)
        self.assertIn("Broken mouse", output)
        self.assertIn("T001", output)
        self.assertIn("T002", output)

    def test_display_tickets_empty(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_tickets([])
            output = fake_out.getvalue()

        self.assertTrue(output.strip())

    def test_create_ticket_menu(self):
        inputs = [
            "Printer not working",
            "Hardware",
            "medium",
            "3",
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                create_ticket_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertIn("Ticket created successfully!", output)
        self.assertIn("T003", output)
        self.assertIn("medium", output)
        self.assertEqual(len(self.tickets), 3)
        self.assertEqual(
            self.tickets[-1]["title"],
            "Printer not working",
        )

    def test_show_work_queue(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            show_work_queue(self.tickets)
            output = fake_out.getvalue()

        self.assertIn("DNS failure", output)
        self.assertIn("Broken mouse", output)

    def test_assign_ticket_menu(self):
        inputs = ["T001", "Ada Lovelace"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                assign_ticket_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertEqual(
            self.tickets[0]["assigned_to"],
            "Ada Lovelace",
        )
        self.assertIn("Ada Lovelace", output)

    def test_change_status_menu(self):
        self.tickets[0]["assigned_to"] = "Ada Lovelace"
        inputs = ["T001", "in_progress"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                change_status_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertEqual(
            self.tickets[0]["status"],
            "in_progress",
        )
        self.assertIn("in_progress", output)

    def test_reopen_ticket_menu(self):
        self.tickets[0]["status"] = "resolved"

        with patch("builtins.input", return_value="T001"):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                reopen_ticket_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertEqual(self.tickets[0]["status"], "open")
        self.assertIn("T001", output)

    def test_show_report(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            show_report(self.tickets)
            output = fake_out.getvalue()

        self.assertIn("2", output)
        self.assertIn("open", output)
        self.assertIn("critical", output)

    def test_display_search_results(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_search_results(self.tickets)
            output = fake_out.getvalue()

        self.assertIn("T001", output)
        self.assertIn("DNS failure", output)
        self.assertIn("Network", output)
        self.assertIn("critical", output)
        self.assertIn("Unassigned", output)

    def test_display_search_results_empty(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_search_results([])
            output = fake_out.getvalue()

        self.assertIn("No matching tickets found.", output)

    def test_search_tickets_menu(self):
        inputs = [
            "DNS",
            "Network",
            "open",
            "critical",
            "n",
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                search_tickets_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertIn("SEARCH RESULTS", output)
        self.assertIn("DNS failure", output)
        self.assertIn("T001", output)
        self.assertNotIn("Broken mouse", output)

    def test_search_tickets_menu_invalid_filter(self):
        inputs = [
            "",
            "Finance",
            "",
            "",
            "n",
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                search_tickets_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertIn("Error:", output)
        self.assertIn("Category must be", output)

    def test_search_results_can_be_sorted_by_priority(self):
        inputs = [
            "",
            "",
            "",
            "",
            "y",
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                search_tickets_menu(self.tickets)
                output = fake_out.getvalue()

        self.assertIn("DNS failure", output)
        self.assertIn("Broken mouse", output)
        self.assertLess(
            output.index("DNS failure"),
            output.index("Broken mouse"),
        )

    def test_main_exits(self):
        with patch(
            "campusflow.cli.get_default_data_file",
            return_value=self.data_file,
        ):
            with patch("builtins.input", return_value="9"):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()

        self.assertIn("Goodbye!", output)

    def test_main_invalid_menu_choice(self):
        inputs = ["99", "9"]

        with patch(
            "campusflow.cli.get_default_data_file",
            return_value=self.data_file,
        ):
            with patch("builtins.input", side_effect=inputs):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()

        self.assertIn(
            "Invalid choice. Please choose a number from 1 to 9.",
            output,
        )


if __name__ == "__main__":
    unittest.main()