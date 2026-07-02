# MCP Tools Usage Pattern

This pattern demonstrates how an ADK agent can use tools served by a local MCP server.

Use this pattern when tools already live behind the Model Context Protocol, or when you want a clean boundary between agent logic and tool implementation.

## What This Agent Does

The pattern has two parts:

```text
agent.py
  -> McpToolset
  -> stdio connection
  -> mcp_server.py
       knowledge_base_search
       get_runbook
```

`mcp_server.py` is a tiny local `FastMCP` server. It exposes two deterministic tools backed by an in-memory ADK sample knowledge base.

`agent.py` creates an ADK `McpToolset` that starts that server over stdio and exposes only the two allowed tools. The tool names are prefixed with `kb_` before the model sees them.

## Files

```text
patterns/mcp_tools_usage/
  README.md
  __init__.py
  agent.py
  mcp_server.py
  .env.example
  .env
```

## Run

From the project root:

```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk run patterns/mcp_tools_usage
```

From this folder:

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/mcp_tools_usage
source /Users/vinodv/projects/AI/agents/adk/.venv/bin/activate
adk run .
```

Do not run `adk run agent.py`; ADK expects the directory containing `agent.py`.

## Example Prompts

```text
Search the knowledge base for OAuth setup notes.
```

```text
Get the smoke-test-api runbook.
```

```text
Which local note explains human approval workflows?
```

## Pattern Anatomy

The local MCP server uses `FastMCP`:

```python
mcp = FastMCP("adk-local-knowledge-base")

@mcp.tool(description="Search the local ADK sample knowledge base.")
def knowledge_base_search(query: str) -> dict:
    ...
```

The ADK agent connects with stdio:

```python
toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(MCP_SERVER_SCRIPT)],
        ),
        timeout=10.0,
    ),
    tool_filter=["knowledge_base_search", "get_runbook"],
    tool_name_prefix="kb",
)
```

The model sees the prefixed tools:

```text
kb_knowledge_base_search
kb_get_runbook
```

Use this pattern for tool servers shared across multiple agents, external data tools, local automation tools, or tool contracts that should be tested separately from the agent prompt.
