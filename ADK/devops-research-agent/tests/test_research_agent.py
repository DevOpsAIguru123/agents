import importlib
import os
import unittest
from unittest import mock


class ResearchAgentConfigTests(unittest.TestCase):
    def test_agent_is_configured_for_devops_platform_research(self):
        with mock.patch.dict(
            os.environ,
            {
                "ENABLE_CLOUD_RUN_MCP": "false",
                "ENABLE_GOOGLE_SEARCH_MCP": "false",
                "ENABLE_ADK_GOOGLE_SEARCH": "false",
            },
            clear=False,
        ):
            import my_agent.agent as agent_module

            agent_module = importlib.reload(agent_module)

        self.assertEqual(agent_module.root_agent.name, "devops_deep_research_agent")
        self.assertIn("DevOps Deep Research Agent", agent_module.root_agent.instruction)
        self.assertIn("Kubernetes", agent_module.root_agent.instruction)
        self.assertIn("Terraform", agent_module.root_agent.instruction)
        self.assertIn("observability", agent_module.root_agent.instruction)
        self.assertIn("plan with 3-5", agent_module.root_agent.instruction)
        self.assertIn("Critique your own findings", agent_module.root_agent.instruction)
        self.assertIn("inline citations", agent_module.root_agent.instruction)
        self.assertIn("DevOps Deep Research Agent", agent_module.root_agent.description)
        self.assertEqual(len(agent_module.platform_root_agent.tools), 1)


if __name__ == "__main__":
    unittest.main()
