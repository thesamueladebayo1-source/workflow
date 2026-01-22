"""
CRUD (Create, Read, Update, Delete) utilities for Workflow backend.

These functions encapsulate database operations for employees and payroll
runs using the ``sqlite3`` module. Separating database logic from the
FastAPI routes keeps the application organized and easier to test.
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from .database import get_db
from .models import EmployeeCreate, EmployeeUpdate, PayrollItem, PayrollPreview


def get_employees() -> List[sqlite3.Row]:
    """Return a list of all employees."""
    conn = get_db()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()
    return employees


def get_employee(employee_id: int) -> Optional[sqlite3.Row]:
    """Return an employee by id or None if not found."""
    conn = get_db()
    emp = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    return emp


def create_employee(emp: EmployeeCreate) -> int:
    """Insert a new employee and return the new id."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO employees (name, role, department, salary, bank_account, status, contract_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (emp.name, emp.role, emp.department, emp.salary, emp.bank_account, emp.status, emp.contract_path),
    )
    emp_id = cur.lastrowid
    conn.commit()
    conn.close()
    return emp_id


def update_employee(employee_id: int, emp: EmployeeUpdate) -> bool:
    """Update fields of an employee. Returns True if updated."""
    current = get_employee(employee_id)
    if not current:
        return False
    # Merge existing values with updates
    data = {k: current[k] for k in current.keys()}
    # Only update provided fields
    for field, value in emp.dict(exclude_unset=True).items():
        data[field] = value
    conn = get_db()
    conn.execute(
        """
        UPDATE employees
        SET name = ?, role = ?, department = ?, salary = ?, bank_account = ?, status = ?, contract_path = ?
        WHERE id = ?
        """,
        (
            data["name"],
            data.get("role"),
            data.get("department"),
            data["salary"],
            data.get("bank_account"),
            data["status"],
            data.get("contract_path"),
            employee_id,
        ),
    )
    conn.commit()
    conn.close()
    return True


def terminate_employee(employee_id: int) -> bool:
    """Mark an employee as exited. Returns True if updated."""
    conn = get_db()
    cur = conn.execute(
        "UPDATE employees SET status = 'exited' WHERE id = ? AND status != 'exited'",
        (employee_id,),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def _calculate_pay(employee: sqlite3.Row) -> PayrollItem:
    """Helper to compute payroll values for an employee.

    For demonstration, deductions are a simple percentage (10%) of the gross
    salary. In a production system this function would include more
    sophisticated tax calculations, pension contributions, bonuses and
    arbitrary deductions/allowances.
    """
    gross = float(employee["salary"])
    deductions = gross * 0.10  # 10% deduction as placeholder
    net = gross - deductions
    return PayrollItem(
        employee_id=employee["id"],
        name=employee["name"],
        gross=gross,
        deductions=deductions,
        net=net,
    )


def preview_payroll(month: int, year: int) -> PayrollPreview:
    """Generate a payroll preview for all active employees.

    Returns a ``PayrollPreview`` with per‑employee items and total cost.
    """
    conn = get_db()
    employees = conn.execute(
        "SELECT * FROM employees WHERE status = 'active'"
    ).fetchall()
    conn.close()
    items: List[PayrollItem] = []
    total_cost = 0.0
    for emp in employees:
        item = _calculate_pay(emp)
        items.append(item)
        total_cost += item.net
    return PayrollPreview(month=month, year=year, total_cost=total_cost, items=items)


def save_payroll(preview: PayrollPreview) -> int:
    """Persist a payroll run to the database and return its id."""
    conn = get_db()
    cur = conn.cursor()
    # Insert into payrolls
    cur.execute(
        "INSERT INTO payrolls (month, year, total_cost) VALUES (?, ?, ?)",
        (preview.month, preview.year, preview.total_cost),
    )
    payroll_id = cur.lastrowid
    # Insert each payroll item
    for item in preview.items:
        cur.execute(
            """
            INSERT INTO payroll_items (payroll_id, employee_id, gross, deductions, net)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payroll_id, item.employee_id, item.gross, item.deductions, item.net),
        )
    conn.commit()
    conn.close()
    return payroll_id


def get_payrolls() -> List[sqlite3.Row]:
    """Return a list of all payroll runs."""
    conn = get_db()
    payrolls = conn.execute(
        "SELECT * FROM payrolls ORDER BY year DESC, month DESC"
    ).fetchall()
    conn.close()
    return payrolls


def get_payroll(payroll_id: int) -> Optional[PayrollPreview]:
    """Return a payroll run with its items or None if not found."""
    conn = get_db()
    payroll = conn.execute(
        "SELECT * FROM payrolls WHERE id = ?",
        (payroll_id,),
    ).fetchone()
    if not payroll:
        conn.close()
        return None
    items_rows = conn.execute(
        """
        SELECT pi.*, e.name
        FROM payroll_items pi
        JOIN employees e ON e.id = pi.employee_id
        WHERE pi.payroll_id = ?
        """,
        (payroll_id,),
    ).fetchall()
    conn.close()
    items: List[PayrollItem] = []
    for row in items_rows:
        items.append(
            PayrollItem(
                employee_id=row["employee_id"],
                name=row["name"],
                gross=row["gross"],
                deductions=row["deductions"],
                net=row["net"],
            )
        )
    return PayrollPreview(
        month=payroll["month"],
        year=payroll["year"],
        total_cost=payroll["total_cost"],
        items=items,
    )
