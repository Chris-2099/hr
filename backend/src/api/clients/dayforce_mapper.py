"""Maps raw Dayforce JSON into flat dicts matching our column names.

Unlike jobvite_mapper.py, this one is only *partially* confirmed. The
Employee base-object field names below (XRefCode, FirstName, LastName,
BirthDate, Gender, HireDate) were read directly off the live
"REST Services for Retrieving Employee Information" doc page during this
build. Department/position/location/manager/employment-status/termination-
date are NOT on that base object - Dayforce's own doc page explicitly
states it documents the WorkAssignments/EmploymentStatuses subordinate
resources only as named endpoints, without listing their field shapes.

`map_work_assignment`/`map_compensation` below were updated against a
third-party API connector's documented schema for these two resources
(not Dayforce's own primary docs, which don't expose their shape to a
non-tenant reader) - stronger than a cold guess, but still UNVERIFIED
against a real tenant response. See each function's docstring for what
that source does and doesn't confirm.
"""

from __future__ import annotations

import datetime as dt


def _parse_date(value) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def map_employee(raw: dict) -> dict:
    """GET /Employees response item -> Employee base fields (confirmed shape)."""
    return {
        "dayforce_employee_id": raw.get("XRefCode"),
        "first_name": raw.get("FirstName"),
        "last_name": raw.get("LastName"),
        "birth_date": _parse_date(raw.get("BirthDate")),
        "gender": raw.get("Gender") or "Decline to Self Identify",
        "hire_date": _parse_date(raw.get("HireDate") or raw.get("OriginalHireDate")),
    }


def map_work_assignment(raw: dict) -> dict:
    """GET /Employees/{XRefCode}/WorkAssignments response item -> org
    placement fields. UNVERIFIED against a real tenant response, but the
    nested shape here (department/position/job under a `Position` object,
    location under a `Location` object) matches a third-party connector's
    documented schema for this resource - confirm before relying on it in
    a real sync. That same source does NOT show `ManagerXRefCode` or
    `EmploymentStatusXRefCode` anywhere on this resource at all - manager
    may live on a separate "Employee Managers" endpoint, and employment
    status may not be here either; both are kept below as best-effort
    fallback reads, not confirmed fields."""
    position = raw.get("Position") or {}
    department = position.get("Department") or {}
    job = position.get("Job") or {}
    location = raw.get("Location") or {}
    return {
        "department_xref_code": department.get("XRefCode") or raw.get("OrgUnitXRefCode") or raw.get("DepartmentXRefCode"),
        "position_xref_code": position.get("XRefCode") or raw.get("PositionXRefCode"),
        "job_xref_code": job.get("XRefCode") or raw.get("JobXRefCode"),
        "location_xref_code": location.get("XRefCode") or raw.get("LocationXRefCode"),
        # Unconfirmed on this resource at all - see docstring above.
        "manager_dayforce_employee_id": raw.get("ManagerXRefCode"),
        "employment_status": raw.get("EmploymentStatusXRefCode"),
        "effective_start": _parse_date(raw.get("EffectiveStart") or raw.get("StartDate")),
    }


def map_compensation(raw: dict) -> dict:
    """GET /Employees/{XRefCode}/CompensationSummary. UNVERIFIED against a
    real tenant response, but field names below match a third-party
    connector's documented schema for this resource. That source does NOT
    show `CurrencyCode` or `AnnualSalary` anywhere on it - kept as
    fallbacks, not confirmed fields. The same source documents several
    real fields we don't map yet (PayGrade, PayType, CompRatio,
    MinimumRate/MaximumRate) - add them here once a real tenant response
    confirms this shape."""
    return {
        "base_salary": raw.get("BaseRate") or raw.get("BaseSalary") or raw.get("AnnualSalary"),
        "currency": raw.get("CurrencyCode") or "USD",
        "effective_date": _parse_date(raw.get("EffectiveStart") or raw.get("EffectiveDate")),
    }
