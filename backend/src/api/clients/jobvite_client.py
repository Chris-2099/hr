"""Real Jobvite API v2 client (per Jobvite-API-v2 04122025.pdf).

This makes genuine HTTP calls - it is **not** wired into the dashboards
(those still read seeded fake data) and has never been run against a live
Jobvite tenant, since no real credentials exist yet. It exists so that once
real credentials land in `.env`, flipping them in and calling a sync route
(see app/routers/integrations.py) is the only remaining step - no client
code to write from scratch.

Auth: Jobvite supports two header-based schemes (see the API doc's
"Encoded Headers" section); this uses the simpler "Header without
Encryption" variant (`x-jvi-api` / `x-jvi-sc`, both plain text). The
HMAC-SHA256 "Header with Encryption" variant is documented there too if a
customer's Jobvite configuration requires it instead - swap `_auth_headers`
for that signing scheme if so.
"""

from __future__ import annotations

import httpx

from src.core.config import settings


class JobviteError(RuntimeError):
    pass


class JobviteClient:
    def __init__(self) -> None:
        self.base_url = (settings.JOBVITE_URL or "https://api.jobvite.com/api/v2").rstrip("/")
        self.api_key = settings.JOBVITE_API_KEY
        self.api_secret = settings.JOBVITE_API_SECRET

    def _auth_headers(self) -> dict[str, str]:
        return {
            "x-jvi-api": self.api_key,
            "x-jvi-sc": self.api_secret,
            "Accept": "application/json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = httpx.get(url, params={"format": "json", **(params or {})}, headers=self._auth_headers(), timeout=30)
        except httpx.HTTPError as exc:
            raise JobviteError(f"Jobvite request to {path} failed: {exc}") from exc
        if resp.status_code != 200:
            raise JobviteError(f"Jobvite {path} returned HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()

    def get_requisitions(self, start: int = 1, count: int = 100, job_state: str | None = None) -> dict:
        """GET /job - requisitions. `job_state` maps to Jobvite's `status` filter param."""
        params: dict = {"start": start, "count": count}
        if job_state:
            params["status"] = job_state
        return self._get("job", params)

    def get_candidates(
        self,
        start: int = 1,
        count: int = 100,
        wflowstate: str | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
    ) -> dict:
        """GET /candidate - candidates + their nested application/job data."""
        params: dict = {"start": start, "count": count}
        if wflowstate:
            params["wflowstate"] = wflowstate
        if date_start:
            params["datestart"] = date_start
        if date_end:
            params["dateend"] = date_end
        return self._get("candidate", params)

    def get_interviews(self, application_id: str | None = None, workflow_state_id: str | None = None) -> dict:
        """GET /interview - interview blocks for an application/workflow state."""
        params: dict = {}
        if application_id:
            params["applicationId"] = application_id
        if workflow_state_id:
            params["workflowStateId"] = workflow_state_id
        return self._get("interview", params)
