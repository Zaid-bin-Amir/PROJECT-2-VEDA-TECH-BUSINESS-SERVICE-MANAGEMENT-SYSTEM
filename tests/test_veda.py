import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from veda.cli import VedaApp
from veda.exceptions import (
    DuplicateRecordError,
    RecordNotFoundError,
    StorageError,
    ValidationError,
)
from veda.managers import CustomerManager, InquiryManager, ProgramManager, ServiceManager
from veda.reports import ReportService
from veda.storage import DataStore
from veda.validators import (
    require_positive_number,
    validate_date,
    validate_email,
    validate_phone,
)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(PROJECT_DIR, "data", "seed_data.json")


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "data.json")
        self.store = DataStore(self.data_path, SEED_PATH)
        self.services = ServiceManager(self.store)
        self.programs = ProgramManager(self.store)
        self.customers = CustomerManager(self.store)
        self.inquiries = InquiryManager(self.store)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class ValidatorTests(unittest.TestCase):
    def test_email(self):
        self.assertEqual(validate_email(" A@B.com "), "a@b.com")
        with self.assertRaises(ValidationError):
            validate_email("not-an-email")

    def test_phone(self):
        self.assertEqual(validate_phone("0300-1234567"), "0300-1234567")
        with self.assertRaises(ValidationError):
            validate_phone("abc")

    def test_date(self):
        self.assertEqual(validate_date("2026-10-24"), "2026-10-24")
        with self.assertRaises(ValidationError):
            validate_date("24-10-2026")

    def test_number(self):
        self.assertEqual(require_positive_number("10", "Price"), 10)
        self.assertEqual(require_positive_number("10.5", "Price"), 10.5)
        for bad in ("0", "-5", "abc", "nan", "inf", ""):
            with self.assertRaises(ValidationError):
                require_positive_number(bad, "Price")


class StorageTests(BaseCase):
    def test_seed_loaded(self):
        self.assertEqual(len(self.store.collection("services")), 6)

    def test_persistence(self):
        self.services.add(name="Data Analytics", category="Consulting", price="900")
        reloaded = DataStore(self.data_path, SEED_PATH)
        names = [record["name"] for record in reloaded.collection("services")]
        self.assertIn("Data Analytics", names)

    def test_corrupt_file(self):
        with open(self.data_path, "w", encoding="utf-8") as handle:
            handle.write("{broken")
        with self.assertRaises(StorageError):
            DataStore(self.data_path, SEED_PATH)

    def test_missing_file_without_seed(self):
        path = os.path.join(self.temp_dir, "new", "empty.json")
        store = DataStore(path)
        self.assertEqual(store.collection("customers"), [])
        self.assertTrue(os.path.exists(path))

    def test_reset(self):
        self.services.delete("S006")
        self.store.reset()
        self.assertEqual(len(self.store.collection("services")), 6)


class ServiceTests(BaseCase):
    def test_add_defaults_and_id(self):
        record = self.services.add(name="Data Analytics", category="Consulting", price="900")
        self.assertEqual(record["id"], "S007")
        self.assertEqual(record["status"], "Active")

    def test_duplicate_name(self):
        with self.assertRaises(DuplicateRecordError):
            self.services.add(name="website development", category="X", price=1)

    def test_invalid_input(self):
        with self.assertRaises(ValidationError):
            self.services.add(name="", category="X", price=1)
        with self.assertRaises(ValidationError):
            self.services.add(name="New", category="X", price="free")
        with self.assertRaises(ValidationError):
            self.services.add(name="New", category="X", price=5, status="Maybe")

    def test_update(self):
        updated = self.services.update("s001", price="950", status="inactive")
        self.assertEqual(updated["price"], 950)
        self.assertEqual(updated["status"], "Inactive")
        self.assertEqual(updated["id"], "S001")

    def test_update_failure_keeps_record(self):
        with self.assertRaises(ValidationError):
            self.services.update("S001", price="-1")
        self.assertEqual(self.services.get("S001")["price"], 800)

    def test_missing_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.services.get("S999")

    def test_delete_unlinked(self):
        self.services.delete("S006")
        self.assertFalse(self.services.exists("S006"))

    def test_delete_linked_blocked(self):
        with self.assertRaises(ValidationError):
            self.services.delete("S001")

    def test_filter(self):
        self.assertEqual(len(self.services.filter(category="development")), 2)
        self.assertEqual(len(self.services.filter(status="Inactive")), 1)
        self.assertEqual(len(self.services.filter(min_price=300, max_price=500)), 3)
        with self.assertRaises(ValidationError):
            self.services.filter(min_price=500, max_price=100)

    def test_search(self):
        self.assertEqual(len(self.services.search("seo")), 1)
        with self.assertRaises(ValidationError):
            self.services.search("  ")


class ProgramTests(BaseCase):
    def test_add(self):
        record = self.programs.add(
            title="Data Science", type="training", duration_weeks="10", seats="20"
        )
        self.assertEqual(record["type"], "Training")
        self.assertEqual(record["status"], "Open")

    def test_invalid_seats(self):
        with self.assertRaises(ValidationError):
            self.programs.add(title="X", type="Training", duration_weeks=4, seats=0)

    def test_filter_by_type(self):
        self.assertEqual(len(self.programs.filter(type="Internship")), 2)


class CustomerTests(BaseCase):
    def test_duplicate_email(self):
        with self.assertRaises(DuplicateRecordError):
            self.customers.add(name="Dup", email="ALI.RAZA@example.com", phone="0300-9999999")

    def test_search_by_name(self):
        self.assertEqual(self.customers.search("sara")[0]["id"], "C002")

    def test_delete_with_inquiries_blocked(self):
        with self.assertRaises(ValidationError):
            self.customers.delete("C001")


