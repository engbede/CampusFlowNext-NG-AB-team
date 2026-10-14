"""Command-line interface for CampusFlow Helpdesk."""

from pathlib import Path

from campusflow.reports import generate_report
from campusflow.search import search_tickets
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import (
    assign_ticket,
    change_status,
    create_ticket,
    get_work_queue,
    reopen_ticket,
)

DEFAULT_DATA_FILE = Path("data/tickets.json")


def get_default_data_file():
    """Determine the default data file path based on existing files."""
    if Path("tickets.json").exists() and not DEFAULT_DATA_FILE.exists():
        return Path("tickets.json")
    return DEFAULT_DATA_FILE


def format_ticket(ticket):
    """Format a single ticket for readable display."""
    assigned = ticket.get("assigned_to") or "Unassigned"
    return (
        f"ID: {ticket.get('id', 'N/A')}\n"
        f"Title: {ticket.get('title', 'N/A')}\n"
        f"Category: {ticket.get('category', 'N/A')}\n"
        f"Urgency: {ticket.get('urgency', 'N/A')}\n"
        f"Affected Users: {ticket.get('affected_users', 'N/A')}\n"
        f"Priority: {ticket.get('priority', 'N/A')}\n"
        f"Status: {ticket.get('status', 'N/A')}\n"
        f"Assigned to: {assigned}"
    )


def display_tickets(tickets):
    """Print a list of tickets to standard output."""
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in tickets:
        print("-" * 40)
        print(format_ticket(ticket))
    print("-" * 40)


def create_ticket_menu(tickets, data_file=None):
    """Prompt user and create a new ticket."""
    data_file = data_file or get_default_data_file()

    print("\n--- Create Ticket ---")
    title = input("Enter issue title: ").strip()
    category = input("Enter category (Network, Hardware, Software, Other): ").strip()
    urgency = input("Enter urgency (low, medium, high): ").strip()
    users_raw = input("Enter number of affected users: ").strip()

    try:
        affected_users = int(users_raw)
    except ValueError:
        print("Error: Affected users must be a positive integer.")
        return

    try:
        ticket = create_ticket(tickets, title, category, urgency, affected_users)
        save_tickets(tickets, data_file)
        print(f"\nTicket created successfully!")
        print(f"ID: {ticket['id']} | Priority: {ticket['priority']}")
    except ValueError as error:
        print(f"Error: {error}") 


def display_search_results(tickets):
    """Display the required fields for search results."""
    if not tickets:
        print("\nNo matching tickets found.")
        return

    for ticket in tickets:
        print("-" * 40)
        print(f"ID: {ticket.get('id', 'N/A')}")
        print(f"Title: {ticket.get('title', 'N/A')}")
        print(f"Category: {ticket.get('category', 'N/A')}")
        print(f"Priority: {ticket.get('priority', 'N/A')}")
        print(f"Status: {ticket.get('status', 'N/A')}")
        print(f"Assigned to: {ticket.get('assigned_to') or 'Unassigned'}")

    print("-" * 40)


def search_tickets_menu(tickets):
    """Prompt for search criteria and display matching tickets."""
    print("\n--- Search Tickets ---")
    query = input("Title contains (leave blank for any title): ").strip()
    category = input(
        "Category (Network, Hardware, Software, Other; blank for any): "
    ).strip()
    status = input(
        "Status (open, in_progress, resolved; blank for any): "
    ).strip()
    priority = input(
        "Priority (critical, high, medium, low; blank for any): "
    ).strip()

    while True:
        sort_choice = input(
            "Sort results by priority? (y/n): "
        ).strip().lower()

        if sort_choice in {"y", "yes", "n", "no"}:
            break

        print("Please enter y or n.")

    try:
        results = search_tickets(
            tickets,
            query=query,
            category=category,
            status=status,
            priority=priority,
            sort_by_priority=sort_choice in {"y", "yes"},
        )
    except ValueError as error:
        print(f"Error: {error}")
        return

    print("\nSEARCH RESULTS")
    display_search_results(results)


def show_work_queue(tickets):
    """Display active tickets ordered by priority and numeric ID."""
    queue = get_work_queue(tickets)

    print("\nWORK QUEUE")
    if not queue:
        print("\nWork queue is empty.")
        return
    display_tickets(queue)


def assign_ticket_menu(tickets, data_file=None):
    """Prompt user and assign a ticket to a staff member."""
    data_file = data_file or get_default_data_file()

    ticket_id = input("Enter ticket ID: ").strip()
    staff_name = input("Enter staff member's name: ").strip()

    try:
        ticket = assign_ticket(tickets, ticket_id, staff_name)
        save_tickets(tickets, data_file)
        print(f"Ticket {ticket['id']} assigned to {ticket['assigned_to']}.")
    except ValueError as error:
        print(f"Error: {error}")


def change_status_menu(tickets, data_file=None):
    """Prompt user and update a ticket's status."""
    data_file = data_file or get_default_data_file()

    ticket_id = input("Enter ticket ID: ").strip()
    print("Available statuses: open, in_progress, resolved")
    new_status = input("Enter new status: ").strip().lower()

    try:
        ticket = change_status(tickets, ticket_id, new_status)
        save_tickets(tickets, data_file)
        print(f"Ticket {ticket['id']} status changed to {ticket['status']}.")
    except ValueError as error:
        print(f"Error: {error}")


def reopen_ticket_menu(tickets, data_file=None):
    """Prompt user and reopen a resolved ticket."""
    data_file = data_file or get_default_data_file()

    ticket_id = input("Enter ticket ID: ").strip()

    try:
        ticket = reopen_ticket(tickets, ticket_id)
        save_tickets(tickets, data_file)
        print(f"Ticket {ticket['id']} reopened to open status.")
    except ValueError as error:
        print(f"Error: {error}")


def show_report(tickets):
    """Display ticket totals and distributions."""
    report = generate_report(tickets)

    print("\nTICKET REPORT")
    print(f"Total tickets: {report['total_tickets']}")

    print("\nTickets by status:")
    for status, count in report["status_counts"].items():
        print(f"  {status}: {count}")

    print("\nTickets by priority:")
    for priority, count in report["priority_counts"].items():
        print(f"  {priority}: {count}")

    print("\nTickets by category:")
    for category, count in report["category_counts"].items():
        print(f"  {category}: {count}")

    print(f"\nResolved tickets: {report['resolved_tickets']}")
    print(f"Unresolved tickets: {report['unresolved_tickets']}")
    print(
        "Resolution percentage: "
        f"{report['resolution_percentage']:.1f}%"
    )

def main(data_file=None):
    """Run the CampusFlow Helpdesk interactive CLI."""
    target_file = data_file or get_default_data_file()
    tickets = load_tickets(target_file) 
    
    while True:
        print("\n=== CampusFlow Helpdesk ===")
        print("1. Create a ticket")
        print("2. View all tickets")
        print("3. View work queue")
        print("4. Assign a ticket")
        print("5. Change ticket status")
        print("6. Reopen a ticket")
        print("7. View report")
        print("8. Search tickets")
        print("9. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_ticket_menu(tickets, target_file)
        elif choice == "2":
            display_tickets(tickets)
        elif choice == "3":
            show_work_queue(tickets)
        elif choice == "4":
            assign_ticket_menu(tickets, target_file)
        elif choice == "5":
            change_status_menu(tickets, target_file)
        elif choice == "6":
            reopen_ticket_menu(tickets, target_file)
        elif choice == "7":
            show_report(tickets)
        elif choice == "8":
            search_tickets_menu(tickets)
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please choose a number from 1 to 9.")

