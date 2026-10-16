# DAYFORCE CLIENT TO CALL DAYFORCE API
#
# ** PROVISIONAL / UNVERIFIED - no live Dayforce API or sandbox access yet
# (confirmed with stakeholder 2026-10-16). Built from publicly documented
# integration patterns, not a tenant's actual API Explorer response. Before
# treating this as correct:
#   - Confirm the base URL shape against developers.dayforce.com. Public
#     integration guides agree on roughly https://{host}/Api/{ClientNamespace}/V1
#     - set DAYFORCE_URL to that full prefix (same convention JOBVITE_URL
#     already uses: a complete base, with resource paths appended below).
#   - Confirm the auth scheme. HTTP Basic against a dedicated Web Services
#     user is the long-documented default (matches the existing
#     DAYFORCE_USERNAME/DAYFORCE_PASSWORD settings in core/config.py), but
#     some tenants are configured for OAuth2 client-credentials instead.
#   - Confirm the response envelope and pagination. Every source agrees
#     GET /Employees returns a SHALLOW record per employee (XRefCode plus a
#     handful of fields) and that fields like HireDate/TerminationDate/
#     EmploymentStatus require a second call per XRefCode
#     (GET /Employees/{XRefCode}) - but none of the sources checked confirm
#     the exact JSON wrapper or pagination field names. Verify in the API
#     Explorer (Employee > GET Employees) once access is granted, then update
#     get_employees() accordingly.
import httpx


class DayforceClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        self.base_url = base_url
        self.auth = (username, password)
        self.headers = {
            "Accept": "application/json",
        }

    async def get_employees(self) -> dict:
        """
        Fetch the employee roster (shallow records). UNVERIFIED response
        shape - likely paginated; add paging-follow logic once the real
        envelope is known.
        """
        async with httpx.AsyncClient(auth=self.auth) as client:
            response = await client.get(
                f"{self.base_url}/Employees",
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        return response.json()

    async def get_employee_detail(self, xref_code: str) -> dict:
        """
        Fetch full detail for one employee by XRefCode - needed for fields
        (hire/termination date, employment status) the shallow list omits.
        """
        async with httpx.AsyncClient(auth=self.auth) as client:
            response = await client.get(
                f"{self.base_url}/Employees/{xref_code}",
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        return response.json()
