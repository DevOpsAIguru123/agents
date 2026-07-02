import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")

# Connect to the remote subagent running via the A2A protocol (e.g. from server.py)
code_expert = RemoteA2aAgent(
    name="code_expert",
    agent_card="http://localhost:8000/.well-known/agent.json",
)

root_agent = Agent(
    name="manager",
    model=MODEL,
    description="A technical manager who delegates coding tasks to an expert.",
    instruction=(
        "You are a technical manager. When the user asks you to write code or solve "
        "a coding problem, you MUST call the `code_expert` tool to generate the code. "
        "Once you receive the response from the tool, present the final code directly "
        "to the user. Do NOT reply with 'I will get back to you' or similar phrases—just "
        "output the final result."
    ),
    tools=[AgentTool(agent=code_expert)],
)
