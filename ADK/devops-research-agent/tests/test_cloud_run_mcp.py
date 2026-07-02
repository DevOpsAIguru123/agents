import os
import unittest
from unittest import mock

from google.adk.agents import Agent


class CloudRunMcpTests(unittest.TestCase):
    def test_cloud_run_mcp_toolset_uses_npx_server(self):
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
        from mcp import StdioServerParameters

        from my_agent.cloud_run_mcp import (
            CLOUD_RUN_MCP_PACKAGE,
            CLOUD_RUN_MCP_TOOL_NAMES,
            create_cloud_run_mcp_toolset,
        )

        toolset = create_cloud_run_mcp_toolset()

        self.assertIsInstance(toolset, McpToolset)
        self.assertEqual(toolset.tool_filter, CLOUD_RUN_MCP_TOOL_NAMES)
        self.assertEqual(toolset.tool_name_prefix, "cloud_run")

        connection_params = toolset._connection_params
        self.assertIsInstance(connection_params, StdioConnectionParams)
        self.assertEqual(connection_params.timeout, 30.0)
        self.assertIsInstance(connection_params.server_params, StdioServerParameters)
        self.assertEqual(connection_params.server_params.command, "npx")
        self.assertEqual(connection_params.server_params.args, ["-y", CLOUD_RUN_MCP_PACKAGE])

    def test_cloud_run_mcp_env_aliases_are_passed_to_server(self):
        from my_agent.cloud_run_mcp import create_cloud_run_mcp_toolset

        with mock.patch.dict(
            os.environ,
            {
                "CLOUD_RUN_MCP_PROJECT": "demo-project",
                "CLOUD_RUN_MCP_REGION": "us-central1",
                "CLOUD_RUN_MCP_SERVICE_NAME": "demo-service",
                "CLOUD_RUN_MCP_TIMEOUT": "12.5",
            },
            clear=False,
        ):
            toolset = create_cloud_run_mcp_toolset()

        connection_params = toolset._connection_params
        self.assertEqual(connection_params.timeout, 12.5)
        self.assertEqual(
            connection_params.server_params.env["GOOGLE_CLOUD_PROJECT"],
            "demo-project",
        )
        self.assertEqual(
            connection_params.server_params.env["GOOGLE_CLOUD_REGION"],
            "us-central1",
        )
        self.assertEqual(
            connection_params.server_params.env["DEFAULT_SERVICE_NAME"],
            "demo-service",
        )

    def test_agent_does_not_wire_cloud_run_mcp(self):
        with mock.patch.dict(
            os.environ,
            {
                "ENABLE_CLOUD_RUN_MCP": "true",
                "ENABLE_GOOGLE_SEARCH_MCP": "false",
                "ENABLE_ADK_GOOGLE_SEARCH": "false",
            },
            clear=False,
        ):
            import importlib
            import my_agent.agent as agent_module

            agent_module = importlib.reload(agent_module)

        self.assertIsInstance(agent_module.root_agent, Agent)
        self.assertEqual(agent_module.root_agent.tools, [])
        self.assertNotIn("cloud_run MCP", agent_module.root_agent.instruction)
        self.assertEqual(agent_module.platform_root_agent.tools, [])


if __name__ == "__main__":
    unittest.main()
