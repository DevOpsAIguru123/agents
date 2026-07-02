# Sequential Workflow Pattern

This pattern demonstrates a deterministic Google ADK workflow using the graph-based `Workflow` API.

Use this pattern when a request should always move through the same stages instead of letting one agent decide everything in a single turn.

## What This Agent Does

The workflow processes a user request through four ordered nodes:

```text
START -> request_analyzer -> researcher -> writer -> reviewer
```

Each node is an `Agent`. The root object is a `Workflow`:

```python
root_agent = Workflow(...)
```

The nodes pass information through ADK state using `output_key` values:

```text
request_analyzer -> request_analysis
researcher       -> research_notes
writer           -> draft_answer
reviewer         -> reviewed_answer
```

## Files

```text
patterns/sequential_workflow/
  README.md
  __init__.py
  agent.py
  .env.example
  .env
```

`agent.py` contains all node definitions and the root workflow graph.

`__init__.py` makes the folder importable in tests.

`.env.example` documents the required environment variables. `.env` contains the local values and should not be committed.

## Environment

This sample uses OAuth/Application Default Credentials, not `GOOGLE_API_KEY`.

Expected `.env` shape:

```bash
GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
DEMO_AGENT_MODEL="gemini-2.5-flash"
```

Before running the workflow, authenticate once:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com --project YOUR_PROJECT_ID
```

## Install

From the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Run

From the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk run patterns/sequential_workflow
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/sequential_workflow
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run:

```bash
adk run agent.py
```

ADK expects the directory containing `agent.py`, not the Python file itself.

## Example Prompts

```text
Give me a one sentence plan for testing a REST API.
```

Expected behavior:

- `request_analyzer` extracts the goal and the one-sentence constraint.
- `researcher` creates useful notes about REST API testing.
- `writer` drafts a single-sentence answer.
- `reviewer` preserves the one-sentence constraint and returns the final answer.

```text
Explain the tradeoffs between simple tool-calling agents and workflow agents in three bullets.
```

Expected behavior: the workflow should produce analysis, research notes, a draft, and a final reviewed three-bullet answer.

## Pattern Anatomy

The graph is declared in one place:

```python
root_agent = Workflow(
    name="sequential_answer_pipeline",
    description=(
        "A deterministic graph workflow that runs request analysis, research, "
        "writing, and review in order."
    ),
    edges=[("START", request_analyzer, researcher, writer, reviewer)],
)
```

The tuple in `edges` defines an ordered chain. ADK expands it into these graph edges:

```text
__START__ -> request_analyzer
request_analyzer -> researcher
researcher -> writer
writer -> reviewer
```

Each intermediate agent writes state with `output_key`:

```python
request_analyzer = Agent(..., output_key="request_analysis")
researcher = Agent(..., output_key="research_notes")
writer = Agent(..., output_key="draft_answer")
reviewer = Agent(..., output_key="reviewed_answer")
```

Later agents reference earlier outputs in their instructions:

```text
Request analysis:
{request_analysis}

Research notes:
{research_notes}
```

## Why Workflow Instead Of SequentialAgent

The installed `google-adk==2.3.0` package emits a deprecation warning for `SequentialAgent` and recommends the newer `Workflow` API.

This sample therefore uses:

```python
from google.adk.workflow import Workflow
```

instead of:

```python
from google.adk.agents import SequentialAgent
```

## Important Behavior Notes

This sample does not include a browser or retrieval tool. The `researcher` node uses the model's available knowledge and should name verification needs when the request depends on current information.

For current facts, prices, schedules, laws, or anything that must be source-backed, add a search/retrieval tool before relying on the answer.

The reviewer node is instructed to preserve the user's requested format and length. This matters because reviewer agents can otherwise expand a concise draft into a much longer answer.

## When To Use This Pattern

Use a workflow when:

- the steps should always run in the same order
- each step has a distinct responsibility
- intermediate outputs should be visible or testable
- a final review pass should enforce constraints
- you want predictable orchestration rather than model-decided delegation

Do not use this pattern when:

- the task only needs one model call
- a simple function tool can solve the request
- the agent should freely choose between tools and sub-agents

For the smallest useful pattern, use `patterns/simple_tool_calling`.

## Verification

Run the unit tests from the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
python -m unittest discover -s tests
```

Run a live smoke test:

```bash
adk run patterns/sequential_workflow "Give me a one sentence plan for testing a REST API."
```

Expected behavior: the CLI shows each workflow node in order and the reviewer output remains one sentence.

## Troubleshooting

If you see:

```text
Directory 'agent.py' is a file.
```

you passed the file path instead of the folder. Use `adk run .` from this folder or `adk run patterns/sequential_workflow` from the project root.

If you see:

```text
Directory 'sequential_workflow' does not exist.
```

you are probably already inside `patterns/sequential_workflow`. Use:

```bash
adk run .
```

If a later node does not seem to use an earlier node's output, check:

- the earlier node has a unique `output_key`
- the later instruction references the same key with `{key_name}`
- the workflow edge order places the writer before the reader

If authentication fails, verify ADC:

```bash
gcloud auth application-default print-access-token >/dev/null && echo adc-ok
```

If the model is unavailable, check that `DEMO_AGENT_MODEL` is available in `GOOGLE_CLOUD_LOCATION`.
