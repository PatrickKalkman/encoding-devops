import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class EncodingClient:
    """Client for interacting with the encoding API"""

    def __init__(self):
        self.api_url = os.getenv("ENCODING_API_URL")
        self.client_id = os.getenv("ENCODING_CLIENT_ID")
        self.client_secret = os.getenv("ENCODING_CLIENT_SECRET")
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(base_url=self.api_url)

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def ensure_token(self):
        """Ensure we have a valid access token"""
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            await self.refresh_token()

    async def refresh_token(self):
        """Get new access token"""
        if not self.session:
            await self.init_session()

        try:
            async with self.session.post(
                "/auth/token", json={"client_id": self.client_id, "client_secret": self.client_secret}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self.token = data["access_token"]
                # Set token expiry (subtract 5 minutes as buffer)
                self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"] - 300)
                logger.debug("Successfully refreshed access token")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    async def get_jobs(self, status: Optional[str] = None) -> list[dict]:
        """Get list of encoding jobs"""
        await self.ensure_token()
        params = {"status": status} if status else {}

        async with self.session.get(
            "/jobs", params=params, headers={"Authorization": f"Bearer {self.token}"}
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_job(self, job_id: str) -> dict:
        """Get specific job details"""
        await self.ensure_token()

        async with self.session.get(f"/jobs/{job_id}", headers={"Authorization": f"Bearer {self.token}"}) as response:
            response.raise_for_status()
            return await response.json()
