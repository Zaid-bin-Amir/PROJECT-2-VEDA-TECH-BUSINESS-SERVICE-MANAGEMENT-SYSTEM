import csv
import os
from collections import Counter
from datetime import datetime

from .display import (
    CUSTOMER_ACTIVITY_COLUMNS,
    count_table,
    format_table,
    heading,
)

INQUIRY_EXPORT_FIELDS = [
    "id",
    "customer_id",
    "customer_name",
    "type",
    "ref_id",
    "subject",
    "message",
    "status",
    "date",
]


class ReportService:
    def __init__(self, services, programs, customers, inquiries):
        self.services = services
        self.programs = programs
        self.customers = customers
        self.inquiries = inquiries

    def service_report(self):
        records = self.services.list_all()
        prices = [record["price"] for record in records]
        return {
            "total": len(records),
            "by_category": dict(Counter(record["category"] for record in records)),
            "by_status": dict(Counter(record["status"] for record in records)),
            "average_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "highest_priced": max(records, key=lambda r: r["price"]) if records else None,
            "lowest_priced": min(records, key=lambda r: r["price"]) if records else None,
        }

    def program_report(self):
        records = self.programs.list_all()
        durations = [record["duration_weeks"] for record in records]
        return {
            "total": len(records),
            "by_type": dict(Counter(record["type"] for record in records)),
            "by_status": dict(Counter(record["status"] for record in records)),
            "total_seats": sum(record["seats"] for record in records),
            "open_seats": sum(
                record["seats"] for record in records if record["status"] == "Open"
            ),
            "average_duration_weeks": round(sum(durations) / len(durations), 1)
            if durations
            else 0,
        }

    def inquiry_report(self):
        rows = self.inquiries.view()
        total = len(rows)
        closed = sum(1 for row in rows if row["status"] == "Closed")
        return {
            "total": total,
            "by_status": dict(Counter(row["status"] for row in rows)),
            "by_type": dict(Counter(row["type"] for row in rows)),
            "resolution_rate": round(closed / total * 100, 1) if total else 0,
            "top_subjects": Counter(row["subject"] for row in rows).most_common(3),
        }

    def customer_report(self):
        rows = self.inquiries.view()
        report = []
        for customer in self.customers.list_all():
            mine = [row for row in rows if row["customer_id"] == customer["id"]]
            report.append(
                {
                    "id": customer["id"],
                    "name": customer["name"],
                    "inquiries": len(mine),
                    "open": sum(1 for row in mine if row["status"] != "Closed"),
                }
            )
        report.sort(key=lambda item: (-item["inquiries"], item["name"]))
        return report

    def render_services(self):
        data = self.service_report()
        lines = [
            heading("Service Report"),
            f"Total services: {data['total']}",
            f"Average price: {data['average_price']}",
        ]
        if data["highest_priced"]:
            top = data["highest_priced"]
            low = data["lowest_priced"]
            lines.append(f"Highest priced: {top['name']} ({top['price']})")
            lines.append(f"Lowest priced: {low['name']} ({low['price']})")
        lines += ["", count_table(data["by_category"], "Category")]
        lines += ["", count_table(data["by_status"], "Status")]
        return "\n".join(lines)

    def render_programs(self):
        data = self.program_report()
        lines = [
            heading("Program Report"),
            f"Total programs: {data['total']}",
            f"Total seats: {data['total_seats']}",
            f"Seats in open programs: {data['open_seats']}",
            f"Average duration: {data['average_duration_weeks']} weeks",
            "",
            count_table(data["by_type"], "Type"),
            "",
            count_table(data["by_status"], "Status"),
        ]
        return "\n".join(lines)

    def render_inquiries(self):
        data = self.inquiry_report()
        subjects = [{"subject": name, "count": count} for name, count in data["top_subjects"]]
        lines = [
            heading("Inquiry Report"),
            f"Total inquiries: {data['total']}",
            f"Resolution rate: {data['resolution_rate']}%",
            "",
            count_table(data["by_status"], "Status"),
            "",
            count_table(data["by_type"], "Type"),
            "",
            "Most requested",
            format_table(subjects, [("subject", "Subject"), ("count", "Inquiries")]),
        ]
        return "\n".join(lines)

    def render_customers(self):
        return "\n".join(
            [
                heading("Customer Activity"),
                format_table(self.customer_report(), CUSTOMER_ACTIVITY_COLUMNS),
            ]
        )

    def render(self):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        parts = [
            "VEDA TECHNOLOGY BUSINESS REPORT",
            f"Generated on {stamp}",
            "",
            self.render_services(),
            "",
            self.render_programs(),
            "",
            self.render_inquiries(),
            "",
            self.render_customers(),
        ]
        return "\n".join(parts)

    def export_text(self, directory):
        os.makedirs(directory, exist_ok=True)
        name = f"business_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.render() + "\n")
        return path

    def export_inquiries_csv(self, directory):
        os.makedirs(directory, exist_ok=True)
        name = f"inquiries_{datetime.now():%Y%m%d_%H%M%S}.csv"
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=INQUIRY_EXPORT_FIELDS, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(self.inquiries.view())
        return path
