import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from encoding_devops.server import mcp

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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


def main():
    """Entry point for the MCP server"""
    try:
        load_environment()

        logger.info("Starting Encoding MCP Server")
        mcp.run()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
