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
    if not job_name or not client_name:
        return "Error: Both job_name and client_name are required to generate the email."

    return f"""Subject: Encoding Job Status Update - {job_name}

Dear {client_name},

I hope this email finds you well. I am writing to inform you about an
issue we've encountered with your encoding job "{job_name}".

Unfortunately, the encoding process has failed to complete successfully. Our technical team has been
 automatically notified and is currently investigating the cause of the failure.

We understand the importance of your project and are treating this with high priority.
We will provide you with more detailed information about the cause and our
resolution plan as soon as we have completed our initial investigation.

Next steps:
1. Our team is analyzing the failure logs
2. We will identify the root cause
3. We will propose a solution and estimated timeline
4. We will keep you updated on our progress

If you have any immediate questions or concerns, please don't hesitate to reach out.

We apologize for any inconvenience this may cause and appreciate your understanding.

Best regards,
Your Encoding Team
AION Media"""


@mcp.prompt("draft-email-redeliver-encoding-job")
def email_redeliver_encoding_job(job_name: str | None = None, client_name: str | None = None) -> str:
    """
    Returns a draft email to request content redelivery for an encoding job.
    """
    if not job_name or not client_name:
        return "Error: Both job_name and client_name are required to generate the email."

    return f"""Subject: Content Redelivery Request - {job_name}

Dear {client_name},

I hope this email finds you well. I am writing regarding your encoding job "{job_name}".

We have encountered some issues with the source content for this job and need to request a redelivery
of the original materials. This will help ensure we can process your encoding job successfully.

Action Required:
1. Please reupload the original source content for "{job_name}"
2. Ensure all files are complete and uncorrupted
3. Use our secure file transfer system for the delivery
4. Notify us once the upload is complete

If you need access to our file transfer system or have any questions about the redelivery process,
please let us know and we'll provide immediate assistance.

We appreciate your prompt attention to this matter and apologize for any inconvenience.

Best regards,
Your Encoding Team
AION Media"""
