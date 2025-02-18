from loguru import logger
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import Context, FastMCP

from encoding_devops.client import EncodingClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage server startup and shutdown lifecycle."""
    client = EncodingClient()
    try:
        await client.init_session()
        yield {"client": client}
    finally:
        await client.close_session()


# Create FastMCP server instance with lifespan management
mcp = FastMCP("encoding-manager", lifespan=server_lifespan, dependencies=["aiohttp", "python-dotenv"])


# For tools, we can use additional parameters like context
@mcp.tool()
async def get_job_by_name(name: str, ctx: Context) -> str:
    """Get details of an encoding job by its name"""
    client = EncodingClient()
    job_data = await client.get_job(name)
    return str(job_data)
