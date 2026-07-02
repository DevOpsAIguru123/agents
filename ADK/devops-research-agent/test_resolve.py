import asyncio
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

async def main():
    agent = RemoteA2aAgent(name="code_expert", agent_card="http://localhost:8000/.well-known/agent.json")
    try:
        await agent._ensure_resolved()
        print("Success!")
    except Exception as e:
        print("ERROR:", repr(e))

asyncio.run(main())
