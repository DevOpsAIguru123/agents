import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters


MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")
MCP_SERVER_SCRIPT = Path(__file__).with_name("mcp_server.py").resolve()
MCP_TOOL_NAMES = ["knowledge_base_search", "get_runbook"]


def create_mcp_toolset() -> McpToolset:
    """Create a fresh MCP toolset connected to the local stdio server."""
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(MCP_SERVER_SCRIPT)],
            ),
            timeout=10.0,
        ),
        tool_filter=MCP_TOOL_NAMES,
        tool_name_prefix="kb",
    )


root_agent = Agent(
    name="mcp_tools_usage_agent",
    model=MODEL,
    description=(
        "Uses a local MCP stdio server as an ADK tool source."
    ),
    instruction=(
        "You answer questions using the local MCP knowledge-base tools. "
        "Use kb_knowledge_base_search to find relevant notes, then use "
        "kb_get_runbook when the user asks for exact steps or a runbook. "
        "Keep answers concise and mention which MCP tool supplied the facts."
    ),
    tools=[create_mcp_toolset()],
)
