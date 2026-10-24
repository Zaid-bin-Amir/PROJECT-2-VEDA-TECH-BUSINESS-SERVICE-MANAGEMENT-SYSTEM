# Veda Technology Business & Service Management System

A menu-driven Python application that models the day-to-day operations of a technology and digital-services company: services, training and internship programs, customers, and customer inquiries / service requests.
# Veda Technology Business & Service Management System

A menu-driven Python application that models the daily operations of a technology and digital-services company. It manages **services**, **training and internship programs**, **customers**, and **customer inquiries / service requests**, and produces simple business reports.

> **Data notice:** All data in this project is synthetic. The application does not connect to any private Veda Technology production data.

---

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [How to Use the Application](#how-to-use-the-application)
6. [Sample Output](#sample-output)
7. [Data Model](#data-model)
8. [Validation and Error Handling](#validation-and-error-handling)
9. [Reports and Exports](#reports-and-exports)
10. [Running the Tests](#running-the-tests)
11. [Uploading to GitHub](#uploading-to-github)
12. [Python Concepts Demonstrated](#python-concepts-demonstrated)
13. [Possible Improvements](#possible-improvements)

---

## Features

| Module | What you can do |
|--------|-----------------|
| **Service Management** | Add, update, delete, list and search services. Filter by category, status and price range. |
| **Program Management** | Manage training and internship programs with duration, seats and status. Filter by type and status. |
| **Customer Management** | Store customers with validated email and phone. Duplicate emails are rejected. |
| **Inquiry Management** | Record inquiries linked to a customer and to a service or program. Track status: Open, In Progress, Closed. Filter by status, type, customer or service/program. |
| **Global Search** | Search across services, programs, customers and inquiries in one step. |
| **Reports** | Service, program, inquiry and customer-activity reports plus a full business report. |
| **Export** | Save the full report as a text file and inquiries as a CSV file. |
| **Reset** | Restore the original sample data at any time. |

Additional highlights:

- JSON storage with safe saving, so the data file is never left half-written
- Automatic IDs: `S001`, `P001`, `C001`, `Q001`, and so on
- Referential integrity: a service, program or customer linked to inquiries cannot be deleted
- Case-insensitive IDs, searches and filters
- 46 automated unit tests

---

## Technologies Used

- **Python 3.8+** (standard library only, no packages to install)
- **JSON** for persistent data and **CSV** for exports
- **unittest** for testing
- **VS Code** or PyCharm for development
- **Git and GitHub** for version control

---

## Project Structure

```
veda_system/
├── main.py                 Entry point
├── README.md               This file
├── .gitignore
├── data/
│   ├── veda_data.json      Working data (changes as you use the app)
│   └── seed_data.json      Original sample data (used by Reset)
├── veda/
│   ├── cli.py              Menus and user interaction
│   ├── managers.py         Service, Program, Customer and Inquiry classes
│   ├── reports.py          Report calculations, text and CSV export
│   ├── storage.py          JSON loading and saving
│   ├── validators.py       Input validation helpers
│   ├── display.py          Table formatting and column layouts
│   ├── constants.py        Allowed statuses and types
│   └── exceptions.py       Custom exception classes
└── tests/
    └── test_veda.py        Unit tests
```

---

## Getting Started

### 1. Requirements

Python 3.8 or newer. Check with:

```
python --version
```

If Python is missing, download it from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick **"Add Python to PATH"** during installation.

### 2. Open the project

Extract the zip file, then in VS Code choose **File → Open Folder** and select the `veda_system` folder.

### 3. Run the application

Open a terminal in VS Code (**Terminal → New Terminal**) and run:

```
python main.py
```

Alternative commands if the first one does not work:

| System | Command |
|--------|---------|
| Windows | `py main.py` |
| macOS / Linux | `python3 main.py` |

You can also open `main.py` in VS Code and press the **Run (▶)** button.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `python is not recognized` | Install Python and tick "Add Python to PATH", then restart VS Code. |
| `can't open file 'main.py'` | The terminal is in the wrong folder. Run `cd veda_system` first. |
| `Startup error: Could not read data file` | The JSON file is damaged. Delete `data/veda_data.json`; the app recreates it from `seed_data.json`. |

---

## How to Use the Application

When the app starts you see the main menu:

```
=== Main Menu ===
1. Service Management
2. Program Management
3. Customer Management
4. Inquiry Management
5. Reports
6. Search everything
7. Reset to sample data
0. Exit
```

Type a number and press **Enter**.

### Inside a module

Each of the four modules offers these actions:

| Option | Description |
|--------|-------------|
| List all | Show every record in a table |
| Add new | Enter the details one by one |
| Update | Enter an ID, then press Enter on any field to keep its current value |
| Delete | Enter an ID and confirm with `y` |
| Search | Find records by any text |
| Filter | Narrow records by status, category, type and similar fields |

The Inquiry module has one more option, **Change inquiry status**, for moving an inquiry from Open to In Progress to Closed.

### Quick walkthrough

1. Choose `1` (Service Management), then `1` (List all) to see the sample services.
2. Choose `2` (Add new) and enter a name, category, price and status. Leave status empty to use `Active`.
3. Go back with `0`, choose `4` (Inquiry Management), then `2` (Add new). Use customer `C001`, type `Service`, and service `S001`.
4. Choose `5` (Reports) and then `5` (Full business report) to see the totals update.

---

## Sample Output

Listing services:

```
ID   | Service                 | Category          | Price | Status
-----+-------------------------+-------------------+-------+---------
S001 | Website Development     | Development       | 800   | Active
S002 | Mobile App Development  | Development       | 1500  | Active
S003 | SEO Optimization        | Digital Marketing | 300   | Active
S004 | Social Media Management | Digital Marketing | 250   | Active
S005 | Cloud Hosting Setup     | Infrastructure    | 400   | Active
S006 | UI/UX Design            | Design            | 500   | Inactive
6 record(s).
```

Inquiry report:

```
Inquiry Report
--------------
Total inquiries: 8
Resolution rate: 25.0%

Status      | Count
------------+------
Closed      | 2
In Progress | 2
Open        | 4
```

---

## Data Model

| Collection | Fields |
|------------|--------|
| **services** | `id`, `name`, `category`, `price`, `status` (Active / Inactive) |
| **programs** | `id`, `title`, `type` (Training / Internship), `duration_weeks`, `seats`, `status` (Open / Closed / Upcoming) |
| **customers** | `id`, `name`, `email`, `phone` |
| **inquiries** | `id`, `customer_id`, `type` (Service / Program), `ref_id`, `message`, `status` (Open / In Progress / Closed), `date` |

How the records connect:

```
customers ──< inquiries >── services
                  └───────── programs
```

An inquiry belongs to one customer and refers to either one service or one program.

Sample data included: 6 services, 5 programs, 6 customers and 8 inquiries.

---

## Validation and Error Handling

The application never crashes on bad input. Errors are shown as a short message and you return to the menu.

| Check | Rule |
|-------|------|
| Required text | Cannot be empty |
| Price | Must be a number greater than zero |
| Seats and duration | Must be whole numbers greater than zero |
| Email | Must be a valid address and unique among customers |
| Phone | Digits with optional `+`, spaces and dashes |
| Date | Must use `YYYY-MM-DD`; defaults to today when left empty |
| Status and type | Must be one of the allowed values (case-insensitive) |
| Customer and service/program IDs | Must exist when creating an inquiry |
| Delete | Blocked when the record is linked to inquiries |
| Duplicates | Service names, program titles and customer emails must be unique |
| Data file | A damaged JSON file produces a clear error instead of a crash |

Custom exceptions live in `veda/exceptions.py`: `ValidationError`, `RecordNotFoundError`, `DuplicateRecordError` and `StorageError`.

---

## Reports and Exports

Open **5. Reports** from the main menu.

| Option | Contents |
|--------|----------|
| Service report | Total, average price, highest and lowest priced, counts by category and status |
| Program report | Total programs, total and open seats, average duration, counts by type and status |
| Inquiry report | Total, resolution rate, counts by status and type, most requested services/programs |
| Customer activity | Inquiries per customer and how many are not yet closed |
| Full business report | All of the above together |
| Export to text file | Saves the full report in the `exports/` folder |
| Export inquiries to CSV | Saves all inquiries in the `exports/` folder, ready for Excel |

The `exports/` folder is created automatically the first time you export.

---

## Running the Tests

From the project folder:

```
python -m unittest discover -s tests -v
```

The tests cover validators, storage, all four managers, reports, exports and the menu flow. Tests use a temporary copy of the data, so your real data is never changed.

---

## Uploading to GitHub

1. Create an empty repository on GitHub (do not add a README there).
2. In the VS Code terminal, inside the project folder, run:

```
git init
git add .
git commit -m "Veda Technology Business & Service Management System"
git branch -M main
git remote add origin https://github.com/<your-username>/<repository-name>.git
git push -u origin main
```

Replace `<your-username>` and `<repository-name>` with your own values.

---

## Python Concepts Demonstrated

- Functions and modules
- Classes, inheritance and properties
- Lists and dictionaries for structured records
- File handling with JSON and CSV
- Input validation and custom exceptions
- Searching, filtering and sorting
- Report generation and aggregation with `collections.Counter`
- Unit testing with `unittest`

---

## Possible Improvements

- A graphical or web interface (Tkinter, Flask or Streamlit)
- User login with roles (admin and staff)
- Inquiry assignment to staff members and due dates
- Charts in reports
- A database such as SQLite in place of JSON
All data is public or synthetic. The project does not connect to any private Veda Technology system.

## Features

- Service management: add, update, delete, list, search, filter by category, status and price range
- Program management: training and internship programs with duration, seats and status
- Customer management: validated email and phone, unique emails
- Inquiry management: link a customer to a service or program, track status (Open, In Progress, Closed)
- Search and filtering in every module, plus a global search across all data
- Business reports: services, programs, inquiries, customer activity, full report
- Export reports to a text file and inquiries to CSV (saved in `exports/`)
- JSON storage with atomic saves, so a crash never leaves a half-written file
- Input validation and exception handling for invalid input and missing records
- Referential integrity: a service, program or customer that has inquiries cannot be deleted
- Unit tests for validators, storage, managers, reports and the menu

## Requirements

- Python 3.8 or newer
- No third-party packages

## Run

```
python main.py
```

On Windows you can also use `py main.py`.

## Run the tests

```
python -m unittest discover -s tests -v
```

## Project structure

```
veda_system/
  main.py              entry point
  README.md
  data/
    veda_data.json     working data (changes as you use the app)
    seed_data.json     original sample data
  veda/
    cli.py             menus and user interaction
    managers.py        Service, Program, Customer and Inquiry classes
    reports.py         report calculations, text and CSV export
    storage.py         JSON load and save
    validators.py      input validation helpers
    display.py         table formatting and column layouts
    constants.py       allowed statuses and types
    exceptions.py      custom exceptions
  tests/
    test_veda.py
```

## Data model

| Collection | Fields |
|------------|--------|
| services   | id, name, category, price, status (Active / Inactive) |
| programs   | id, title, type (Training / Internship), duration_weeks, seats, status (Open / Closed / Upcoming) |
| customers  | id, name, email, phone |
| inquiries  | id, customer_id, type (Service / Program), ref_id, message, status (Open / In Progress / Closed), date |

IDs are generated automatically: S001, P001, C001, Q001 and so on.

## Using the application

1. Pick a module from the main menu (Services, Programs, Customers, Inquiries).
2. Choose an action: list, add, update, delete, search or filter.
3. When updating, press Enter on any field to keep its current value.
4. Use Reports for summaries and exports.
5. Use "Reset to sample data" to restore `seed_data.json` if you want a fresh start.

## Git and GitHub

```
git init
git add .
git commit -m "Veda Technology Business & Service Management System"
git branch -M main
git remote add origin https://github.com/<your-username>/<repository-name>.git
git push -u origin main
```

## Concepts covered

Functions, modules, classes and inheritance, lists, dictionaries, JSON file handling, validation, custom exceptions, searching and filtering, reporting, and unit testing.
