import importlib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PatternLayoutTests(unittest.TestCase):
    def test_each_agent_pattern_has_own_folder(self):
        expected_patterns = [
            "simple_tool_calling",
            "sequential_workflow",
            "parallel_workflow",
            "conditional_routing",
            "loop_workflow",
            "guardrails_callbacks",
            "human_in_the_loop",
            "mcp_tools_usage",
        ]

        for pattern in expected_patterns:
            with self.subTest(pattern=pattern):
                pattern_dir = PROJECT_ROOT / "patterns" / pattern
                self.assertTrue(pattern_dir.is_dir())
                self.assertTrue((pattern_dir / "agent.py").is_file())
                self.assertTrue((pattern_dir / "__init__.py").is_file())
                self.assertTrue((pattern_dir / ".env.example").is_file())
                self.assertTrue((pattern_dir / "README.md").is_file())

    def test_pattern_agents_are_importable(self):
        for module_name in [
            "patterns.simple_tool_calling.agent",
            "patterns.sequential_workflow.agent",
            "patterns.parallel_workflow.agent",
            "patterns.conditional_routing.agent",
            "patterns.loop_workflow.agent",
            "patterns.guardrails_callbacks.agent",
            "patterns.human_in_the_loop.agent",
            "patterns.mcp_tools_usage.agent",
        ]:
            with self.subTest(module_name=module_name):
                module = importlib.import_module(module_name)
                self.assertTrue(hasattr(module, "root_agent"))


if __name__ == "__main__":
    unittest.main()
