from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from loguru import logger
from mcp.server.fastmcp import FastMCP

from encoding_devops.client import EncodingClient


@dataclass
class AppContext:
    """Application context with initialized resources"""

    client: EncodingClient


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage server startup and shutdown lifecycle with type-safe context"""
    logger.info("Initializing server lifespan")
    client = EncodingClient()
    try:
        logger.debug("Initializing encoding client session")
        await client.init_session()
        logger.info("Server lifespan initialized successfully")
        yield AppContext(client=client)
    finally:
        logger.debug("Cleaning up server lifespan")
        await client.close_session()
        logger.info("Server lifespan cleanup completed")


mcp = FastMCP(
    "encoding-manager", lifespan=server_lifespan, dependencies=["aiohttp", "python-dotenv", "loguru", "cachetools"]
)
