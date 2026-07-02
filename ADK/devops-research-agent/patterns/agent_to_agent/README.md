# Agent to Agent (a2a) Protocol Pattern

This pattern demonstrates how to use the Google ADK to have one agent delegate tasks to another using the true **Agent to Agent (A2A) JSON-RPC Protocol** over the network.

## Architecture

*   **`server.py` (Subagent)**: Exposes the `code_expert` subagent as a remote A2A server using `to_a2a` and `uvicorn`.
*   **`agent.py` (Manager)**: Defines the `root_agent` that receives the user's request. It connects to the `code_expert` via the `RemoteA2aAgent` class (using the A2A Agent Card protocol) and wraps it as a tool.

This is a demonstration of remote agent-to-agent delegation. The manager can synthesize the result and interact with the user, while securely delegating to a completely isolated technical coding agent running on a different server process.

## Prerequisites

To run this pattern, your Python environment must have the `a2a` extras installed:
```bash
pip install "google-adk[a2a]"
```

## Setup

```bash
cd /Users/vinodv/projects/AI/agents/adk/patterns/agent_to_agent
cp .env.example .env
```

Edit `.env` with your `GOOGLE_CLOUD_PROJECT`.

## Run

You will need two terminal windows to run this pattern.

**Terminal 1 (Start the A2A Subagent Server):**
```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
python patterns/agent_to_agent/server.py
```
*This will start the remote `code_expert` on `http://127.0.0.1:8000`.*

**Terminal 2 (Start the Manager Agent Client):**
```bash
cd /Users/vinodv/projects/AI/agents/adk
source .venv/bin/activate
adk run patterns/agent_to_agent
```

Example prompt for the Manager:
> Can you write a Python function to compute the Fibonacci sequence?
