SERVICE_COLUMNS = [
    ("id", "ID"),
    ("name", "Service"),
    ("category", "Category"),
    ("price", "Price"),
    ("status", "Status"),
]

PROGRAM_COLUMNS = [
    ("id", "ID"),
    ("title", "Program"),
    ("type", "Type"),
    ("duration_weeks", "Weeks"),
    ("seats", "Seats"),
    ("status", "Status"),
]

CUSTOMER_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("email", "Email"),
    ("phone", "Phone"),
]

INQUIRY_COLUMNS = [
    ("id", "ID"),
    ("customer_name", "Customer"),
    ("type", "Type"),
    ("subject", "Subject"),
    ("status", "Status"),
    ("date", "Date"),
    ("message", "Message"),
]

CUSTOMER_ACTIVITY_COLUMNS = [
    ("id", "ID"),
    ("name", "Customer"),
    ("inquiries", "Inquiries"),
    ("open", "Not Closed"),
]


def shorten(text, limit):
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def format_table(rows, columns, max_width=40):
    if not rows:
        return "No records found."
    headers = [title for _, title in columns]
    body = [
        [shorten(str(row.get(key, "")), max_width) for key, _ in columns]
        for row in rows
    ]
    widths = [
        max(len(headers[index]), max(len(line[index]) for line in body))
        for index in range(len(headers))
    ]

    def render(cells):
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

    divider = "-+-".join("-" * width for width in widths)
    lines = [render(headers), divider]
    lines.extend(render(line) for line in body)
    return "\n".join(lines)


def heading(text):
    return f"{text}\n{'-' * len(text)}"


def count_table(mapping, label):
    rows = [{"label": key, "count": value} for key, value in sorted(mapping.items())]
    return format_table(rows, [("label", label), ("count", "Count")])
