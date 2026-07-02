import unittest

from google.adk.agents import Agent
from google.adk.workflow import Workflow

from patterns.sequential_workflow.agent import root_agent


class SequentialPipelineTests(unittest.TestCase):
    def test_root_agent_uses_graph_workflow_in_fixed_order(self):
        self.assertIsInstance(root_agent, Workflow)
        self.assertEqual(root_agent.name, "sequential_answer_pipeline")
        self.assertEqual(
            [(edge.from_node.name, edge.to_node.name) for edge in root_agent.graph.edges],
            [
                ("__START__", "request_analyzer"),
                ("request_analyzer", "researcher"),
                ("researcher", "writer"),
                ("writer", "reviewer"),
            ],
        )

    def test_workflow_nodes_persist_outputs_for_later_steps(self):
        workflow_agents = [
            node for node in root_agent.graph.nodes if isinstance(node, Agent)
        ]

        self.assertEqual(
            [agent.output_key for agent in workflow_agents],
            ["request_analysis", "research_notes", "draft_answer", "reviewed_answer"],
        )


if __name__ == "__main__":
    unittest.main()
