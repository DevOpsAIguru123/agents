import os

from google.adk import Agent


APPROVED_RECIPIENTS = {"alice", "bob"}
MAX_TRANSFER_AMOUNT = 1000


def transfer_funds(recipient: str, amount: float) -> dict:
    """Demo transfer tool guarded by before_tool_callback.

    Args:
        recipient: Approved recipient name.
        amount: Transfer amount in dollars.
    """
    return {
        "status": "success",
        "recipient": recipient,
        "amount": amount,
        "confirmation": "demo-transfer-approved",
    }


def guard_transfer(tool, args: dict, tool_context) -> dict | None:
    """Block transfer_funds calls that violate local guardrails."""
    recipient = str(args.get("recipient", "")).strip().lower()
    amount = float(args.get("amount", 0))

    if recipient not in APPROVED_RECIPIENTS:
        return {
            "status": "blocked",
            "reason": (
                f"{args.get('recipient')!r} is not an approved recipient. "
                "Approved recipients are Alice and Bob."
            ),
        }

    if amount > MAX_TRANSFER_AMOUNT:
        return {
            "status": "blocked",
            "reason": (
                f"Transfer amount {amount:g} exceeds the demo limit of "
                f"{MAX_TRANSFER_AMOUNT:g}."
            ),
        }

    return None


root_agent = Agent(
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash"),
    name="guarded_transfer_agent",
    description="Demonstrates before_tool_callback guardrails for tool calls.",
    instruction=(
        "You are a guarded demo transfer assistant. For transfer requests, call "
        "transfer_funds. Do not claim a transfer succeeded unless the tool "
        "returns success. If the tool returns blocked, explain the reason."
    ),
    tools=[transfer_funds],
    before_tool_callback=guard_transfer,
)

