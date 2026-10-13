"""CampusFlow Helpdesk CLI main entry point."""

from campusflow.cli import (
    assign_ticket_menu,
    change_status_menu,
    create_ticket_menu,
    display_tickets,
    main,
    reopen_ticket_menu,
    show_report,
    show_work_queue,
)

if __name__ == "__main__":
    main()