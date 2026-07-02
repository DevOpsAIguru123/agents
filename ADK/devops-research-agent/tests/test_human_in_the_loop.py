import unittest

from google.adk.events.request_input import RequestInput
from google.adk.workflow import FunctionNode, Workflow

from patterns.human_in_the_loop.agent import (
    APPROVAL_INTERRUPT_ID,
    draft_response,
    parse_approval_response,
    publish_response,
    request_human_approval,
    revise_after_rejection,
    root_agent,
)


class FakeContext:
    def __init__(self, resume_inputs=None):
        self.resume_inputs = resume_inputs or {}


class HumanInTheLoopTests(unittest.TestCase):
    def test_root_agent_uses_approval_branch(self):
        self.assertIsInstance(root_agent, Workflow)
        self.assertEqual(root_agent.name, "human_approval_workflow")
        self.assertEqual(
            [(edge.from_node.name, edge.to_node.name, edge.route) for edge in root_agent.graph.edges],
            [
                ("__START__", "draft_response", None),
                ("draft_response", "request_human_approval", None),
                ("request_human_approval", "publish_response", "approved"),
                ("request_human_approval", "revise_after_rejection", "rejected"),
            ],
        )

    def test_approval_node_reruns_on_resume(self):
        approval_nodes = [
            node
            for node in root_agent.graph.nodes
            if isinstance(node, FunctionNode) and node.name == "request_human_approval"
        ]
        self.assertEqual(len(approval_nodes), 1)
        self.assertTrue(approval_nodes[0].rerun_on_resume)

    def test_request_human_approval_interrupts_without_resume_input(self):
        event_or_request = request_human_approval(FakeContext(), draft="Draft text")

        self.assertIsInstance(event_or_request, RequestInput)
        self.assertEqual(event_or_request.interrupt_id, APPROVAL_INTERRUPT_ID)
        self.assertIn("Approve", event_or_request.message)
        self.assertEqual(event_or_request.payload["draft"], "Draft text")

    def test_request_human_approval_routes_resume_response(self):
        approved = request_human_approval(
            FakeContext({APPROVAL_INTERRUPT_ID: {"approved": True, "feedback": "ship it"}}),
            draft="Draft text",
        )
        self.assertEqual(approved.actions.route, "approved")
        self.assertEqual(approved.actions.state_delta["approval_feedback"], "ship it")

        rejected = request_human_approval(
            FakeContext({APPROVAL_INTERRUPT_ID: {"approved": False, "feedback": "make it shorter"}}),
            draft="Draft text",
        )
        self.assertEqual(rejected.actions.route, "rejected")
        self.assertEqual(rejected.actions.state_delta["approval_feedback"], "make it shorter")

    def test_helpers_create_visible_content(self):
        draft = draft_response("Announce the release")
        self.assertIn("Draft prepared", draft.content.parts[0].text)
        self.assertIn("Announce the release", draft.actions.state_delta["draft"])

        parsed = parse_approval_response({"result": {"approved": True, "feedback": "ok"}})
        self.assertEqual(parsed, {"approved": True, "feedback": "ok"})

        published = publish_response("Draft", "approved", "ok")
        self.assertIn("Approved by human", published.parts[0].text)

        revised = revise_after_rejection("Draft", "needs detail")
        self.assertIn("Human requested changes", revised.parts[0].text)


if __name__ == "__main__":
    unittest.main()
