"""Maps raw Dayforce JSON into flat dicts matching our column names.

Unlike jobvite_mapper.py, this one is only *partially* confirmed. The
Employee base-object field names below (XRefCode, FirstName, LastName,
BirthDate, Gender, HireDate) were read directly off the live
"REST Services for Retrieving Employee Information" doc page during this
build. Department/position/location/manager/employment-status/termination-
date are NOT on that base object - Dayforce's own doc page explicitly
states it documents the WorkAssignments/EmploymentStatuses subordinate
resources only as named endpoints, without listing their field shapes.
So `map_work_assignment` below is a best-guess based on Dayforce's general
naming convention (XRefCode-suffixed fields), not a confirmed mapping - it
must be validated against one real tenant's response before being trusted.
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
    placement fields. UNVERIFIED field names - confirm against a real
    tenant response (Dayforce's doc page did not enumerate these) before
    relying on this in a real sync."""
    return {
        "department_xref_code": raw.get("OrgUnitXRefCode") or raw.get("DepartmentXRefCode"),
        "position_xref_code": raw.get("JobXRefCode") or raw.get("PositionXRefCode"),
        "location_xref_code": raw.get("LocationXRefCode"),
        "manager_dayforce_employee_id": raw.get("ManagerXRefCode"),
        "employment_status": raw.get("EmploymentStatusXRefCode"),
        "effective_start": _parse_date(raw.get("EffectiveStart") or raw.get("StartDate")),
    }


def map_compensation(raw: dict) -> dict:
    """GET /Employees/{XRefCode}/CompensationSummary. UNVERIFIED field
    names - same caveat as map_work_assignment."""
    return {
        "base_salary": raw.get("BaseRate") or raw.get("AnnualSalary"),
        "currency": raw.get("CurrencyCode") or "USD",
        "effective_date": _parse_date(raw.get("EffectiveDate")),
    }
