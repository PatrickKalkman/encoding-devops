from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from loguru import logger
from mcp.server.fastmcp import Context, FastMCP

from encoding_devops.encoding_client import EncodingClient
from encoding_devops.omdb_client import OMDBClient


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


@mcp.tool()
async def is_cluster_busy(ctx: Context) -> str:
    """Check if the encoding cluster is busy (has jobs in progress)"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    jobs_count = await app_ctx.client.get_inprogress_jobs_count()
    is_busy = jobs_count > 0
    return f"Cluster is {'busy' if is_busy else 'not busy'} with {jobs_count} jobs in progress"


@mcp.tool()
async def search_movie(title: str, ctx: Context) -> str:
    """
    Search for a movie by title

    Args:
        title: Movie title to search for

    Returns:
        String representation of the search results
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    results = await app_ctx.omdb_client.search_movie(title)

    if not results.get("Search"):
        return f"No movies found matching '{title}'"

    movies = results["Search"]
    total = results.get("totalResults", len(movies))

    output = [f"Found {total} results for '{title}':"]
    for movie in movies:
        output.append(f"- {movie['Title']} ({movie['Year']}) - Type: {movie['Type']} - IMDB: {movie['imdbID']}")

    return "\n".join(output)
