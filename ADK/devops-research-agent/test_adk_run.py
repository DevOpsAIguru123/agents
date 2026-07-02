import asyncio
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from patterns.agent_to_agent.agent import root_agent

async def main():
    runner = Runner(
        agent=root_agent, 
        app_name="test",
        session_service=InMemorySessionService(),
        artifact_service=InMemoryArtifactService(),
        memory_service=InMemoryMemoryService()
    )
    session = await runner.session_service.create_session(app_name="test")
    
    async for event in runner.run_async(session_id=session.id, new_message="Can you write a Python function to compute the Fibonacci sequence?"):
        if event.content:
            print(f"CONTENT: {event.content.model_dump_json(indent=2)}")
        if event.tool_calls:
            print("TOOL CALLS issued")
        if event.tool_responses:
            print("TOOL RESPONSES returned")
            
asyncio.run(main())
