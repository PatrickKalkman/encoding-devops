from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server.fastmcp import Context, FastMCP

from encoding_devops.client import EncodingClient


@dataclass
class AppContext:
    """Application context with initialized resources"""
    client: EncodingClient


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage server startup and shutdown lifecycle with type-safe context"""
    client = EncodingClient()
    try:
        await client.init_session()
        yield AppContext(client=client)
    finally:
        await client.close_session()


# Create FastMCP server instance with lifespan management
mcp = FastMCP("encoding-manager", lifespan=server_lifespan, dependencies=["aiohttp", "python-dotenv"])


@mcp.tool()
async def get_job_by_name(name: str, ctx: Context) -> str:
    """Get details of an encoding job by its name"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    job_data = await app_ctx.client.get_job(name)
    return str(job_data)
