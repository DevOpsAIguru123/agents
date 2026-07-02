import unittest

from google.adk import Agent

from patterns.guardrails_callbacks.agent import (
    guard_transfer,
    root_agent,
    transfer_funds,
)


class GuardrailsCallbacksTests(unittest.TestCase):
    def test_root_agent_has_tool_guardrail_callback(self):
        self.assertIsInstance(root_agent, Agent)
        self.assertEqual(root_agent.name, "guarded_transfer_agent")
        self.assertIs(root_agent.before_tool_callback, guard_transfer)
        self.assertEqual(root_agent.tools, [transfer_funds])

    def test_guard_blocks_large_or_unknown_transfers(self):
        large_transfer = guard_transfer(
            tool=None,
            args={"recipient": "Alice", "amount": 1500},
            tool_context=None,
        )
        self.assertEqual(large_transfer["status"], "blocked")
        self.assertIn("limit", large_transfer["reason"])

        unknown_recipient = guard_transfer(
            tool=None,
            args={"recipient": "Mallory", "amount": 25},
            tool_context=None,
        )
        self.assertEqual(unknown_recipient["status"], "blocked")
        self.assertIn("approved", unknown_recipient["reason"])

    def test_guard_allows_safe_transfer_and_tool_succeeds(self):
        allowed = guard_transfer(
            tool=None,
            args={"recipient": "Alice", "amount": 25},
            tool_context=None,
        )
        self.assertIsNone(allowed)

        result = transfer_funds(recipient="Alice", amount=25)
        self.assertEqual(
            result,
            {
                "status": "success",
                "recipient": "Alice",
                "amount": 25,
                "confirmation": "demo-transfer-approved",
            },
        )


if __name__ == "__main__":
    unittest.main()
