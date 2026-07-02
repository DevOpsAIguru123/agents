# Google ADK Sample Agents

Minimal Python samples for the Google Agent Development Kit (ADK). These agents
use Google OAuth through Application Default Credentials, not a Gemini API key.

## Agents

The primary `my_agent` app is the DevOps Deep Research Agent.
It helps investigate infrastructure, CI/CD, Kubernetes, Cloud Run, GKE,
Terraform, observability, SRE, security, cost, release engineering, and internal
developer platform topics. It is configured to produce practical findings,
tradeoffs, risks, recommendations, and implementation guidance.

Its research behavior is adapted from the ADK `deep-search` sample: broad
requests are planned first, substantial work is split into search and synthesis
phases, weak coverage triggers follow-up search, and final answers should cite
or name sources when Google Search grounding provides them. This project keeps
that behavior in a single main agent instead of copying the full multi-agent
sample app.

| Agent | Pattern | Run command |
| --- | --- | --- |
| `patterns/simple_tool_calling` | Simple tool-calling agent for current-time questions plus basic addition and multiplication | `adk run patterns/simple_tool_calling` |
| `patterns/sequential_workflow` | Sequential workflow: research, write, then review | `adk run patterns/sequential_workflow` |
| `patterns/parallel_workflow` | Parallel fan-out/fan-in workflow: benefits review and risks review, then synthesis | `adk run patterns/parallel_workflow` |
| `patterns/conditional_routing` | Conditional workflow: deterministic router sends requests to math, writing, or general specialists | `adk run patterns/conditional_routing` |
| `patterns/loop_workflow` | Route-controlled loop workflow: initialize, check, revise, and exit | `adk run patterns/loop_workflow` |
| `patterns/guardrails_callbacks` | Tool-calling agent with `before_tool_callback` policy guardrails | `adk run patterns/guardrails_callbacks` |
| `patterns/human_in_the_loop` | Human approval workflow: draft, pause for approval, then publish or revise | `adk run patterns/human_in_the_loop` |
| `patterns/mcp_tools_usage` | MCP toolset agent: connect to a local stdio MCP server and use its tools | `adk run patterns/mcp_tools_usage` |
| `patterns/agent_to_agent` | Agent to Agent (a2a) delegation: a manager agent delegates tasks to an expert subagent | `adk run patterns/agent_to_agent` |

Each pattern folder has its own detailed README:

- [Simple Tool Calling](patterns/simple_tool_calling/README.md)
- [Sequential Workflow](patterns/sequential_workflow/README.md)
- [Parallel Workflow](patterns/parallel_workflow/README.md)
- [Conditional Routing](patterns/conditional_routing/README.md)
- [Loop Workflow](patterns/loop_workflow/README.md)
- [Guardrails Callbacks](patterns/guardrails_callbacks/README.md)
- [Human In The Loop](patterns/human_in_the_loop/README.md)
- [MCP Tools Usage](patterns/mcp_tools_usage/README.md)
- [Agent to Agent](patterns/agent_to_agent/README.md)

## Setup

```bash
cd /Users/vinodv/projects/AI/agents/adk
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp patterns/simple_tool_calling/.env.example patterns/simple_tool_calling/.env
cp patterns/sequential_workflow/.env.example patterns/sequential_workflow/.env
cp patterns/parallel_workflow/.env.example patterns/parallel_workflow/.env
cp patterns/conditional_routing/.env.example patterns/conditional_routing/.env
cp patterns/loop_workflow/.env.example patterns/loop_workflow/.env
cp patterns/guardrails_callbacks/.env.example patterns/guardrails_callbacks/.env
cp patterns/human_in_the_loop/.env.example patterns/human_in_the_loop/.env
cp patterns/mcp_tools_usage/.env.example patterns/mcp_tools_usage/.env
cp patterns/agent_to_agent/.env.example patterns/agent_to_agent/.env
```

