import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from encoding_devops.client import EncodingClient
from encoding_devops.server import mcp

# Configure loguru logging
logger.add(sys.stderr, format="{time} {level} {message}", level="DEBUG")

# Ensure UTF-8 encoding on Windows
if sys.platform == "win32" and os.environ.get("PYTHONIOENCODING") is None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment from .env file")
    else:
        logger.warning("No .env file found, using system environment variables")

    # Validate required environment variables
    required_vars = ["ENCODING_API_URL", "ENCODING_CLIENT_ID", "ENCODING_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


async def run_server():
    """Run the MCP server"""
    if hasattr(mcp, "run_async"):
        await mcp.run_async()  # If there's an async version
    else:
        # Run synchronous mcp.run() in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, mcp.run)


async def main():
    """Entry point for the MCP server"""
    try:
        load_environment()
        client = EncodingClient()
        await client.refresh_token()
        await client.get_job("test")
        logger.info("Starting Encoding MCP Server")
        await run_server()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def entrypoint():
    """Synchronous entrypoint for script execution"""
    asyncio.run(main())

if __name__ == "__main__":
    entrypoint()
