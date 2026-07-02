import asyncio
from google.adk.runners import Runner
from patterns.agent_to_agent.agent import root_agent

async def main():
    runner = Runner(agent=root_agent, app_name="test")
    session = await runner.session_service.create_session(app_name="test")
    
    async for event in runner.run_async(session_id=session.id, new_message="Can you write a Python function to compute the Fibonacci sequence?"):
        print(f"EVENT: {event.model_dump_json(indent=2)}")
        
asyncio.run(main())
