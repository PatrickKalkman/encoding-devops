import webbrowser
from urllib.parse import quote

from mcp.server.fastmcp import Context

from encoding_devops.mcp_instance import AppContext, mcp


@mcp.tool()
async def get_job_by_name(name: str, ctx: Context) -> str:
    """Get details of an encoding job by its name"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    job_data = await app_ctx.client.get_job_by_name(name)
    return job_data


@mcp.tool()
async def get_job_tasks_by_id(job_id: str, ctx: Context) -> str:
    """Get tasks for a specific job by its ID"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    tasks_data = await app_ctx.client.get_job_tasks_by_id(job_id)
    return tasks_data


@mcp.tool()
async def get_clients(ctx: Context) -> str:
    """Get list of all clients"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    clients_data = await app_ctx.client.get_clients()
    return clients_data


@mcp.tool()
async def is_cluster_busy(ctx: Context) -> str:
    """Check if the encoding cluster is busy (has jobs in progress)"""
    app_ctx: AppContext = ctx.request_context.lifespan_context
    jobs_count = await app_ctx.client.get_inprogress_jobs_count()
    is_busy = jobs_count > 0
    return {"is_busy": is_busy, "jobs_count": jobs_count, "status": "busy" if is_busy else "not busy"}


@mcp.tool()
async def get_latest_jobs(limit: int, ctx: Context) -> str:
    """
    Get the most recent encoding jobs

    Args:
        limit: Number of jobs to return (default: 3, max: 10)

    Returns:
        String representation of the latest jobs
    """
    if not 1 <= limit <= 10:
        return "Error: Limit must be between 1 and 10 jobs"

    app_ctx: AppContext = ctx.request_context.lifespan_context
    jobs_data = await app_ctx.client.get_latest_jobs(limit)

    return {"count": len(jobs_data) if jobs_data else 0, "limit": limit, "jobs": jobs_data if jobs_data else []}


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

    return {"query": title, "total_results": int(results.get("totalResults", 0)), "movies": results.get("Search", [])}


@mcp.tool()
async def get_movie_details(imdb_id: str, ctx: Context) -> str:
    """
    Get detailed information about a movie by its IMDB ID

    Args:
        imdb_id: IMDB ID of the movie (e.g., 'tt0111161')

    Returns:
        String representation of the movie details
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    movie_data = await app_ctx.omdb_client.get_movie_details(imdb_id)

    if not movie_data:
        return {"error": f"No movie found with IMDB ID: {imdb_id}"}

    return movie_data


@mcp.tool()
async def open_email(
    body: str, to: str = "", subject: str = "", cc: str = "", bcc: str = "", ctx: Context = None
) -> str:
    """
    Opens the default email client with your message ready to go

    Args:
        body: What you want to say in the email
        to: Who to send it to (optional)
        subject: Email subject line (optional)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        ctx: MCP context

    Returns:
        str: Quick status message so you know it worked
    """
    # URL encode everything (handles special characters and spaces)
    params = []

    # Start with the body since it's required
    params.append(f"body={quote(body)}")

    # Add any optional fields that were provided
    if subject:
        params.append(f"subject={quote(subject)}")
    if cc:
        params.append(f"cc={quote(cc)}")
    if bcc:
        params.append(f"bcc={quote(bcc)}")

    # Build the mailto URL - if we have a recipient, include it in the base URL
    mailto_base = f"mailto:{quote(to)}?" if to else "mailto:?"
    mailto_url = mailto_base + "&".join(params)

    # Fire up the email client
    webbrowser.open(mailto_url, new=1)

    return "Ready to go! Your email client should be open with the template loaded."
