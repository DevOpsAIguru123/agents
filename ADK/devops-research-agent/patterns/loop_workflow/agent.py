from google.adk.events.event import Event
from google.adk.workflow import Workflow
from google.genai import types


def initialize_draft(node_input: str) -> Event:
    """Create the first draft and initialize loop state."""
    request = node_input.strip()
    draft = (
        f"For request: {request}\n"
        "1. Send a happy-path request to a representative endpoint.\n"
        "2. Verify the status code, response shape, and one key field."
    )
    return Event(
        message=f"Initialized draft from input:\n{request}\n\n{draft}",
        state={
            "original_request": request,
            "draft": draft,
            "iteration": 1,
        },
    )


def quality_check(iteration: int, draft: str) -> Event:
    """Route to another revision until the bounded loop is complete."""
    if iteration < 2:
        return Event(
            message=(
                f"Quality check iteration {iteration}: draft needs one more "
                "revision for clarity."
            ),
            route="revise",
        )
    return Event(
        message=f"Quality check iteration {iteration}: draft is ready.",
        route="done",
    )


def revise_draft(iteration: int, draft: str) -> Event:
    """Refine the draft and increment the loop counter."""
    revised = (
        f"{draft}\n"
        "Refined: keep the smoke test small, fast, and runnable after every "
        "deploy."
    )
    return Event(
        message=f"Revised draft for iteration {iteration + 1}:\n{revised}",
        state={
            "draft": revised,
            "iteration": iteration + 1,
        },
    )


def final_answer(iteration: int, draft: str) -> types.Content:
    """Return the final refined result."""
    return types.Content(
        role="model",
        parts=[
            types.Part(
                text=f"Final answer after {iteration} iterations:\n{draft}"
            )
        ],
    )


root_agent = Workflow(
    name="loop_refinement_workflow",
    description=(
        "A bounded route-controlled loop that drafts, checks quality, revises, "
        "and exits when complete."
    ),
    edges=[
        (
            "START",
            initialize_draft,
            quality_check,
            {
                "revise": revise_draft,
                "done": final_answer,
            },
        ),
        (revise_draft, quality_check),
    ],
)
