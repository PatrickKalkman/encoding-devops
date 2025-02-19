# Import tools and prompts after everything is set up
import encoding_devops.prompts  # noqa
import encoding_devops.tools  # noqa
from encoding_devops.mcp_instance import mcp

# Export mcp instance
__all__ = ["mcp"]
