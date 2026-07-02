# Conditional Routing Pattern

This pattern demonstrates branching with Google ADK's graph-based `Workflow` API.

Use this pattern when one entrypoint should dispatch requests to different specialist branches.

## What This Agent Does

The workflow runs a deterministic router first:

```text
START -> route_request
```

Then it branches:

```text
route_request -- math          -> math_specialist
route_request -- writing       -> writing_specialist
route_request -- DEFAULT_ROUTE -> general_specialist
```

The router also stores the original user request in workflow state as `original_request`, so each specialist can answer the actual prompt instead of only seeing the route label.

## Files

```text
patterns/conditional_routing/
  README.md
  __init__.py
  agent.py
  .env.example
  .env
```

## Environment

This sample uses OAuth/Application Default Credentials, not `GOOGLE_API_KEY`.

```bash
GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
DEMO_AGENT_MODEL="gemini-2.5-flash"
```

## Run

From the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk run patterns/conditional_routing
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/conditional_routing
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run `adk run agent.py`; ADK expects the directory containing `agent.py`.

## Example Prompts

Math branch:

```text
Add 12 and 30.
```

Writing branch:

```text
Write a short launch email for a new dashboard.
```

Default branch:

```text
Give me one practical tip for debugging APIs.
```

## Pattern Anatomy

The router returns an ADK `Event`:

```python
return Event(route=route, state={"original_request": node_input})
```

The `route` chooses the branch. The `state` preserves the original request for the selected specialist.

The routing map is declared in `edges`:

```python
edges=[
    (
        "START",
        route_request,
        {
            "math": math_specialist,
            "writing": writing_specialist,
            DEFAULT_ROUTE: general_specialist,
        },
    )
]
```

Use this pattern when route choice should be deterministic, auditable, and easy to test.
