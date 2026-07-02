from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.workflow import Workflow, node
from google.genai import types


APPROVAL_INTERRUPT_ID = "human_approval"


def _content(text: str) -> types.Content:
    return types.Content(role="model", parts=[types.Part(text=text)])


def parse_approval_response(response: dict) -> dict:
    """Normalize approval responses from ADK Web or direct tests."""
    if (
        isinstance(response, dict)
        and isinstance(response.get("result"), dict)
    ):
        response = response["result"]

    response = response or {}
    feedback = str(response.get("feedback", "")).strip()
    return {
        "approved": bool(response.get("approved", False)),
        "feedback": feedback,
    }


def draft_response(node_input: str) -> Event:
    """Create a draft and store it for human review."""
    request = node_input.strip()
    draft = (
        f"Draft response for request: {request}\n"
        "Proposed action: prepare and share this response after human approval."
    )

    return Event(
        message=f"Draft prepared for human review:\n{draft}",
        state={
            "original_request": request,
            "draft": draft,
        },
    )


def request_human_approval(ctx, draft: str):
    """Pause the workflow until a human approves or rejects the draft."""
    if not ctx.resume_inputs:
        return RequestInput(
            interrupt_id=APPROVAL_INTERRUPT_ID,
            message=(
                "Approve this draft? Respond with approved=true/false and "
                "optional feedback."
            ),
            payload={"draft": draft},
            response_schema={
                "type": "object",
                "properties": {
                    "approved": {"type": "boolean"},
                    "feedback": {"type": "string"},
                },
                "required": ["approved"],
            },
        )

    raw_response = ctx.resume_inputs.get(APPROVAL_INTERRUPT_ID)
    if raw_response is None:
        raw_response = next(iter(ctx.resume_inputs.values()))

    decision = parse_approval_response(raw_response)
    route = "approved" if decision["approved"] else "rejected"

    return Event(
        message=(
            f"Human decision: {route}. "
            f"Feedback: {decision['feedback'] or '(none)'}"
        ),
        route=route,
        state={
            "approval_decision": route,
            "approval_feedback": decision["feedback"],
        },
    )


approval_node = node(
    request_human_approval,
    name="request_human_approval",
    rerun_on_resume=True,
)


def publish_response(
    draft: str,
    approval_decision: str,
    approval_feedback: str = "",
) -> types.Content:
    """Return the approved final response."""
    feedback_line = (
        f"\nHuman feedback: {approval_feedback}" if approval_feedback else ""
    )
    return _content(
        f"Approved by human. Publishing response:\n{draft}{feedback_line}"
    )


def revise_after_rejection(
    draft: str,
    approval_feedback: str = "",
) -> types.Content:
    """Return the rejected draft with revision guidance."""
    feedback = approval_feedback or "No specific feedback was provided."
    return _content(
        "Human requested changes. Revised draft is not published yet.\n"
        f"Feedback: {feedback}\n\n"
        f"Draft to revise:\n{draft}"
    )


root_agent = Workflow(
    name="human_approval_workflow",
    description=(
        "Drafts a response, pauses for human approval, then publishes or "
        "returns revision guidance."
    ),
    edges=[
        (
            "START",
            draft_response,
            approval_node,
            {
                "approved": publish_response,
                "rejected": revise_after_rejection,
            },
        )
    ],
)