Authenticate with Google Cloud:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com --project YOUR_PROJECT_ID
```

Edit each agent `.env` and set:

```bash
GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
GOOGLE_CLOUD_LOCATION="us-central1"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
DEMO_AGENT_MODEL="gemini-2.5-flash"
```

This is the OAuth/ADC path ADK uses for Gemini models through Google Cloud
Agent Platform / Vertex AI. Do not set `GOOGLE_API_KEY` for this sample.

### Cloud Run MCP

The project includes an optional Google Cloud Run MCP helper, but `my_agent`
does not attach Cloud Run tools by default. The helper can create a local stdio
toolset using:

```json
{
  "command": "npx",
  "args": ["-y", "@google-cloud/cloud-run-mcp@1.10.0"]
}
```

The tool names are exposed to ADK with the `cloud_run_` prefix:
`cloud_run_list_projects`, `cloud_run_create_project`,
`cloud_run_list_services`, `cloud_run_get_service`,
`cloud_run_get_service_log`, `cloud_run_deploy_local_folder`,
`cloud_run_deploy_file_contents`, and `cloud_run_deploy_container_image`.
Authenticate locally before using these tools:

```bash
gcloud auth login
gcloud auth application-default login
```

Optional local defaults:

```bash
export CLOUD_RUN_MCP_PROJECT="YOUR_PROJECT_ID"
export CLOUD_RUN_MCP_REGION="us-central1"
export CLOUD_RUN_MCP_SERVICE_NAME="YOUR_SERVICE_NAME"
```

The Agent Platform `platform_app` keeps this toolset disabled because source
deployments do not guarantee a Node.js runtime.

### ADK Google Search

`my_agent` uses ADK's built-in Google Search integration directly. ADK requires
`google_search` to be the only tool inside the agent instance, so Cloud Run MCP
tools are not attached to the main agent.

Set `ENABLE_ADK_GOOGLE_SEARCH=false` to disable the built-in search path.

In production UIs, Google Search grounding may return Search Suggestions HTML
that must be displayed according to Google's grounding policy.

### Google Search MCP Fallback

When `ENABLE_ADK_GOOGLE_SEARCH=false`, `my_agent` can attach a local Google
Search MCP fallback server using:

```bash
python my_agent/google_search_mcp_server.py
```

The MCP server exposes `search`; ADK prefixes that as `google_search_search`.
It searches Google News RSS for current web/news results and accepts `query`,
plus optional `limit`, `timeout`, `language`, and `region` arguments.

Set `ENABLE_GOOGLE_SEARCH_MCP=false` to start `my_agent` without this local MCP
process. The Agent Platform `platform_app` keeps this toolset disabled because
source deployments should avoid local stdio processes unless explicitly
packaged for them.

To experiment with the npm Playwright-based server instead, set:

```bash
export GOOGLE_SEARCH_MCP_COMMAND=npx
export GOOGLE_SEARCH_MCP_PACKAGE="@mcp-server/google-search-mcp@1.0.3"
```

## Verify OAuth

```bash
python scripts/check_gemini_oauth.py
```

The script should print `oauth-ok`.

## Evaluate

ADK eval uses the agent directory as its first argument. Do not pass
`__init__.py` or `agent.py`.

Run the MCP tools usage eval:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk eval \
  patterns/mcp_tools_usage \
  evals/mcp_tools_usage.evalset.json \
  --config_file_path evals/eval_config.json \
  --print_detailed_results
```

The sample eval checks that the agent calls `kb_knowledge_base_search` for an
OAuth setup query and that the final response sufficiently matches the
reference answer.

## Run

From the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/simple_tool_calling
```

Run the sequential workflow pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/sequential_workflow
```

Run the parallel workflow pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/parallel_workflow
```

Run the conditional routing pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/conditional_routing
```

Run the loop workflow pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/loop_workflow
```

Run the guardrails callbacks pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/guardrails_callbacks
```

Run the human-in-the-loop pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/human_in_the_loop
```

Run the MCP tools usage pattern:

```bash
cd /Users/vinodv/projects/AI/agents/adk
adk run patterns/mcp_tools_usage
```

From inside a pattern folder, run the current directory:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/simple_tool_calling
adk run .
```

Do not run `adk run agent.py`; ADK expects the agent directory that contains
`agent.py`.

Or start ADK's development UI from this parent directory:

```bash
adk web --port 8000
```

Then open `http://localhost:8000` and select `my_agent` or a pattern folder.
