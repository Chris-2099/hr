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

UNRESOLVED (flagged during a later doc re-check): the full 225-page
Jobvite API v2 PDF describes query-string creds (`?api=&sc=`) or an
HMAC-signed header scheme (`X-JVI-API` + `X-JVI-SIGN` + `X-JVI-EPOCH`) -
not two plain-text headers. This file's `04122025.pdf` source may be a
newer revision that simplified this (a gated Jobvite help-center article
hints at a "post-April-2024 header-based scheme" using these exact
literal header names, but it couldn't be fetched to confirm). Don't change
this without a real credential to test against - getting it wrong either
way is silent until a real call is made.
"""

from __future__ import annotations

from typing import Any

import httpx

from src.core.config import settings


class JobviteError(RuntimeError):
    pass


class JobviteClient:
    def __init__(self) -> None:
        self.base_url = settings.JOBVITE_URL.rstrip("/")
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
        """ GET /job - requisitions """
        params: dict = {"start": start, "count": count}
        if job_state:
            params["jobStatus"] = job_state
        return self._get("job", params)

    def get_candidates(
        self,
        start: int = 1,
        count: int = 100,
        wflowstate: str | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
    ) -> dict:
        """ GET /candidate - candidates + their nested application/job data """
        params: dict = {"start": start, "count": count}
        if wflowstate:
            params["wflowstate"] = wflowstate
        if date_start:
            params["datestart"] = date_start
        if date_end:
            params["dateend"] = date_end
        return self._get("candidate", params)

    def get_interviews(
        self,
        eid: str | None = None,
        application_id: str | None = None,
        workflow_state_id: str | None = None,
    ) -> dict:
        """ GET /interview - interview blocks for an application/workflow state """
        params: dict = {}
        if eid:
            params["eId"] = eid
        if application_id:
            params["applicationId"] = application_id
        if workflow_state_id:
            params["workflowStateId"] = workflow_state_id
        return self._get("interview", params)

    def get_departments(self, start: int = 1, count: int = 500) -> dict:
        """ GET /department - the department taxonomy """
        return self._get("department", {"start": start, "count": count})

    def get_offerLetterCompletedList(
        self, 
        date_start: str,
        date_end: str, 
    ) -> dict[str, Any]:
        """ GET /offerLetterCompletedList """ 
        return self._get("offerLetterCompletedList", params={
                "offerLetterCompletedList":"ESIGNATURE",
                "datestart": date_start,
                "dateend": date_end,
            }
    )
