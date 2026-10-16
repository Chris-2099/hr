# JOBVITE CLIENT TO CALL JOBVITE API
import httpx

class JobviteClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_secret: str,
    ) -> None:
        self.base_url = base_url
        self.headers = {
            "x-jvi-api": api_key,
            "x-jvi-sc": api_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def get_jobs(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/job",
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        return response.json()

    async def get_candidates(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/candidate", # also returns application data
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        return response.json()

    async def get_workflows(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/workflow",
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        return response.json()

    async def get_departments(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/department",
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        return response.json()