from encoding_devops.mcp_instance import mcp


@mcp.prompt("movie-encoding-status")
def movie_encoding_status(job_name: str | None = None) -> str:
    """
    Returns a short overview of encoding jobs and cluster status.
    """
    # If you want to include the optional job_name in the text:
    job_detail = f" for job: {job_name}" if job_name else ""
    return f"""Generating encoding status report{job_detail}:
- Current cluster load
- Active jobs with progress
- Basic movie info for each job
- Estimated completion times
"""
