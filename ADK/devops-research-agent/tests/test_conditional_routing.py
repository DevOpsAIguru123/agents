import unittest

from google.adk.agents import Agent
from google.adk.workflow import DEFAULT_ROUTE, FunctionNode, Workflow

from patterns.conditional_routing.agent import root_agent, route_request


class ConditionalRoutingTests(unittest.TestCase):
    def test_route_request_selects_expected_route(self):
        self.assertEqual(route_request("Add 2 and 3.").actions.route, "math")
        self.assertEqual(route_request("Write a launch email.").actions.route, "writing")
        self.assertEqual(route_request("Tell me something useful.").actions.route, "general")

    def test_root_agent_uses_conditional_edges(self):
        self.assertIsInstance(root_agent, Workflow)
        self.assertEqual(root_agent.name, "conditional_routing_workflow")
        self.assertEqual(
            [(edge.from_node.name, edge.to_node.name, edge.route) for edge in root_agent.graph.edges],
            [
                ("__START__", "route_request", None),
                ("route_request", "math_specialist", "math"),
                ("route_request", "writing_specialist", "writing"),
                ("route_request", "general_specialist", DEFAULT_ROUTE),
            ],
        )

    def test_router_and_specialists_are_typed(self):
        self.assertTrue(any(isinstance(node, FunctionNode) and node.name == "route_request" for node in root_agent.graph.nodes))
        workflow_agents = [
            node for node in root_agent.graph.nodes if isinstance(node, Agent)
        ]
        self.assertEqual(
            [agent.name for agent in workflow_agents],
            ["math_specialist", "writing_specialist", "general_specialist"],
        )


if __name__ == "__main__":
    unittest.main()
