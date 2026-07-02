import os

from google.adk.agents import Agent
from google.adk.events.event import Event
from google.adk.workflow import DEFAULT_ROUTE, Workflow


MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")


def route_request(node_input: str) -> Event:
    """Route the user request to the best specialist branch."""
    request = node_input.lower()
    math_terms = [
        "add",
        "sum",
        "subtract",
        "minus",
        "multiply",
        "divide",
        "calculate",
        "percent",
    ]
    writing_terms = [
        "write",
        "draft",
        "email",
        "rewrite",
        "summarize",
        "message",
        "copy",
    ]

    if any(term in request for term in math_terms):
        route = "math"
    elif any(term in request for term in writing_terms):
        route = "writing"
    else:
        route = "general"

    return Event(route=route, state={"original_request": node_input})


math_specialist = Agent(
    name="math_specialist",
    model=MODEL,
    description="Handles arithmetic and calculation-style requests.",
    instruction=(
        "Answer the user's math or calculation request. Show the key equation "
        "briefly, then give the result.\n\n"
        "dont not include dollar signs or currency symbols in your answer. If the user asks for a " 
        "Original request:\n{original_request}"
    ),
)

writing_specialist = Agent(
    name="writing_specialist",
    model=MODEL,
    description="Handles writing, rewriting, and summarization requests.",
    instruction=(
        "Answer the user's writing request. Produce polished, concise text and "
        "avoid extra explanation unless it is needed.\n\n"
        "Original request:\n{original_request}"
    ),
)

general_specialist = Agent(
    name="general_specialist",
    model=MODEL,
    description="Handles requests that do not match a specific specialist.",
    instruction=(
        "Answer the user's request directly and concisely.\n\n"
        "Original request:\n{original_request}"
    ),
)


root_agent = Workflow(
    name="conditional_routing_workflow",
    description=(
        "A routing workflow that sends the request to a specialist branch based "
        "on a deterministic route function."
    ),
    edges=[
        (
            "START",
            route_request,
            {
                "math": math_specialist,
                "writing": writing_specialist,
                DEFAULT_ROUTE: general_specialist,
            },
        )
    ],
)
