import os

from google.adk.agents import Agent
from google.adk.workflow import Workflow


MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")


request_analyzer = Agent(
    name="request_analyzer",
    model=MODEL,
    description="Extracts the important facts and constraints from the request.",
    instruction=(
        "Read the user's request and produce concise request analysis. Capture "
        "the user's goal, constraints, assumptions, and any missing information. "
        "Do not research the topic or answer the user yet."
    ),
    output_key="request_analysis",
)

researcher = Agent(
    name="researcher",
    model=MODEL,
    description="Produces factual research notes for the user's topic.",
    instruction=(
        "Use the request analysis below to produce actual research notes about "
        "the user's topic. Do not stop at request analysis; directly research "
        "the topic using your available knowledge and make the notes useful for "
        "the writer.\n\n"
        "Structure your output with these sections:\n"
        "Actual research notes:\n"
        "- Direct findings: concrete facts, trends, mechanisms, or comparisons "
        "that answer the topic.\n"
        "- Evidence and examples: named examples, dates or timeframes when known, "
        "and why each example matters.\n"
        "- Caveats and uncertainty: limits, competing interpretations, or missing "
        "context.\n"
        "- Sources or verification status: name source types to verify when the "
        "request depends on current information; do not invent sources, links, "
        "or precise recency you cannot verify.\n\n"
        "Do not draft the final answer yet.\n\n"
        "Request analysis:\n{request_analysis}"
    ),
    output_key="research_notes",
)

writer = Agent(
    name="writer",
    model=MODEL,
    description="Drafts a direct answer from the research notes.",
    instruction=(
        "Use the request analysis and research notes below to draft a helpful "
        "answer. Preserve the user's constraints exactly, especially requested "
        "length or format. Be concise, practical, and specific.\n\n"
        "Request analysis:\n{request_analysis}\n\n"
        "Research notes:\n{research_notes}"
    ),
    output_key="draft_answer",
)

reviewer = Agent(
    name="reviewer",
    model=MODEL,
    description="Reviews and tightens the drafted answer before returning it.",
    instruction=(
        "Review the draft answer for clarity, accuracy, usefulness, and fit "
        "with the original constraints. Preserve requested length and format. "
        "Return only the improved final answer.\n\n"
        "Request analysis:\n{request_analysis}\n\n"
        "Research notes:\n{research_notes}\n\n"
        "Draft answer:\n{draft_answer}"
    ),
    output_key="reviewed_answer",
)


root_agent = Workflow(
    name="sequential_answer_pipeline",
    description=(
        "A deterministic graph workflow that runs request analysis, research, "
        "writing, and review in order."
    ),
    edges=[("START", request_analyzer, researcher, writer, reviewer)],
)
