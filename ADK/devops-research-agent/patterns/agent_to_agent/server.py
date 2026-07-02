import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")

# The subagent (specialist) that will be hosted remotely
code_expert = Agent(
    name="code_expert",
    model=MODEL,
    description="An expert software engineer who can write python code.",
    instruction=(
        "You are an expert Python engineer. Provide clear, bug-free code snippets "
        "when requested. Explain your reasoning briefly."
    ),
)

# Convert the Agent to an A2A Starlette application
app = to_a2a(code_expert, host="localhost", port=8000)

if __name__ == "__main__":
    print("Starting A2A server for code_expert on http://127.0.0.1:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
