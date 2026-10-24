from datetime import date

from .constants import (
    INQUIRY_STATUSES,
    INQUIRY_TYPES,
    PROGRAM_STATUSES,
    PROGRAM_TYPES,
    SERVICE_STATUSES,
)
from .exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError
from .validators import (
    is_given,
    require_choice,
    require_non_negative_number,
    require_positive_int,
    require_positive_number,
    require_text,
    validate_date,
    validate_email,
    validate_phone,
)


class BaseManager:
    collection = ""
    prefix = ""
    label = "Record"
    search_fields = ()
    reference_field = None

    def __init__(self, store):
        self.store = store

    @property
    def records(self):
        return self.store.collection(self.collection)

    def view(self):
        return [dict(record) for record in self.records]

    def list_all(self):
        return self.view()

    def next_id(self):
        numbers = []
        for record in self.records:
            record_id = record["id"]
            suffix = record_id[len(self.prefix):]
            if record_id.startswith(self.prefix) and suffix.isdigit():
                numbers.append(int(suffix))
        return f"{self.prefix}{max(numbers, default=0) + 1:03d}"

    def find(self, record_id):
        key = require_text(record_id, f"{self.label} ID").upper()
        for record in self.records:
            if record["id"].upper() == key:
                return record
        raise RecordNotFoundError(f"{self.label} '{key}' was not found.")

    def get(self, record_id):
        return dict(self.find(record_id))

    def exists(self, record_id):
        try:
            self.find(record_id)
        except (RecordNotFoundError, ValidationError):
            return False
        return True

    def clean(self, fields, exclude_id=None):
        raise NotImplementedError

    def add(self, **fields):
        cleaned = self.clean(fields)
        record = {"id": self.next_id(), **cleaned}
        self.records.append(record)
        self.store.save()
        return dict(record)

    def update(self, record_id, **changes):
        record = self.find(record_id)
        merged = dict(record)
        for key, value in changes.items():
            if is_given(value):
                merged[key] = value
        cleaned = self.clean(merged, exclude_id=record["id"])
        keep_id = record["id"]
        record.clear()
        record["id"] = keep_id
        record.update(cleaned)
        self.store.save()
        return dict(record)

    def check_delete(self, record):
        if self.reference_field is None:
            return
        for inquiry in self.store.collection("inquiries"):
            if inquiry.get(self.reference_field) == record["id"]:
                raise ValidationError(
                    f"{self.label} '{record['id']}' is linked to inquiries and cannot be deleted."
                )

    def delete(self, record_id):
        record = self.find(record_id)
        self.check_delete(record)
        self.records.remove(record)
        self.store.save()
        return dict(record)

    def search(self, text):
        needle = require_text(text, "Search text").lower()
        results = []
        for row in self.view():
            for field in self.search_fields:
                if needle in str(row.get(field, "")).lower():
                    results.append(row)
                    break
        return results

    def filter(self, **criteria):
        rows = self.view()
        for key, value in criteria.items():
            if not is_given(value):
                continue
            wanted = str(value).strip().lower()
            rows = [row for row in rows if str(row.get(key, "")).lower() == wanted]
        return rows

    def ensure_unique(self, field, value, exclude_id=None):
        for record in self.records:
            if record["id"] == exclude_id:
                continue
            if str(record.get(field, "")).lower() == value.lower():
                raise DuplicateRecordError(
                    f"A {self.label.lower()} with this {field} already exists."
                )


