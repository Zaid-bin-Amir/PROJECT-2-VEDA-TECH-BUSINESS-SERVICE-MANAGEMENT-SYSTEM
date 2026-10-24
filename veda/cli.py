import os

from .display import (
    CUSTOMER_COLUMNS,
    INQUIRY_COLUMNS,
    PROGRAM_COLUMNS,
    SERVICE_COLUMNS,
    format_table,
)
from .exceptions import VedaError
from .managers import CustomerManager, InquiryManager, ProgramManager, ServiceManager
from .reports import ReportService
from .storage import DataStore


class VedaApp:
    def __init__(self, data_path, seed_path, export_dir, input_func=input, output_func=print):
        self.store = DataStore(data_path, seed_path)
        self.services = ServiceManager(self.store)
        self.programs = ProgramManager(self.store)
        self.customers = CustomerManager(self.store)
        self.inquiries = InquiryManager(self.store)
        self.reports = ReportService(
            self.services, self.programs, self.customers, self.inquiries
        )
        self.export_dir = export_dir
        self.read = input_func
        self.write = output_func
        self.entities = {
            "1": {
                "title": "Service Management",
                "manager": self.services,
                "columns": SERVICE_COLUMNS,
                "fields": [
                    ("name", "Service name"),
                    ("category", "Category"),
                    ("price", "Price"),
                    ("status", "Status [Active/Inactive]"),
                ],
                "filters": [
                    ("category", "Category"),
                    ("status", "Status"),
                    ("min_price", "Minimum price"),
                    ("max_price", "Maximum price"),
                ],
                "extra": [],
            },
            "2": {
                "title": "Program Management",
                "manager": self.programs,
                "columns": PROGRAM_COLUMNS,
                "fields": [
                    ("title", "Program title"),
                    ("type", "Type [Training/Internship]"),
                    ("duration_weeks", "Duration in weeks"),
                    ("seats", "Seats"),
                    ("status", "Status [Open/Closed/Upcoming]"),
                ],
                "filters": [("type", "Type"), ("status", "Status")],
                "extra": [],
            },
            "3": {
                "title": "Customer Management",
                "manager": self.customers,
                "columns": CUSTOMER_COLUMNS,
                "fields": [
                    ("name", "Customer name"),
                    ("email", "Email"),
                    ("phone", "Phone"),
                ],
                "filters": [],
                "extra": [],
            },
            "4": {
                "title": "Inquiry Management",
                "manager": self.inquiries,
                "columns": INQUIRY_COLUMNS,
                "fields": [
                    ("customer_id", "Customer ID"),
                    ("type", "Type [Service/Program]"),
                    ("ref_id", "Service or Program ID"),
                    ("message", "Message"),
                    ("status", "Status [Open/In Progress/Closed]"),
                    ("date", "Date YYYY-MM-DD"),
                ],
                "filters": [
                    ("status", "Status"),
                    ("type", "Type"),
                    ("customer_id", "Customer ID"),
                    ("ref_id", "Service or Program ID"),
                ],
                "extra": [("Change inquiry status", self.change_status)],
            },
        }

    def show(self, rows, columns):
        self.write(format_table(rows, columns))
        if rows:
            self.write(f"{len(rows)} record(s).")

    def collect(self, fields, suffix=""):
        values = {}
        for key, prompt in fields:
            answer = self.read(f"{prompt}{suffix}: ").strip()
            if answer:
                values[key] = answer
        return values

    def list_records(self, entity):
        self.show(entity["manager"].view(), entity["columns"])

    def add_record(self, entity):
        values = self.collect(entity["fields"], " (Enter to skip optional)")
        record = entity["manager"].add(**values)
        self.write(f"{entity['manager'].label} added with ID {record['id']}.")

    def update_record(self, entity):
        manager = entity["manager"]
        record_id = self.read(f"{manager.label} ID to update: ")
        current = manager.get(record_id)
        self.show([current], [(key, key) for key in current])
        values = self.collect(entity["fields"], " (Enter to keep)")
        if not values:
            self.write("Nothing changed.")
            return
        updated = manager.update(current["id"], **values)
        self.write(f"{manager.label} {updated['id']} updated.")

    def delete_record(self, entity):
        manager = entity["manager"]
        record_id = self.read(f"{manager.label} ID to delete: ")
        record = manager.get(record_id)
        answer = self.read(f"Delete {record['id']}? (y/n): ").strip().lower()
        if answer == "y":
            manager.delete(record["id"])
            self.write(f"{manager.label} {record['id']} deleted.")
        else:
            self.write("Delete cancelled.")

    def search_records(self, entity):
        text = self.read("Search text: ")
        self.show(entity["manager"].search(text), entity["columns"])

    def filter_records(self, entity):
        values = self.collect(entity["filters"], " (Enter to skip)")
        if not values:
            self.write("No filters entered.")
            return
        self.show(entity["manager"].filter(**values), entity["columns"])

    def change_status(self, entity):
        manager = entity["manager"]
        record_id = self.read("Inquiry ID: ")
        status = self.read("New status [Open/In Progress/Closed]: ")
        updated = manager.set_status(record_id, status)
        self.write(f"Inquiry {updated['id']} is now {updated['status']}.")

    def entity_menu(self, entity):
        actions = [
            ("List all", self.list_records),
            ("Add new", self.add_record),
            ("Update", self.update_record),
            ("Delete", self.delete_record),
            ("Search", self.search_records),
        ]
        if entity["filters"]:
            actions.append(("Filter", self.filter_records))
        actions.extend(entity["extra"])
        while True:
            self.write(f"\n=== {entity['title']} ===")
            for number, (label, _) in enumerate(actions, 1):
                self.write(f"{number}. {label}")
            self.write("0. Back")
            choice = self.read("Choose an option: ").strip()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(actions):
                try:
                    actions[int(choice) - 1][1](entity)
                except VedaError as error:
                    self.write(f"Error: {error}")
            else:
                self.write("Invalid choice, please try again.")

    def report_menu(self):
        options = {
            "1": ("Service report", lambda: self.write(self.reports.render_services())),
            "2": ("Program report", lambda: self.write(self.reports.render_programs())),
            "3": ("Inquiry report", lambda: self.write(self.reports.render_inquiries())),
            "4": ("Customer activity", lambda: self.write(self.reports.render_customers())),
            "5": ("Full business report", lambda: self.write(self.reports.render())),
            "6": ("Export full report to text file", self.export_report),
            "7": ("Export inquiries to CSV", self.export_inquiries),
        }
        while True:
            self.write("\n=== Reports ===")
            for key, (label, _) in options.items():
                self.write(f"{key}. {label}")
            self.write("0. Back")
            choice = self.read("Choose an option: ").strip()
            if choice == "0":
                return
            if choice in options:
                try:
                    options[choice][1]()
                except VedaError as error:
                    self.write(f"Error: {error}")
                except OSError as error:
                    self.write(f"Error: could not write file ({error}).")
            else:
                self.write("Invalid choice, please try again.")

    def export_report(self):
        path = self.reports.export_text(self.export_dir)
        self.write(f"Report saved to {path}")

    def export_inquiries(self):
        path = self.reports.export_inquiries_csv(self.export_dir)
        self.write(f"Inquiries saved to {path}")

    def global_search(self):
        text = self.read("Search everything for: ")
        found = False
        for entity in self.entities.values():
            rows = entity["manager"].search(text)
            if rows:
                found = True
                self.write(f"\n{entity['title']}")
                self.show(rows, entity["columns"])
        if not found:
            self.write("No records found.")

    def reset_data(self):
        answer = self.read("Reset all data to the original sample data? (y/n): ").strip().lower()
        if answer == "y":
            self.store.reset()
            self.write("Sample data restored.")
        else:
            self.write("Reset cancelled.")

    def run(self):
        self.write("Veda Technology Business & Service Management System")
        while True:
            self.write("\n=== Main Menu ===")
            for key, entity in self.entities.items():
                self.write(f"{key}. {entity['title']}")
            self.write("5. Reports")
            self.write("6. Search everything")
            self.write("7. Reset to sample data")
            self.write("0. Exit")
            try:
                choice = self.read("Choose an option: ").strip()
            except (EOFError, KeyboardInterrupt):
                self.write("\nGoodbye.")
                return
            try:
                if choice == "0":
                    self.write("Goodbye.")
                    return
                if choice in self.entities:
                    self.entity_menu(self.entities[choice])
                elif choice == "5":
                    self.report_menu()
                elif choice == "6":
                    self.global_search()
                elif choice == "7":
                    self.reset_data()
                else:
                    self.write("Invalid choice, please try again.")
            except VedaError as error:
                self.write(f"Error: {error}")
            except (EOFError, KeyboardInterrupt):
                self.write("\nGoodbye.")
                return


def build_app(base_dir):
    data_dir = os.path.join(base_dir, "data")
    return VedaApp(
        data_path=os.path.join(data_dir, "veda_data.json"),
        seed_path=os.path.join(data_dir, "seed_data.json"),
        export_dir=os.path.join(base_dir, "exports"),
    )
