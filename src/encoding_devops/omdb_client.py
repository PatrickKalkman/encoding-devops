import os
from typing import Optional

import aiohttp
from cachetools import TTLCache, cached
from loguru import logger


class OMDBClient:
    """Client for interacting with the OMDB API"""

    def __init__(self):
        self.api_url = "http://www.omdbapi.com"
        self.api_key = os.getenv("OMDB_API_KEY")
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

    # Create a TTL cache for movie searches
    _movie_cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour

    @cached(_movie_cache)
    async def search_movie(self, title: str) -> dict:
        """Search for a movie by title"""
        if not self.session:
            await self.init_session()

        try:
            async with self.session.get(
                "/", params={"apikey": self.api_key, "t": title}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("Response") == "False":
                    logger.warning(f"Movie not found: {title}")
                    return {}
                logger.info(f"Successfully retrieved data for movie: {title}")
                return data

        except Exception as e:
            logger.error(f"Error searching for movie {title}: {e}")
            raise

    async def get_movie_rating(self, title: str) -> float:
        """Get IMDB rating for a movie"""
        movie_data = await self.search_movie(title)
        try:
            return float(movie_data.get("imdbRating", 0))
        except (ValueError, TypeError):
            logger.warning(f"Invalid rating for movie {title}")
            return 0.0