class ServiceManager(BaseManager):
    collection = "services"
    prefix = "S"
    label = "Service"
    search_fields = ("id", "name", "category", "status")
    reference_field = "ref_id"

    def clean(self, fields, exclude_id=None):
        name = require_text(fields.get("name"), "Service name")
        self.ensure_unique("name", name, exclude_id)
        return {
            "name": name,
            "category": require_text(fields.get("category"), "Category"),
            "price": require_positive_number(fields.get("price"), "Price"),
            "status": require_choice(
                fields.get("status") or "Active", SERVICE_STATUSES, "Status"
            ),
        }

    def filter(self, category=None, status=None, min_price=None, max_price=None):
        rows = super().filter(category=category, status=status)
        low = None
        high = None
        if is_given(min_price):
            low = require_non_negative_number(min_price, "Minimum price")
        if is_given(max_price):
            high = require_non_negative_number(max_price, "Maximum price")
        if low is not None and high is not None and low > high:
            raise ValidationError("Minimum price cannot be greater than maximum price.")
        if low is not None:
            rows = [row for row in rows if row["price"] >= low]
        if high is not None:
            rows = [row for row in rows if row["price"] <= high]
        return rows

    def categories(self):
        return sorted({record["category"] for record in self.records})


class ProgramManager(BaseManager):
    collection = "programs"
    prefix = "P"
    label = "Program"
    search_fields = ("id", "title", "type", "status")
    reference_field = "ref_id"

    def clean(self, fields, exclude_id=None):
        title = require_text(fields.get("title"), "Program title")
        self.ensure_unique("title", title, exclude_id)
        return {
            "title": title,
            "type": require_choice(fields.get("type"), PROGRAM_TYPES, "Type"),
            "duration_weeks": require_positive_int(
                fields.get("duration_weeks"), "Duration (weeks)"
            ),
            "seats": require_positive_int(fields.get("seats"), "Seats"),
            "status": require_choice(
                fields.get("status") or "Open", PROGRAM_STATUSES, "Status"
            ),
        }


class CustomerManager(BaseManager):
    collection = "customers"
    prefix = "C"
    label = "Customer"
    search_fields = ("id", "name", "email", "phone")
    reference_field = "customer_id"

    def clean(self, fields, exclude_id=None):
        email = validate_email(fields.get("email"))
        self.ensure_unique("email", email, exclude_id)
        return {
            "name": require_text(fields.get("name"), "Customer name"),
            "email": email,
            "phone": validate_phone(fields.get("phone")),
        }


class InquiryManager(BaseManager):
    collection = "inquiries"
    prefix = "Q"
    label = "Inquiry"
    search_fields = (
        "id",
        "customer_id",
        "customer_name",
        "type",
        "subject",
        "message",
        "status",
    )

    def view(self):
        customers = {
            record["id"]: record["name"] for record in self.store.collection("customers")
        }
        services = {
            record["id"]: record["name"] for record in self.store.collection("services")
        }
        programs = {
            record["id"]: record["title"] for record in self.store.collection("programs")
        }
        rows = []
        for record in self.records:
            row = dict(record)
            row["customer_name"] = customers.get(record["customer_id"], "Unknown")
            lookup = services if record["type"] == "Service" else programs
            row["subject"] = lookup.get(record["ref_id"], "Unknown")
            rows.append(row)
        return rows

    def clean(self, fields, exclude_id=None):
        customer_id = require_text(fields.get("customer_id"), "Customer ID").upper()
        known_customers = {record["id"] for record in self.store.collection("customers")}
        if customer_id not in known_customers:
            raise RecordNotFoundError(f"Customer '{customer_id}' was not found.")
        inquiry_type = require_choice(fields.get("type"), INQUIRY_TYPES, "Type")
        ref_id = require_text(fields.get("ref_id"), "Reference ID").upper()
        source = "services" if inquiry_type == "Service" else "programs"
        known_refs = {record["id"] for record in self.store.collection(source)}
        if ref_id not in known_refs:
            raise RecordNotFoundError(f"{inquiry_type} '{ref_id}' was not found.")
        raw_date = fields.get("date")
        return {
            "customer_id": customer_id,
            "type": inquiry_type,
            "ref_id": ref_id,
            "message": require_text(fields.get("message"), "Message"),
            "status": require_choice(
                fields.get("status") or "Open", INQUIRY_STATUSES, "Status"
            ),
            "date": validate_date(raw_date) if is_given(raw_date) else date.today().isoformat(),
        }

    def set_status(self, record_id, status):
        return self.update(record_id, status=status)
