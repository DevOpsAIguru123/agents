import os

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters


CLOUD_RUN_MCP_PACKAGE = os.getenv(
    "CLOUD_RUN_MCP_PACKAGE",
    "@google-cloud/cloud-run-mcp@1.10.0",
)
CLOUD_RUN_MCP_TOOL_NAMES = [
    "deploy_file_contents",
    "list_services",
    "get_service",
    "get_service_log",
    "deploy_local_folder",
    "deploy_container_image",
    "list_projects",
    "create_project",
]
_FALSE_VALUES = {"0", "false", "no", "off"}


def cloud_run_mcp_enabled() -> bool:
    """Return whether the local Cloud Run MCP stdio toolset should be attached."""
    return os.getenv("ENABLE_CLOUD_RUN_MCP", "true").strip().lower() not in _FALSE_VALUES


def create_cloud_run_mcp_toolset() -> McpToolset:
    """Create a Cloud Run MCP toolset backed by the npm stdio server."""
    env = dict(os.environ)

    if project := os.getenv("CLOUD_RUN_MCP_PROJECT"):
        env["GOOGLE_CLOUD_PROJECT"] = project
    if region := os.getenv("CLOUD_RUN_MCP_REGION"):
        env["GOOGLE_CLOUD_REGION"] = region
    if service_name := os.getenv("CLOUD_RUN_MCP_SERVICE_NAME"):
        env["DEFAULT_SERVICE_NAME"] = service_name

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.getenv("CLOUD_RUN_MCP_COMMAND", "npx"),
                args=["-y", CLOUD_RUN_MCP_PACKAGE],
                env=env,
            ),
            timeout=float(os.getenv("CLOUD_RUN_MCP_TIMEOUT", "30")),
        ),
        tool_filter=CLOUD_RUN_MCP_TOOL_NAMES,
        tool_name_prefix="cloud_run",
    )
