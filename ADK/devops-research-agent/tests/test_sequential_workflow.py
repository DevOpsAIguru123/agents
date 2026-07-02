import unittest

from patterns.sequential_workflow import agent as workflow_agent


class SequentialWorkflowTests(unittest.TestCase):
    def test_runs_request_analysis_before_research_writing_and_review(self):
        self.assertEqual(workflow_agent.request_analyzer.name, "request_analyzer")
        self.assertEqual(workflow_agent.request_analyzer.output_key, "request_analysis")
        self.assertEqual(workflow_agent.researcher.name, "researcher")
        self.assertEqual(workflow_agent.researcher.output_key, "research_notes")

        _, *agents = workflow_agent.root_agent.edges[0]

        self.assertEqual(
            [agent.name for agent in agents],
            ["request_analyzer", "researcher", "writer", "reviewer"],
        )

    def test_later_agents_receive_analysis_and_research_notes(self):
        self.assertIn("{request_analysis}", workflow_agent.researcher.instruction)
        self.assertIn("{request_analysis}", workflow_agent.writer.instruction)
        self.assertIn("{research_notes}", workflow_agent.writer.instruction)
        self.assertIn("{request_analysis}", workflow_agent.reviewer.instruction)
        self.assertIn("{research_notes}", workflow_agent.reviewer.instruction)
        self.assertIn("{draft_answer}", workflow_agent.reviewer.instruction)

    def test_researcher_prompt_requires_substantive_topic_research(self):
        instruction = workflow_agent.researcher.instruction

        self.assertIn("Actual research notes", instruction)
        self.assertIn("Direct findings", instruction)
        self.assertIn("Evidence and examples", instruction)
        self.assertIn("Sources or verification status", instruction)
        self.assertIn("Do not stop at request analysis", instruction)


if __name__ == "__main__":
    unittest.main()
