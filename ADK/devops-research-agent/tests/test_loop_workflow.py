import unittest

from google.adk.events.event import Event
from google.adk.workflow import FunctionNode, Workflow

from patterns.loop_workflow.agent import (
    final_answer,
    initialize_draft,
    quality_check,
    revise_draft,
    root_agent,
)


class LoopWorkflowTests(unittest.TestCase):
    def test_root_agent_uses_route_controlled_cycle(self):
        self.assertIsInstance(root_agent, Workflow)
        self.assertEqual(root_agent.name, "loop_refinement_workflow")
        self.assertEqual(
            [(edge.from_node.name, edge.to_node.name, edge.route) for edge in root_agent.graph.edges],
            [
                ("__START__", "initialize_draft", None),
                ("initialize_draft", "quality_check", None),
                ("quality_check", "revise_draft", "revise"),
                ("quality_check", "final_answer", "done"),
                ("revise_draft", "quality_check", None),
            ],
        )

    def test_loop_nodes_are_function_nodes(self):
        node_names = [
            node.name for node in root_agent.graph.nodes if isinstance(node, FunctionNode)
        ]
        self.assertEqual(
            node_names,
            ["initialize_draft", "quality_check", "revise_draft", "final_answer"],
        )

    def test_loop_functions_update_state_and_route(self):
        initialized = initialize_draft("Write a test plan")
        self.assertIsInstance(initialized, Event)
        self.assertIn("Initialized draft from input", initialized.content.parts[0].text)
        self.assertEqual(initialized.actions.state_delta["iteration"], 1)
        self.assertIn("Write a test plan", initialized.actions.state_delta["draft"])

        should_revise = quality_check(iteration=1, draft="Draft")
        self.assertEqual(should_revise.actions.route, "revise")
        self.assertIn("needs one more revision", should_revise.content.parts[0].text)

        revised = revise_draft(iteration=1, draft="Draft")
        self.assertEqual(revised.actions.state_delta["iteration"], 2)
        self.assertIn("Refined", revised.actions.state_delta["draft"])
        self.assertIn("Revised draft", revised.content.parts[0].text)

        should_finish = quality_check(iteration=2, draft="Draft")
        self.assertEqual(should_finish.actions.route, "done")
        self.assertIn("ready", should_finish.content.parts[0].text)
        final = final_answer(iteration=2, draft="Draft")
        self.assertIn("Final answer", final.parts[0].text)


if __name__ == "__main__":
    unittest.main()
