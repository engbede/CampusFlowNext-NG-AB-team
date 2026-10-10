from reports import generate_report
from storage import load_tickets, save_tickets
from ticket_manager import assign_ticket, change_status, get_work_queue


DATA_FILE = "tickets.json"


def display_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in tickets:
        print("-" * 40)
        print(f"ID: {ticket['id']}")
        print(f"Title: {ticket['title']}")
        print(f"Priority: {ticket['priority']}")
        print(f"Status: {ticket['status']}")
        print(f"Assigned to: {ticket.get('assigned_to') or 'Unassigned'}")

    print("-" * 40)


def show_work_queue(tickets):
    queue = get_work_queue(tickets)

    print("\nWORK QUEUE")
    display_tickets(queue)


def assign_ticket_menu(tickets):
    ticket_id = input("Enter ticket ID: ").strip()
    staff_name = input("Enter staff member's name: ").strip()

    try:
        ticket = assign_ticket(tickets, ticket_id, staff_name)
        save_tickets(tickets, DATA_FILE)
        print(f"Ticket {ticket['id']} assigned to {ticket['assigned_to']}.")
    except ValueError as error:
        print(f"Error: {error}")


def change_status_menu(tickets):
    ticket_id = input("Enter ticket ID: ").strip()

    print("Available statuses: open, in_progress, resolved")
    new_status = input("Enter new status: ").strip()

    try:
        ticket = change_status(tickets, ticket_id, new_status)
        save_tickets(tickets, DATA_FILE)
        print(f"Ticket {ticket['id']} status changed to {ticket['status']}.")
    except ValueError as error:
        print(f"Error: {error}")


def show_report(tickets):
    report = generate_report(tickets)

    print("\nTICKET REPORT")
    print(f"Total tickets: {report['total_tickets']}")

    print("\nTickets by status:")
    for status, count in report["status_counts"].items():
        print(f"  {status}: {count}")

    print("\nTickets by priority:")
    for priority, count in report["priority_counts"].items():
        print(f"  {priority}: {count}")


def main():
    tickets = load_tickets(DATA_FILE)

    while True:
        print("\n=== CampusFlow Helpdesk ===")
        print("1. View all tickets")
        print("2. View work queue")
        print("3. Assign a ticket")
        print("4. Change ticket status")
        print("5. View report")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            display_tickets(tickets)
        elif choice == "2":
            show_work_queue(tickets)
        elif choice == "3":
            assign_ticket_menu(tickets)
        elif choice == "4":
            change_status_menu(tickets)
        elif choice == "5":
            show_report(tickets)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please choose a number from 1 to 6.")


if __name__ == "__main__":
    main()