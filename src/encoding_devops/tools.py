from mcp.server.fastmcp import Context

from encoding_devops.mcp_instance import AppContext, mcp


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
async def get_latest_jobs(ctx: Context, limit: int = 3) -> str:
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
    
    if not jobs_data:
        return "No recent encoding jobs found"
        
    output = [f"Latest {limit} encoding jobs:"]
    for job in jobs_data:
        status = job.get("status", "Unknown")
        name = job.get("name", "Unnamed")
        progress = job.get("progress", 0)
        output.append(f"- {name}: {status} ({progress}% complete)")
    
    return "\n".join(output)


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
        return f"No movie found with IMDB ID: {imdb_id}"

    # Format the movie details in a readable way
    details = [
        f"Title: {movie_data.get('Title', 'N/A')}",
        f"Year: {movie_data.get('Year', 'N/A')}",
        f"Rating: {movie_data.get('imdbRating', 'N/A')}/10",
        f"Runtime: {movie_data.get('Runtime', 'N/A')}",
        f"Genre: {movie_data.get('Genre', 'N/A')}",
        f"Director: {movie_data.get('Director', 'N/A')}",
        f"Actors: {movie_data.get('Actors', 'N/A')}",
        f"Plot: {movie_data.get('Plot', 'N/A')}",
    ]

    return "\n".join(details)
