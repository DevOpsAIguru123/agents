# Guardrails Callbacks Pattern

This pattern demonstrates ADK tool guardrails with `before_tool_callback`.

Use this pattern when the model may call tools, but local policy should be able to inspect, block, or override a tool call before it executes.

## What This Agent Does

The agent has one demo tool:

```text
transfer_funds(recipient: str, amount: float) -> dict
```

Before the tool executes, `guard_transfer` checks:

- recipient must be approved: Alice or Bob
- amount must be less than or equal to `1000`

If a request violates those rules, the callback returns a replacement tool response and ADK skips the actual tool call.

## Files

```text
patterns/guardrails_callbacks/
  README.md
  __init__.py
  agent.py
  .env.example
  .env
```

## Run

From the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk run patterns/guardrails_callbacks
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/guardrails_callbacks
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run `adk run agent.py`; ADK expects the directory containing `agent.py`.

## Example Prompts

Allowed:

```text
Transfer 25 dollars to Alice.
```

Blocked by amount:

```text
Transfer 1500 dollars to Alice.
```

Blocked by recipient:

```text
Transfer 25 dollars to Mallory.
```

## Pattern Anatomy

The callback returns `None` to allow a tool call:

```python
return None
```

It returns a dictionary to block/override a tool call:

```python
return {
    "status": "blocked",
    "reason": "Transfer amount exceeds the demo limit.",
}
```

The agent wires the guardrail here:

```python
root_agent = Agent(
    tools=[transfer_funds],
    before_tool_callback=guard_transfer,
)
```

Use this pattern for policy checks, argument validation, rate limits, allowlists, and tool-call safety gates.

