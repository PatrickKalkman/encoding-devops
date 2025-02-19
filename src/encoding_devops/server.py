from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from loguru import logger
from mcp.server.fastmcp import Context, FastMCP

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


# Create FastMCP server instance with lifespan management
mcp = FastMCP("encoding-manager", lifespan=server_lifespan, dependencies=["aiohttp", "python-dotenv", "loguru", "cachetools"])


@mcp.tool()
async def get_job_by_name(name: str, ctx: Context) -> str:
    """Get details of an encoding job by its name"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    job_data = await app_ctx.client.get_job_by_name(name)
    return str(job_data)


@mcp.tool()
async def get_job_tasks_by_id(job_id: str, ctx: Context) -> str:
    """Get tasks for a specific job by its ID"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    tasks_data = await app_ctx.client.get_job_tasks_by_id(job_id)
    return str(tasks_data)


@mcp.tool()
async def get_clients(ctx: Context) -> str:
    """Get list of all clients"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    clients_data = await app_ctx.client.get_clients()
    return str(clients_data)
