"""
Database module for Workflow backend.

This module manages a SQLite database connection and sets up tables for
employees, payroll runs, and per‑employee payroll line items. It uses
Python's built‑in ``sqlite3`` module to avoid external dependencies.

Functions are provided to obtain a database connection and initialize
tables on startup. The tables created include:

* ``employees`` – stores basic employee information such as name,
  role, department, salary, bank account details, employment status and
  contract document path. Status can be ``active``, ``on_leave`` or
  ``exited``.
* ``payrolls`` – stores summary information about each payroll run,
  including a generated primary key, month and year, total cost and
  timestamp of approval.
* ``payroll_items`` – stores per‑employee details for each payroll run,
  including gross salary, deductions and net pay. A foreign key to
  ``payrolls`` associates the items with a payroll run, while a foreign
  key to ``employees`` associates the items with an employee.

``get_db()`` returns a connection with row factory configured to
`sqlite3.Row` for dict‑like access. ``init_db()`` initializes the schema.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "workflow.db"


def get_db() -> sqlite3.Connection:
    """Return a SQLite database connection.

    The connection uses ``sqlite3.Row`` as row factory to support
    dict‑like access (e.g. row["name"]). Connections returned by
    ``sqlite3.connect`` are not thread‑safe by default, but FastAPI's
    default ``uvicorn`` server runs each request in its own thread.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables if they don't already exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Create employees table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            department TEXT,
            salary REAL NOT NULL,
            bank_account TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            contract_path TEXT
        );
        """
    )

    # Create payrolls table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payrolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Create payroll_items table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_id INTEGER NOT NULL REFERENCES payrolls(id) ON DELETE CASCADE,
            employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
            gross REAL NOT NULL,
            deductions REAL NOT NULL,
            net REAL NOT NULL
        );
        """
    )

    conn.commit()
    conn.close()
