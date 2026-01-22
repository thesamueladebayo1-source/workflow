"""
Entry point for the Workflow backend.

This FastAPI application exposes RESTful endpoints for managing
employees and running payroll. It uses a simple SQLite database via
``sqlite3`` and Pydantic models defined in ``models.py``. On startup the
database is initialized automatically. The API includes endpoints to
create, read, update and terminate employees; preview payroll for a
given month and year; approve payroll runs; and list previous payroll
runs.

To run locally, install FastAPI and Uvicorn (already available in this
environment) and launch with:

```
uvicorn workflow.backend.main:app --reload
```

The API docs will be available at ``/docs``.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import crud, database
from .models import EmployeeCreate, Employee, EmployeeUpdate, PayrollPreview, PayrollItem

# Initialize database tables
database.init_db()

app = FastAPI(title="Workflow Company OS Backend", description="Payroll‑first API for SMEs", version="0.1.0")

# Enable CORS for all origins (for demonstration). In production specify origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/employees", response_model=list[Employee])
def list_employees() -> list[Employee]:
    """Return all employees."""
    rows = crud.get_employees()
    return [Employee(**row) for row in rows]


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int) -> Employee:
    """Return a single employee or 404."""
    row = crud.get_employee(employee_id)
    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Employee(**row)


@app.post("/employees", response_model=Employee, status_code=201)
def create_employee(emp: EmployeeCreate) -> Employee:
    """Create a new employee."""
    emp_id = crud.create_employee(emp)
    row = crud.get_employee(emp_id)
    return Employee(**row)


@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, emp: EmployeeUpdate) -> Employee:
    """Update an existing employee."""
    ok = crud.update_employee(employee_id, emp)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    row = crud.get_employee(employee_id)
    return Employee(**row)


from fastapi import Response

@app.delete("/employees/{employee_id}", status_code=204)
def terminate(employee_id: int) -> Response:
    """Terminate (exit) an employee.

    A 204 No Content response is returned on success.
    """
    ok = crud.terminate_employee(employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found or already exited")
    return Response(status_code=204)


@app.get("/payroll/preview", response_model=PayrollPreview)
def preview_payroll(month: int, year: int) -> PayrollPreview:
    """Preview payroll for the specified month and year."""
    preview = crud.preview_payroll(month, year)
    return preview


@app.post("/payroll/approve", response_model=dict)
def approve_payroll(month: int, year: int) -> dict:
    """Approve and save a payroll run for the specified month and year."""
    preview = crud.preview_payroll(month, year)
    payroll_id = crud.save_payroll(preview)
    return {"payroll_id": payroll_id, "message": "Payroll approved"}


@app.get("/payrolls", response_model=list[dict])
def list_payrolls() -> list[dict]:
    """Return a summary of all payroll runs."""
    rows = crud.get_payrolls()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "month": r["month"],
            "year": r["year"],
            "total_cost": r["total_cost"],
            "approved_at": r["approved_at"],
        })
    return results


@app.get("/payrolls/{payroll_id}", response_model=PayrollPreview)
def get_payroll(payroll_id: int) -> PayrollPreview:
    """Return a detailed payroll run with items."""
    payroll = crud.get_payroll(payroll_id)
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    return payroll
