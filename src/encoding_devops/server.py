from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from loguru import logger
from mcp.server.fastmcp import FastMCP

from encoding_devops.encoding_client import EncodingClient
from encoding_devops.omdb_client import OMDBClient

__all__ = ["mcp"]

# Create MCP instance first so tools can use it

# Import tools after mcp is created
from encoding_devops import tools  # noqa


@dataclass
class AppContext:
    """Application context with initialized resources"""

    client: EncodingClient
    omdb_client: OMDBClient


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage server startup and shutdown lifecycle with type-safe context"""
    logger.info("Initializing server lifespan")
    client = EncodingClient()
    omdb_client = OMDBClient()
    try:
        logger.debug("Initializing client sessions")
        await client.init_session()
        await omdb_client.init_session()
        logger.info("Server lifespan initialized successfully")
        yield AppContext(client=client, omdb_client=omdb_client)
    finally:
        logger.debug("Cleaning up server lifespan")
        await client.close_session()
        await omdb_client.close_session()
        logger.info("Server lifespan cleanup completed")


mcp = FastMCP(
    "encoding-manager", lifespan=server_lifespan, dependencies=["aiohttp", "python-dotenv", "loguru", "cachetools"]
)
