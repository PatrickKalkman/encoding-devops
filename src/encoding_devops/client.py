import os
from datetime import datetime
from typing import Optional

import aiohttp
import jwt
from loguru import logger


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
                "auth/authenticate", json={"email": self.client_id, "password": self.client_secret}
            ) as response:
                logger.debug(f"Refreshing access token: {response.status}")
                logger.debug(f"Response: {await response.text()}")
                response.raise_for_status()
                logger.info("Successfully authenticated with encoding API")
                data = await response.json()
                self.token = data["token"]
                # Decode JWT token to extract expiration time
                decoded_token = jwt.decode(self.token, options={"verify_signature": False})
                self.token_expiry = datetime.fromtimestamp(decoded_token["exp"])

                logger.debug(f"Token expires at: {self.token_expiry}")
                logger.debug("Successfully refreshed access token")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    async def get_job(self, name: str) -> dict:
        """Get list of encoding jobs"""
        await self.ensure_token()
        params = {"name": name}

        async with self.session.get(
            "/jobs/name/", params=params, headers={"Authorization": f"Bearer {self.token}"}
        ) as response:
            response.raise_for_status()
            return await response.json()
