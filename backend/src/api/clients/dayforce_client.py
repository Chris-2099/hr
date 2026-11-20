"""Real Dayforce RESTful Web Services client (per the Dayforce RESTful Web
Services Developer Guide: "Request an Access Token" and "REST Services for
Retrieving Employee Information").

Like jobvite_client.py, this makes genuine HTTP calls but has never been
run against a live Dayforce tenant - no real credentials exist yet. It's
the integration-ready counterpart to the fake data in src/seed/seed_data.py.

Auth: password grant against Dayforce's identity service
(`POST {DAYFORCE_TOKEN_URL}`, form-encoded `grant_type=password` +
`companyId` + `username` + `password` + `client_id`), returning a Bearer
token used on subsequent `/Employees` etc. calls. Confirmed against the
live Dayforce developer-guide doc pages during this build - not guessed.
"""

from __future__ import annotations

import time

import httpx

from src.core.config import settings


class DayforceError(RuntimeError):
    pass


class DayforceClient:
    def __init__(self) -> None:
        self.base_url = settings.DAYFORCE_URL.rstrip("/")
        self.token_url = settings.DAYFORCE_TOKEN_URL
        self.company_id = settings.DAYFORCE_CLIENT_NAMESPACE
        self.username = settings.DAYFORCE_USERNAME
        self.password = settings.DAYFORCE_PASSWORD
        self.client_id = settings.DAYFORCE_CLIENT_ID
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    def _fetch_token(self) -> str:
        data = {
            "grant_type": "password",
            "companyId": self.company_id,
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
        }
        try:
            resp = httpx.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
        except httpx.HTTPError as exc:
            raise DayforceError(f"Dayforce token request failed: {exc}") from exc
        if resp.status_code != 200:
            raise DayforceError(f"Dayforce token request returned HTTP {resp.status_code}: {resp.text[:500]}")
        body = resp.json()
        self._access_token = body["access_token"]
        self._token_expires_at = time.time() + body.get("expires_in", 3600) - 30
        return self._access_token

    def _token(self) -> str:
        if not self._access_token or time.time() >= self._token_expires_at:
            return self._fetch_token()
        return self._access_token

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self._token()}", "Accept": "application/json"}
        try:
            resp = httpx.get(url, params=params or {}, headers=headers, timeout=30)
        except httpx.HTTPError as exc:
            raise DayforceError(f"Dayforce request to {path} failed: {exc}") from exc
        if resp.status_code != 200:
            raise DayforceError(f"Dayforce {path} returned HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    def get_employees(
        self,
        org_unit_xref_code: str | None = None,
        filter_updated_start_date: str | None = None,
        filter_updated_end_date: str | None = None,
    ) -> dict:
        """GET /Employees - returns {"Data": [...]}."""
        params: dict = {}
        if org_unit_xref_code:
            params["OrgUnitXRefCode"] = org_unit_xref_code
        if filter_updated_start_date:
            params["FilterUpdatedStartDate"] = filter_updated_start_date
        if filter_updated_end_date:
            params["FilterUpdatedEndDate"] = filter_updated_end_date
        return self._get("Employees", params)

    def get_work_assignments(self, employee_xref_code: str) -> dict:
        """GET /Employees/{XRefCode}/WorkAssignments - department/position/location/manager."""
        return self._get(f"Employees/{employee_xref_code}/WorkAssignments")

    def get_compensation_summary(self, employee_xref_code: str) -> dict:
        """GET /Employees/{XRefCode}/CompensationSummary."""
        return self._get(f"Employees/{employee_xref_code}/CompensationSummary")

    def get_org_unit_infos(self) -> dict:
        """GET /OrgUnitInfos - department/org-unit hierarchy."""
        return self._get("OrgUnitInfos")

    def get_locations(self) -> dict:
        """GET /Locations."""
        return self._get("Locations")
