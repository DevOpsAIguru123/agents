from google.adk import Agent

def main():
    agent = Agent(model="gemini-2.5-flash", name="hello_agent")
    response = agent.run("Hello, ADK!")
    print(f"Agent response: {response.text}")

if __name__ == "__main__":
    main()
