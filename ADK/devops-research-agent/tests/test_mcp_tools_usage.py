import sys
import tomllib
import unittest
import asyncio
from pathlib import Path

from google.adk.agents import Agent


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class McpToolsUsageTests(unittest.TestCase):
    def test_project_pins_mcp_dependency(self):
        pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

        self.assertIn("mcp==1.28.1", pyproject["project"]["dependencies"])

    def test_root_agent_uses_stdio_mcp_toolset(self):
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
        from mcp import StdioServerParameters

        from patterns.mcp_tools_usage.agent import (
            MCP_SERVER_SCRIPT,
            MCP_TOOL_NAMES,
            create_mcp_toolset,
            root_agent,
        )

        self.assertIsInstance(root_agent, Agent)
        self.assertEqual(root_agent.name, "mcp_tools_usage_agent")
        self.assertIn("knowledge_base_search", root_agent.instruction)
        self.assertEqual(len(root_agent.tools), 1)

        toolset = root_agent.tools[0]
        self.assertIsInstance(toolset, McpToolset)
        self.assertEqual(toolset.tool_filter, MCP_TOOL_NAMES)
        self.assertEqual(toolset.tool_name_prefix, "kb")

        connection_params = toolset._connection_params
        self.assertIsInstance(connection_params, StdioConnectionParams)
        self.assertEqual(connection_params.timeout, 10.0)
        self.assertIsInstance(connection_params.server_params, StdioServerParameters)
        self.assertEqual(connection_params.server_params.command, sys.executable)
        self.assertEqual(connection_params.server_params.args, [str(MCP_SERVER_SCRIPT)])

        fresh_toolset = create_mcp_toolset()
        self.assertIsInstance(fresh_toolset, McpToolset)
        self.assertIsNot(fresh_toolset, toolset)

    def test_demo_server_functions_are_deterministic(self):
        from patterns.mcp_tools_usage.mcp_server import (
            KNOWLEDGE_BASE,
            get_runbook,
            knowledge_base_search,
        )

        search_result = knowledge_base_search("oauth")
        self.assertEqual(search_result["query"], "oauth")
        self.assertGreaterEqual(len(search_result["matches"]), 1)
        self.assertIn("title", search_result["matches"][0])

        phrase_result = knowledge_base_search("OAuth setup notes")
        self.assertEqual(phrase_result["matches"][0]["slug"], "gemini-oauth-adk")

        self.assertIn("smoke-test-api", KNOWLEDGE_BASE)
        runbook = get_runbook("smoke-test-api")
        self.assertEqual(runbook["slug"], "smoke-test-api")
        self.assertIn("steps", runbook)

        missing = get_runbook("missing")
        self.assertEqual(missing["status"], "not_found")

    def test_toolset_lists_tools_from_local_mcp_server(self):
        from patterns.mcp_tools_usage.agent import (
            MCP_TOOL_NAMES,
            create_mcp_toolset,
        )

        async def list_tool_names():
            toolset = create_mcp_toolset()
            try:
                tools = await toolset.get_tools()
                prefixed_tools = await toolset.get_tools_with_prefix()
                return [tool.name for tool in tools], [
                    tool.name for tool in prefixed_tools
                ]
            finally:
                await toolset.close()

        tool_names, prefixed_tool_names = asyncio.run(list_tool_names())

        self.assertEqual(tool_names, MCP_TOOL_NAMES)
        self.assertEqual(
            prefixed_tool_names,
            [f"kb_{tool_name}" for tool_name in MCP_TOOL_NAMES],
        )


if __name__ == "__main__":
    unittest.main()
