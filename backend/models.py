"""
Pydantic models and utility functions for the Workflow backend.

This module defines Pydantic schemas used by the FastAPI endpoints for
validating and serializing request and response bodies. Using Pydantic
ensures type safety and auto‑generates API documentation when running
with FastAPI.

Models defined here:

* ``EmployeeBase`` – base fields shared by create and update operations.
* ``EmployeeCreate`` – fields required to create a new employee.
* ``EmployeeUpdate`` – optional fields for updating an employee.
* ``Employee`` – returned from API with an ``id``.
* ``PayrollItem`` – per employee payroll line item.
* ``PayrollPreview`` – preview response summarizing total cost and items.
* ``Payroll`` – stored payroll run with id, period and summary.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class EmployeeBase(BaseModel):
    """Shared properties for employee operations."""

    name: str = Field(..., description="Full name of the employee")
    role: Optional[str] = Field(None, description="Job role or title")
    department: Optional[str] = Field(None, description="Department name")
    salary: float = Field(..., ge=0.0, description="Monthly gross salary")
    bank_account: Optional[str] = Field(None, description="Bank account details")
    status: Optional[str] = Field(
        "active",
        description="Employment status: active, on_leave or exited",
    )
    contract_path: Optional[str] = Field(
        None, description="Path to stored contract or documents"
    )


class EmployeeCreate(EmployeeBase):
    """Properties required to create an employee."""
    pass


class EmployeeUpdate(BaseModel):
    """Properties allowed to update an employee."""
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0.0)
    bank_account: Optional[str] = None
    status: Optional[str] = None
    contract_path: Optional[str] = None


class Employee(EmployeeBase):
    """Representation of an employee returned by the API."""
    id: int

    class Config:
        # allow constructing from objects/dicts
        from_attributes = True


class PayrollItem(BaseModel):
    """Line item for an employee in a payroll preview or run."""
    employee_id: int
    name: str
    gross: float
    deductions: float
    net: float


class PayrollPreview(BaseModel):
    """Response for a payroll preview."""
    month: int
    year: int
    total_cost: float
    items: List[PayrollItem]


class Payroll(BaseModel):
    """Representation of a stored payroll run."""
    id: int
    month: int
    year: int
    total_cost: float
    approved_at: datetime
    items: List[PayrollItem]