class InquiryTests(BaseCase):
    def test_add_valid(self):
        record = self.inquiries.add(
            customer_id="c003", type="service", ref_id="s002", message="Need a quote"
        )
        self.assertEqual(record["id"], "Q009")
        self.assertEqual(record["status"], "Open")
        self.assertEqual(len(record["date"]), 10)

    def test_unknown_customer(self):
        with self.assertRaises(RecordNotFoundError):
            self.inquiries.add(customer_id="C999", type="Service", ref_id="S001", message="Hi")

    def test_wrong_reference_type(self):
        with self.assertRaises(RecordNotFoundError):
            self.inquiries.add(customer_id="C001", type="Program", ref_id="S001", message="Hi")

    def test_change_status(self):
        updated = self.inquiries.set_status("Q001", "closed")
        self.assertEqual(updated["status"], "Closed")
        with self.assertRaises(ValidationError):
            self.inquiries.set_status("Q001", "Pending")

    def test_view_adds_names(self):
        row = self.inquiries.view()[0]
        self.assertEqual(row["customer_name"], "Ali Raza")
        self.assertEqual(row["subject"], "Website Development")

    def test_filter_and_search(self):
        self.assertEqual(len(self.inquiries.filter(status="Open")), 4)
        self.assertEqual(len(self.inquiries.filter(status="open", type="Program")), 1)
        self.assertEqual(len(self.inquiries.search("internship")), 1)
        self.assertEqual(len(self.inquiries.search("Sara Khan")), 2)


class ReportTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.reports = ReportService(
            self.services, self.programs, self.customers, self.inquiries
        )

    def test_service_report(self):
        data = self.reports.service_report()
        self.assertEqual(data["total"], 6)
        self.assertEqual(data["highest_priced"]["name"], "Mobile App Development")
        self.assertEqual(data["average_price"], 625)

    def test_program_report(self):
        data = self.reports.program_report()
        self.assertEqual(data["total_seats"], 113)
        self.assertEqual(data["open_seats"], 65)

    def test_inquiry_report(self):
        data = self.reports.inquiry_report()
        self.assertEqual(data["total"], 8)
        self.assertEqual(data["resolution_rate"], 25.0)

    def test_customer_report(self):
        data = self.reports.customer_report()
        self.assertEqual(data[0]["inquiries"], 2)

    def test_empty_data(self):
        path = os.path.join(self.temp_dir, "empty.json")
        store = DataStore(path)
        reports = ReportService(
            ServiceManager(store), ProgramManager(store), CustomerManager(store), InquiryManager(store)
        )
        self.assertEqual(reports.service_report()["average_price"], 0)
        self.assertEqual(reports.inquiry_report()["resolution_rate"], 0)
        self.assertIn("No records found.", reports.render())

    def test_exports(self):
        text_path = self.reports.export_text(os.path.join(self.temp_dir, "out"))
        csv_path = self.reports.export_inquiries_csv(os.path.join(self.temp_dir, "out"))
        with open(text_path, encoding="utf-8") as handle:
            self.assertIn("VEDA TECHNOLOGY BUSINESS REPORT", handle.read())
        with open(csv_path, encoding="utf-8") as handle:
            self.assertEqual(len(handle.read().strip().splitlines()), 9)


class CliTests(BaseCase):
    def run_app(self, answers):
        feed = iter(answers)
        output = []

        def fake_input(prompt=""):
            output.append(prompt)
            try:
                return next(feed)
            except StopIteration:
                raise EOFError

        app = VedaApp(
            self.data_path,
            SEED_PATH,
            os.path.join(self.temp_dir, "exports"),
            input_func=fake_input,
            output_func=output.append,
        )
        app.run()
        return "\n".join(output)

    def test_list_services(self):
        text = self.run_app(["1", "1", "0", "0"])
        self.assertIn("Website Development", text)
        self.assertIn("6 record(s).", text)

    def test_add_service_through_menu(self):
        text = self.run_app(
            ["1", "2", "Data Analytics", "Consulting", "900", "", "0", "0"]
        )
        self.assertIn("Service added with ID S007.", text)
        with open(self.data_path, encoding="utf-8") as handle:
            saved = json.load(handle)
        self.assertEqual(len(saved["services"]), 7)

    def test_error_is_reported_not_raised(self):
        text = self.run_app(["1", "2", "X", "Y", "abc", "", "0", "0"])
        self.assertIn("Error: Price must be a number.", text)

    def test_invalid_menu_choice(self):
        text = self.run_app(["9", "x", "0"])
        self.assertIn("Invalid choice", text)

    def test_global_search(self):
        text = self.run_app(["6", "cloud", "0"])
        self.assertIn("Cloud Hosting Setup", text)

    def test_inquiry_status_change(self):
        text = self.run_app(["4", "7", "Q001", "Closed", "0", "0"])
        self.assertIn("Inquiry Q001 is now Closed.", text)

    def test_delete_cancel(self):
        text = self.run_app(["1", "4", "S006", "n", "0", "0"])
        self.assertIn("Delete cancelled.", text)
        self.assertTrue(self.services.exists("S006"))

    def test_exit_on_eof(self):
        text = self.run_app([])
        self.assertIn("Goodbye.", text)

    def test_report_menu(self):
        text = self.run_app(["5", "5", "0", "0"])
        self.assertIn("VEDA TECHNOLOGY BUSINESS REPORT", text)


if __name__ == "__main__":
    unittest.main()
