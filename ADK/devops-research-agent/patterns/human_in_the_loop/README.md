# Human In The Loop Pattern

This pattern demonstrates an ADK workflow that pauses for a human approval decision before continuing.

Use this pattern when an agent can draft work automatically, but a person must approve, reject, or provide feedback before the workflow publishes the result.

## What This Agent Does

The workflow has four steps:

```text
START
  -> draft_response
  -> request_human_approval
       approved -> publish_response
       rejected -> revise_after_rejection
```

`draft_response` creates a visible draft and stores it in workflow state.

`request_human_approval` returns a `RequestInput` interrupt when there is no resume input. ADK Web can render this as a human response request. When the human responds, the node runs again because it is wrapped with `rerun_on_resume=True`.

`publish_response` returns the final answer when the human approves.

`revise_after_rejection` returns revision guidance when the human rejects the draft.

## Files

```text
patterns/human_in_the_loop/
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
adk run patterns/human_in_the_loop
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/human_in_the_loop
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run `adk run agent.py`; ADK expects the directory containing `agent.py`.

## Example Prompt

```text
Draft a short release announcement for the new dashboard.
```

The workflow pauses at the approval step. Approve with:

```json
{"approved": true, "feedback": "Looks good"}
```

Reject with:

```json
{"approved": false, "feedback": "Make it shorter and more specific"}
```

For the clearest manual test, use ADK Web:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk web --port 8000
```

Then open `http://localhost:8000`, select `human_in_the_loop`, send the example prompt, and respond to the approval request. In CLI JSONL output, the pause appears as an `adk_request_input` function call with `longRunningToolIds`.

## Pattern Anatomy

The interrupt is created with `RequestInput`:

```python
return RequestInput(
    interrupt_id=APPROVAL_INTERRUPT_ID,
    message="Approve this draft?",
    payload={"draft": draft},
)
```

The approval node must run again after the human responds:

```python
approval_node = node(
    request_human_approval,
    name="request_human_approval",
    rerun_on_resume=True,
)
```

The resumed node returns an `Event(route=...)` so the workflow can choose the next branch:

```python
route = "approved" if decision["approved"] else "rejected"
return Event(route=route, state={"approval_decision": route})
```

Use this pattern for approvals, review gates, sensitive actions, release checks, policy decisions, and any workflow step where a human must be in control before the agent proceeds.
