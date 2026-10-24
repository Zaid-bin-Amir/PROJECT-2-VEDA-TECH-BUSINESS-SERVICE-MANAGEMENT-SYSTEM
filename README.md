# Veda Technology Business & Service Management System

A menu-driven Python application that models the day-to-day operations of a technology and digital-services company: services, training and internship programs, customers, and customer inquiries / service requests.

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
