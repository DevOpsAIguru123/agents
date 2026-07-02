import os
import unittest
from unittest import mock

from google.adk.agents import Agent


class GoogleSearchMcpTests(unittest.TestCase):
    def test_google_search_mcp_toolset_uses_npx_server(self):
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
        from mcp import StdioServerParameters

        from my_agent.google_search_mcp import (
            GOOGLE_SEARCH_MCP_SERVER_SCRIPT,
            GOOGLE_SEARCH_MCP_TOOL_NAMES,
            create_google_search_mcp_toolset,
        )

        toolset = create_google_search_mcp_toolset()

        self.assertIsInstance(toolset, McpToolset)
        self.assertEqual(toolset.tool_filter, GOOGLE_SEARCH_MCP_TOOL_NAMES)
        self.assertEqual(toolset.tool_name_prefix, "google_search")

        connection_params = toolset._connection_params
        self.assertIsInstance(connection_params, StdioConnectionParams)
        self.assertEqual(connection_params.timeout, 30.0)
        self.assertIsInstance(connection_params.server_params, StdioServerParameters)
        self.assertEqual(connection_params.server_params.command, os.sys.executable)
        self.assertEqual(connection_params.server_params.args, [str(GOOGLE_SEARCH_MCP_SERVER_SCRIPT)])
        self.assertEqual(connection_params.server_params.env["LOG_LEVEL"], "silent")

    def test_google_search_mcp_can_use_npx_package_override(self):
        from my_agent.google_search_mcp import (
            GOOGLE_SEARCH_MCP_PACKAGE,
            create_google_search_mcp_toolset,
        )

        with mock.patch.dict(
            os.environ,
            {"GOOGLE_SEARCH_MCP_COMMAND": "npx"},
            clear=False,
        ):
            toolset = create_google_search_mcp_toolset()

        connection_params = toolset._connection_params
        self.assertEqual(connection_params.server_params.command, "npx")
        self.assertEqual(connection_params.server_params.args, ["-y", GOOGLE_SEARCH_MCP_PACKAGE])

    def test_google_search_mcp_timeout_can_be_overridden(self):
        from my_agent.google_search_mcp import create_google_search_mcp_toolset

        with mock.patch.dict(
            os.environ,
            {"GOOGLE_SEARCH_MCP_TIMEOUT": "12.5"},
            clear=False,
        ):
            toolset = create_google_search_mcp_toolset()

        self.assertEqual(toolset._connection_params.timeout, 12.5)

    def test_agent_wires_google_search_mcp_only_for_local_root_agent(self):
        with mock.patch.dict(
            os.environ,
            {
                "ENABLE_CLOUD_RUN_MCP": "false",
                "ENABLE_GOOGLE_SEARCH_MCP": "true",
            },
            clear=False,
        ):
            import importlib
            import my_agent.agent as agent_module

            agent_module = importlib.reload(agent_module)

        self.assertIsInstance(agent_module.root_agent, Agent)
        self.assertEqual(len(agent_module.root_agent.tools), 1)
        self.assertIn("google_search MCP", agent_module.root_agent.instruction)
        self.assertEqual(agent_module.platform_root_agent.tools, [])

    def test_google_news_search_parses_rss_results(self):
        from my_agent import google_search_mcp_server as server

        rss = b"""<?xml version="1.0" encoding="UTF-8" ?>
        <rss><channel>
          <item>
            <title>Platform engineering news</title>
            <link>https://news.google.com/articles/example</link>
            <source>Example Tech</source>
            <pubDate>Thu, 02 Jul 2026 12:00:00 GMT</pubDate>
            <description>Useful summary</description>
          </item>
        </channel></rss>"""
        response = mock.Mock()
        response.content = rss
        response.raise_for_status.return_value = None

        with mock.patch.object(server.requests, "get", return_value=response):
            result = server.search("platform engineering", limit=5)

        self.assertEqual(result["source"], "Google News RSS")
        self.assertEqual(result["results"][0]["title"], "Platform engineering news")
        self.assertEqual(result["results"][0]["source"], "Example Tech")
        self.assertEqual(result["results"][0]["published_at"], "2026-07-02T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
