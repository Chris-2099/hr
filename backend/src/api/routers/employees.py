"""Serves Dayforce-shaped HRIS data (employees, departments) with RBAC
applied: row-level department scoping for hr_business_partner, column-level
compensation hiding for recruiter/viewer."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src import models
from src.api.schemas import DepartmentOut, EmployeeOut
from src.core.database import get_db
from src.core.deps import CurrentUser, department_filter_ids, get_current_user

router = APIRouter(prefix="/api", tags=["employees"])


def _latest_compensation(db: Session, employee_id: str) -> models.Compensation | None:
    return (
        db.query(models.Compensation)
        .filter(models.Compensation.employee_id == employee_id)
        .order_by(models.Compensation.effective_date.desc())
        .first()
    )


def _to_employee_out(employee: models.Employee, comp: models.Compensation | None, can_view_compensation: bool) -> EmployeeOut:
    out = EmployeeOut.model_validate(employee)
    if can_view_compensation and comp:
        out.base_salary = comp.base_salary
        out.compa_ratio = comp.compa_ratio
    return out


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    all_ids = [d.department_id for d in db.query(models.Department.department_id).all()]
    allowed = department_filter_ids(current_user, all_ids)
    departments = db.query(models.Department).filter(models.Department.department_id.in_(allowed)).all()
    return [DepartmentOut.model_validate(d) for d in departments]


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    all_ids = [d.department_id for d in db.query(models.Department.department_id).all()]
    allowed = department_filter_ids(current_user, all_ids)
    employees = db.query(models.Employee).filter(models.Employee.department_id.in_(allowed)).all()
    return [
        _to_employee_out(e, _latest_compensation(db, e.employee_id), current_user.can_view_compensation)
        for e in employees
    ]


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Employee not found")
    all_ids = [d.department_id for d in db.query(models.Department.department_id).all()]
    allowed = department_filter_ids(current_user, all_ids)
    if employee.department_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not permitted to view this employee")
    return _to_employee_out(employee, _latest_compensation(db, employee.employee_id), current_user.can_view_compensation)
