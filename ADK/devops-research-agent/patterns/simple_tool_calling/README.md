# Simple Tool Calling Pattern

This pattern demonstrates the smallest useful Google ADK agent shape:

- one `root_agent`
- one or more plain Python functions exposed as tools
- one model selected from environment configuration
- local OAuth/Application Default Credentials through Vertex AI

Use this pattern when the agent should answer normally most of the time, but call deterministic Python code for operations that should not be guessed by the model.

## What This Agent Does

The agent can:

- return the current local time for a supported city
- add two numbers
- multiply two numbers

Supported time cities:

```text
Austin, Chicago, Denver, London, Los Angeles, New York, San Francisco, Seattle, Tokyo
```

Tools in `agent.py`:

```text
get_current_time(city: str) -> dict
calculate(operation: str, left: float, right: float) -> dict
```

## Files

```text
patterns/simple_tool_calling/
  README.md
  __init__.py
  agent.py
  .env.example
  .env
```

`agent.py` is the file ADK loads. It must expose:

```python
root_agent = Agent(...)
```

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

Before running the agent, authenticate once:

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
adk run patterns/simple_tool_calling
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/simple_tool_calling
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
What time is it in Chicago?
```

Expected behavior: the model calls `get_current_time` with `city="Chicago"` and returns the tool result in natural language.

```text
Add 2 and 3.
```

Expected behavior: the model calls `calculate` with `operation="add"`, `left=2`, and `right=3`.

```text
Multiply 4 by 5.
```

Expected behavior: the model calls `calculate` with `operation="multiply"`, `left=4`, and `right=5`.

```text
What time is it in Mumbai?
```

Expected behavior: the city is not supported, so the tool returns an error and the agent should explain the supported options.

## Pattern Anatomy

The important parts are:

```python
root_agent = Agent(
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash"),
    name="demo_time_agent",
    instruction="...",
    tools=[get_current_time, calculate],
)
```

ADK inspects the Python function signatures and docstrings to expose tool schemas to Gemini. Keep tool signatures simple and strongly typed where possible.

The tool return shape uses dictionaries with a `status` field:

```python
{
    "status": "success",
    "result": 5,
}
```

For expected user-facing failures, return structured error data instead of raising:

```python
{
    "status": "error",
    "error_message": "Unsupported operation ...",
}
```

## When To Use This Pattern

Use simple tool calling when:

- the agent has a small number of deterministic actions
- each tool can run independently
- there is no need for multi-step orchestration
- the model can decide when to call each tool

Do not use this pattern when:

- every request must follow a fixed sequence
- intermediate outputs need review or transformation
- multiple specialist agents should process the request in order

For fixed multi-step behavior, use `patterns/sequential_workflow`.

## Verification

Run the unit tests from the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
python -m unittest discover -s tests
```

Run a live smoke test:

```bash
adk run patterns/simple_tool_calling "add 2 and 3"
```

Expected final answer should report that the result is `5`.

## Troubleshooting

If you see:

```text
Directory 'agent.py' is a file.
```

you passed the file path instead of the folder. Use `adk run .` from this folder or `adk run patterns/simple_tool_calling` from the project root.

If you see:

```text
Directory 'simple_tool_calling' does not exist.
```

you are probably already inside `patterns/simple_tool_calling`. Use:

```bash
adk run .
```

If authentication fails, verify ADC:

```bash
gcloud auth application-default print-access-token >/dev/null && echo adc-ok
```

If the model is unavailable, check that `DEMO_AGENT_MODEL` is available in `GOOGLE_CLOUD_LOCATION`.
