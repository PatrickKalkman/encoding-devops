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
    async def search_movie(self, title: str, page: int = 1, type_filter: str = "movie") -> dict:
        """
        Search for movies by title

        Args:
            title: Movie title to search for
            page: Page number (1-100)
            type_filter: Type of result (movie, series, episode)

        Returns:
            Dict containing search results
        """
        if not self.session:
            await self.init_session()

        try:
            params = {"apikey": self.api_key, "s": title, "type": type_filter, "page": str(page), "r": "json"}

            async with self.session.get("/", params=params) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("Response") == "False":
                    logger.warning(f"No results found for: {title}")
                    return {"Search": []}
                logger.info(f"Found {data.get('totalResults', 0)} results for: {title}")
                return data

        except Exception as e:
            logger.error(f"Error searching for movie {title}: {e}")
            raise

    async def get_movie_details(self, imdb_id: str) -> dict:
        """Get detailed movie information by IMDB ID"""
        if not self.session:
            await self.init_session()

        try:
            async with self.session.get("/", params={"apikey": self.api_key, "i": imdb_id}) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("Response") == "False":
                    logger.warning(f"Movie not found with ID: {imdb_id}")
                    return {}
                return data
        except Exception as e:
            logger.error(f"Error getting movie details for ID {imdb_id}: {e}")
            raise

    async def get_movie_rating(self, title: str) -> float:
        """Get IMDB rating for a movie"""
        search_results = await self.search_movie(title)
        if not search_results.get("Search"):
            return 0.0

        # Get the first movie's details
        first_movie = search_results["Search"][0]
        movie_data = await self.get_movie_details(first_movie["imdbID"])

        try:
            return float(movie_data.get("imdbRating", 0))
        except (ValueError, TypeError):
            logger.warning(f"Invalid rating for movie {title}")
            return 0.0
