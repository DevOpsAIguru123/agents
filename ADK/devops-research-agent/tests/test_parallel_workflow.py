import unittest

from google.adk.agents import Agent
from google.adk.workflow import JoinNode, Workflow

from patterns.parallel_workflow.agent import root_agent


class ParallelWorkflowTests(unittest.TestCase):
    def test_root_agent_uses_parallel_fan_out_and_join(self):
        self.assertIsInstance(root_agent, Workflow)
        self.assertEqual(root_agent.name, "parallel_review_workflow")
        self.assertEqual(
            [(edge.from_node.name, edge.to_node.name) for edge in root_agent.graph.edges],
            [
                ("__START__", "benefits_reviewer"),
                ("__START__", "risks_reviewer"),
                ("benefits_reviewer", "join_reviews"),
                ("risks_reviewer", "join_reviews"),
                ("join_reviews", "synthesizer"),
            ],
        )

    def test_join_and_agent_outputs_are_named(self):
        self.assertTrue(
            any(isinstance(node, JoinNode) and node.name == "join_reviews" for node in root_agent.graph.nodes)
        )
        workflow_agents = [
            node for node in root_agent.graph.nodes if isinstance(node, Agent)
        ]
        self.assertEqual(
            [agent.output_key for agent in workflow_agents],
            ["benefits_review", "risks_review", "final_recommendation"],
        )


if __name__ == "__main__":
    unittest.main()

