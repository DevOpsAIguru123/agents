import importlib
import os
import unittest
from unittest import mock

from google.adk.tools import google_search


class AdkGoogleSearchTests(unittest.TestCase):
    def test_agent_wires_direct_adk_google_search_tool(self):
        with mock.patch.dict(
            os.environ,
            {
                "ENABLE_CLOUD_RUN_MCP": "false",
                "ENABLE_GOOGLE_SEARCH_MCP": "true",
                "ENABLE_ADK_GOOGLE_SEARCH": "true",
            },
            clear=False,
        ):
            import my_agent.agent as agent_module

            agent_module = importlib.reload(agent_module)

        self.assertEqual(len(agent_module.root_agent.tools), 1)
        self.assertIs(agent_module.root_agent.tools[0], google_search)
        self.assertIn("built-in google_search tool", agent_module.root_agent.instruction)
        self.assertNotIn("google_search_agent tool", agent_module.root_agent.instruction)
        self.assertNotIn("google_search MCP tool", agent_module.root_agent.instruction)
        self.assertEqual(len(agent_module.platform_root_agent.tools), 1)
        self.assertIs(agent_module.platform_root_agent.tools[0], google_search)


if __name__ == "__main__":
    unittest.main()
