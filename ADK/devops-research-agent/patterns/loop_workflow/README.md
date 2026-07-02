# Loop Workflow Pattern

This pattern demonstrates a bounded loop using Google ADK's graph-based `Workflow` API.

`LoopAgent` exists in the installed package, but `google-adk==2.3.0` marks it deprecated and recommends `Workflow`. This sample uses a route-controlled graph cycle instead.

## What This Agent Does

The workflow creates a draft, checks whether another revision is needed, revises once, then exits:

```text
START -> initialize_draft -> quality_check -- revise -> revise_draft -> quality_check
                                |
                                done
                                v
                           final_answer
```

The loop is bounded by state:

```text
iteration = 1 -> revise
iteration = 2 -> done
```

## Files

```text
patterns/loop_workflow/
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
adk run patterns/loop_workflow
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/loop_workflow
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run `adk run agent.py`; ADK expects the directory containing `agent.py`.

## Example Prompt

```text
Write a two step smoke test plan for an API.
```

Expected behavior: the workflow emits visible messages for initialization,
quality check, revision, final quality check, and final answer. It also keeps
state/route events so ADK Web can show the loop mechanics.

## Pattern Anatomy

The loop is controlled by route values:

```python
def quality_check(iteration: int, draft: str) -> Event:
    if iteration < 2:
        return Event(route="revise")
    return Event(route="done")
```

The graph cycles only through the `revise` route:

```python
edges=[
    (
        "START",
        initialize_draft,
        quality_check,
        {
            "revise": revise_draft,
            "done": final_answer,
        },
    ),
    (revise_draft, quality_check),
]
```

Use this pattern when the workflow needs a bounded refine/check loop with an explicit exit condition.

## ADK Web Display Note

Pure state-only function nodes show up in ADK Web as compact state/route chips.
This pattern intentionally emits `message=...` on each function-node event so
the UI displays the actual input, draft, quality check, and revision text.
