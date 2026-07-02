# Parallel Workflow Pattern

This pattern demonstrates fan-out/fan-in orchestration with Google ADK's graph-based `Workflow` API.

Use this pattern when independent reviewers or workers can process the same user request at the same time, then a final node should combine their outputs.

## What This Agent Does

The workflow reviews a proposal from two angles:

```text
START -> benefits_reviewer -> join_reviews -> synthesizer
START -> risks_reviewer    -> join_reviews -> synthesizer
```

The two reviewer nodes run as parallel branches. `JoinNode` waits for both branches before the synthesizer runs.

State handoff:

```text
benefits_reviewer -> benefits_review
risks_reviewer    -> risks_review
synthesizer       -> final_recommendation
```

## Files

```text
patterns/parallel_workflow/
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
adk run patterns/parallel_workflow
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/parallel_workflow
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run `adk run agent.py`; ADK expects the directory containing `agent.py`.

## Example Prompt

```text
Should we add a cache in front of a slow product catalog API?
```

Expected behavior:

- `benefits_reviewer` lists upside.
- `risks_reviewer` lists risks and missing checks.
- `join_reviews` waits for both.
- `synthesizer` returns a balanced recommendation.

## Pattern Anatomy

The graph uses a tuple to fan out:

```python
edges=[
    (
        "START",
        (benefits_reviewer, risks_reviewer),
        join_reviews,
        synthesizer,
    )
]
```

ADK expands that into:

```text
__START__ -> benefits_reviewer
__START__ -> risks_reviewer
benefits_reviewer -> join_reviews
risks_reviewer -> join_reviews
join_reviews -> synthesizer
```

Use this pattern when branches are independent and can run before synthesis.

