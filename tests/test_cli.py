import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.cli import (
    assign_ticket_menu,
    change_status_menu,
    create_ticket_menu,
    display_tickets,
    format_ticket,
    main,
    reopen_ticket_menu,
    show_report,
    show_work_queue,
)
from campusflow.storage import load_tickets, save_tickets


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "tickets.json"
        self.sample_tickets = [
            {
                "id": "T001",
                "title": "DNS failure",
                "category": "Network",
                "urgency": "high",
                "affected_users": 10,
                "priority": "critical",
                "status": "open",
                "assigned_to": "Alice",
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
        save_tickets(self.sample_tickets, self.data_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_format_ticket(self):
        formatted = format_ticket(self.sample_tickets[0])
        self.assertIn("ID: T001", formatted)
        self.assertIn("DNS failure", formatted)
        self.assertIn("Priority: critical", formatted)
        self.assertIn("Assigned to: Alice", formatted)

        unassigned_formatted = format_ticket(self.sample_tickets[1])
        self.assertIn("Assigned to: Unassigned", unassigned_formatted)

    def test_display_tickets_empty(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_tickets([])
            self.assertIn("No tickets found.", fake_out.getvalue())

    def test_display_tickets_non_empty(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_tickets(self.sample_tickets)
            self.assertIn("T001", fake_out.getvalue())
            self.assertIn("T002", fake_out.getvalue())

    def test_create_ticket_menu_success(self):
        tickets = load_tickets(self.data_file)
        inputs = ["Printer broken", "Hardware", "medium", "5"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                create_ticket_menu(tickets, self.data_file)
                self.assertIn("Ticket created successfully!", fake_out.getvalue())
                self.assertIn("ID: T003", fake_out.getvalue())

        saved = load_tickets(self.data_file)
        self.assertEqual(len(saved), 3)
        self.assertEqual(saved[-1]["title"], "Printer broken")
        self.assertEqual(saved[-1]["priority"], "medium")

    def test_create_ticket_menu_invalid_users(self):
        tickets = load_tickets(self.data_file)
        inputs = ["Printer broken", "Hardware", "medium", "not_a_number"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                create_ticket_menu(tickets, self.data_file)
                self.assertIn("Error: Affected users must be a positive integer.", fake_out.getvalue())

    def test_create_ticket_menu_invalid_urgency(self):
        tickets = load_tickets(self.data_file)
        inputs = ["Printer broken", "Hardware", "super_urgent", "5"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                create_ticket_menu(tickets, self.data_file)
                self.assertIn("Error: Urgency must be low, medium, or high.", fake_out.getvalue())

    def test_show_work_queue(self):
        tickets = load_tickets(self.data_file)
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            show_work_queue(tickets)
            output = fake_out.getvalue()
            self.assertIn("WORK QUEUE", output)
            self.assertIn("T001", output)

    def test_show_work_queue_empty(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            show_work_queue([])
            self.assertIn("Work queue is empty.", fake_out.getvalue())

    def test_assign_ticket_menu_success(self):
        tickets = load_tickets(self.data_file)
        inputs = ["T002", "Bob"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                assign_ticket_menu(tickets, self.data_file)
                self.assertIn("Ticket T002 assigned to Bob.", fake_out.getvalue())

        saved = load_tickets(self.data_file)
        self.assertEqual(saved[1]["assigned_to"], "Bob")

    def test_assign_ticket_menu_not_found(self):
        tickets = load_tickets(self.data_file)
        inputs = ["T999", "Bob"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                assign_ticket_menu(tickets, self.data_file)
                self.assertIn("Ticket T999 not found", fake_out.getvalue())

    def test_change_status_menu_success(self):
        tickets = load_tickets(self.data_file)
        inputs = ["T001", "in_progress"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                change_status_menu(tickets, self.data_file)
                self.assertIn("Ticket T001 status changed to in_progress.", fake_out.getvalue())

        saved = load_tickets(self.data_file)
        self.assertEqual(saved[0]["status"], "in_progress")

    def test_change_status_menu_unassigned_in_progress_fails(self):
        tickets = load_tickets(self.data_file)
        inputs = ["T002", "in_progress"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                change_status_menu(tickets, self.data_file)
                self.assertIn("Error: A ticket must be assigned before it can move to in_progress.", fake_out.getvalue())

    def test_reopen_ticket_menu_success(self):
        tickets = load_tickets(self.data_file)
        tickets[0]["status"] = "resolved"
        save_tickets(tickets, self.data_file)

        inputs = ["T001"]
        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                reopen_ticket_menu(tickets, self.data_file)
                self.assertIn("Ticket T001 reopened to open status.", fake_out.getvalue())

        saved = load_tickets(self.data_file)
        self.assertEqual(saved[0]["status"], "open")

    def test_show_report(self):
        tickets = load_tickets(self.data_file)
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            show_report(tickets)
            output = fake_out.getvalue()
            self.assertIn("TICKET REPORT", output)
            self.assertIn("Total tickets: 2", output)
            self.assertIn("critical: 1", output)

    def test_main_cli_exit(self):
        with patch("builtins.input", return_value="8"):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main(data_file=self.data_file)
                self.assertIn("Goodbye!", fake_out.getvalue())

    def test_main_cli_invalid_option(self):
        with patch("builtins.input", side_effect=["99", "8"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main(data_file=self.data_file)
                self.assertIn("Invalid choice. Please choose a number from 1 to 8.", fake_out.getvalue())


if __name__ == "__main__":
    unittest.main()

