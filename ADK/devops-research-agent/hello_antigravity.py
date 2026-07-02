import asyncio
from google.antigravity import Agent, LocalAgentConfig

async def main():
    # Provide a simple local agent configuration for testing
    async with Agent(LocalAgentConfig()) as agent:
        response = await agent.chat("Hello! Are you the Antigravity SDK?")
        print("Agent response:", await response.text())

if __name__ == "__main__":
    asyncio.run(main())
