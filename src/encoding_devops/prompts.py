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
- Last 3 jobs with progress
- Basic movie info for each job
- Estimated completion times
"""


@mcp.prompt("draft-email-failed-encoding-job")
def email_failed_encoding_job(job_name: str | None = None, client_name: str | None = None) -> str:
    """
    Returns a draft email to inform a client of a failed encoding job.
    """
    return ""
