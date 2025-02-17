import logging
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

from .client import EncodingClient

logger = logging.getLogger(__name__)


class EncodingServer:
    """MCP server for encoding job management"""

    def __init__(self):
        self.api_client = EncodingClient()
        self.server = Server("encoding-manager")
        self.setup_handlers()

    def setup_handlers(self):
        """Set up all MCP protocol handlers"""

        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List all active encoding jobs as resources"""
            logger.debug("Handling list_resources request")
            try:
                jobs = await self.api_client.get_jobs()
                return [
                    types.Resource(
                        uri=AnyUrl(f"encoding://jobs/{job['id']}"),
                        name=f"Encoding Job: {job['sourceFile']}",
                        description=f"Status: {job['status']}, Progress: {job['progress']}%",
                        mimeType="application/json",
                    )
                    for job in jobs
                ]
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return []

        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read specific job details"""
            logger.debug(f"Handling read_resource request for URI: {uri}")
            if uri.scheme != "encoding":
                raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

            try:
                job_id = str(uri).split("/")[-1]
                job_data = await self.api_client.get_job(job_id)
                return str(job_data)
            except Exception as e:
                logger.error(f"Error reading resource: {e}")
                raise

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="get_job_status",
                    description="Get status of a specific encoding job",
                    inputSchema={
                        "type": "object",
                        "properties": {"job_id": {"type": "string", "description": "ID of the encoding job"}},
                        "required": ["job_id"],
                    },
                ),
                types.Tool(
                    name="list_active_jobs",
                    description="List all active encoding jobs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "processing"],
                                "description": "Filter jobs by status",
                            }
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent]:
            """Handle tool execution requests"""
            try:
                if name == "get_job_status":
                    if not arguments or "job_id" not in arguments:
                        raise ValueError("Missing job_id argument")

                    job_data = await self.api_client.get_job(arguments["job_id"])
                    return [types.TextContent(type="text", text=str(job_data))]

                elif name == "list_active_jobs":
                    status = arguments.get("status") if arguments else None
                    jobs = await self.api_client.get_jobs(status)
                    return [types.TextContent(type="text", text=str(jobs))]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Start the MCP server"""
        try:
            await self.api_client.init_session()

            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                logger.info("Server running with stdio transport")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="encoding",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        finally:
            await self.api_client.close_session()
