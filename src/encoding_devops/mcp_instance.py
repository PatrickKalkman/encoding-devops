from mcp.server.fastmcp import FastMCP

# Create MCP instance that will be shared across the application
mcp = FastMCP("encoding-manager", dependencies=["aiohttp", "python-dotenv", "loguru", "cachetools"])
