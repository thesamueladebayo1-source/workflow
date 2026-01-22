# Workflow – Payroll‑First Company OS for SMEs

Workflow is a proof‑of‑concept payroll platform inspired by the need for
lightweight, mobile‑friendly HR and payroll tools built for African
small and medium sized enterprises (SMEs). Rather than competing
head‑on with enterprise suites, Workflow focuses on the core problem
many founders face: running payroll accurately and on time without
consultants or expensive implementations. Research on the African
payroll market shows that the right payroll software automates salary
calculations, handles tax deductions and statutory compliance, and
provides employee self‑service portals【368278679881115†L225-L237】. Leaders like
PaidHR reduce payroll processing time from over a week to just one
day by ensuring clean, compliant data for timely salary payments and
remittances【837604664997935†L182-L190】. Mobile access is critical because
over 600 million Africans subscribe to mobile services and desktop
ownership remains below 15 percent【100352320239419†L20-L32】; mobile‑first
payroll platforms allow workers to register, check earnings and
receive payslips on their phones【100352320239419†L59-L63】.

## Features

* **Employee management (People)** – add, view, update and terminate
  employees. Each employee stores name, role, department, salary,
  bank account details, contract path and status (active, on leave
  or exited). Simple defaults avoid the complexity of enterprise HR
  software. SME payroll tools typically capture employee bio data,
  corporate information, job details and bank information to support
  payroll and compliance【805472718268149†L13-L38】.

* **Payroll preview & approval** – generate a payroll preview for a
  selected month and year. For each active employee the system
  computes gross pay, a simple deduction (10 % for demonstration) and
  net pay, and sums the total cost. After review you can approve and
  persist the payroll run. African payroll platforms stand out
  because they automate statutory calculations and provide mobile
  self‑service【399704601645257†L95-L107】, delivering a stress‑free payroll
  cycle with predictable outputs【399704601645257†L139-L146】.

* **Payroll history** – list previously approved payroll runs and
  inspect their per‑employee breakdowns. A persistent record of
  payroll history is essential for reporting and compliance.

* **API documentation** – built with FastAPI, Workflow auto‑generates
  interactive API documentation at `/docs`.

### Not implemented (future work)

The blueprint for a full company OS includes modules like a founder
dashboard, employee self‑service portal (ESS) and mobile apps. ESS
portals are important because they allow employees to view payslips
and update details themselves, reducing HR workload【368278679881115†L233-L237】.
For the sake of brevity this prototype focuses on the backend API.

## Technology

* **Backend:** FastAPI with Pydantic
  models and SQLite for persistence. FastAPI provides a modern,
  type‑annotated framework with automatic OpenAPI documentation. SQLite
  offers a zero‑configuration relational database suitable for
  prototyping.

* **Database schema:** three tables — `employees`, `payrolls` and
  `payroll_items`. See `backend/database.py` for details. A payroll
  run stores the month, year and total cost, while `payroll_items`
  record per‑employee gross, deductions and net amounts.

* **Project layout:**

      workflow/
        ├── backend/
        │   ├── database.py    # SQLite connection and schema initialization
        │   ├── models.py      # Pydantic models for API requests/responses
        │   ├── crud.py        # Data access functions (employees, payroll)
        │   └── main.py        # FastAPI application with endpoints
        └── README.md          # Project overview (this file)

## Getting started

### Prerequisites

Python 3.10+ is required. FastAPI and uvicorn are already installed in
this environment. No external database server is needed; the app
creates a `workflow.db` SQLite file on first run.

### Running the API

From the repository root (`workflow/`), run the following command:

      uvicorn workflow.backend.main:app --reload

Open your browser to `http://localhost:8000/docs` to explore the
interactive API documentation. Use any REST client to create
employees, preview payroll and approve payroll runs. The database file
will be created automatically.

### Example usage

1. **Create an employee**

   Send a `POST` request to `/employees` with a JSON body:

        {
          "name": "Ada Lovelace",
          "role": "Developer",
          "department": "Engineering",
          "salary": 300000,
          "bank_account": "0123456789",
          "status": "active"
        }

2. **Preview payroll**

   Issue a `GET` request to `/payroll/preview?month=1&year=2026` to see the
   total cost and per‑employee breakdown. Deductions are currently
   calculated as 10 % of gross pay.

3. **Approve payroll**

   If the preview looks correct, call `POST /payroll/approve?month=1&year=2026`.
   This saves the payroll run and returns its ID. You can view all
   payroll runs via `GET /payrolls` and inspect a specific run via
   `GET /payrolls/{id}`.

## Inspiration from research

This prototype draws on insights from HR and payroll platforms
operating in Africa. Key takeaways include the importance of payroll
automation and statutory compliance【368278679881115†L225-L233】, the need for
employee self‑service portals to reduce HR workload【368278679881115†L233-L237】,
mobile‑first access due to high mobile penetration【100352320239419†L20-L33】, and
the advantages of reducing payroll processing time to improve employee
morale【837604664997935†L182-L193】. By focusing on these principles,
Workflow aims to offer SMEs peace of mind on payroll day.
