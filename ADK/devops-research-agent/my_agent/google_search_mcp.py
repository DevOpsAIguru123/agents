import os
import sys
from pathlib import Path

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters


GOOGLE_SEARCH_MCP_SERVER_SCRIPT = Path(__file__).with_name(
    "google_search_mcp_server.py"
).resolve()
GOOGLE_SEARCH_MCP_PACKAGE = os.getenv(
    "GOOGLE_SEARCH_MCP_PACKAGE",
    "@mcp-server/google-search-mcp@1.0.3",
)
GOOGLE_SEARCH_MCP_TOOL_NAMES = ["search"]
_FALSE_VALUES = {"0", "false", "no", "off"}


def google_search_mcp_enabled() -> bool:
    """Return whether the local Google Search MCP stdio toolset should be attached."""
    return os.getenv("ENABLE_GOOGLE_SEARCH_MCP", "true").strip().lower() not in _FALSE_VALUES


def create_google_search_mcp_toolset() -> McpToolset:
    """Create a Google Search MCP toolset backed by a local stdio server."""
    env = dict(os.environ)
    env.setdefault("LOG_LEVEL", "silent")
    command = os.getenv("GOOGLE_SEARCH_MCP_COMMAND", sys.executable)
    package_mode = command.endswith("npx") or command == "npx"
    args = (
        ["-y", GOOGLE_SEARCH_MCP_PACKAGE]
        if package_mode
        else [str(GOOGLE_SEARCH_MCP_SERVER_SCRIPT)]
    )

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=command,
                args=args,
                env=env,
            ),
            timeout=float(os.getenv("GOOGLE_SEARCH_MCP_TIMEOUT", "30")),
        ),
        tool_filter=GOOGLE_SEARCH_MCP_TOOL_NAMES,
        tool_name_prefix="google_search",
    )
