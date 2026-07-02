import os

from google.adk.agents import Agent
from google.adk.workflow import JoinNode, Workflow


MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")


benefits_reviewer = Agent(
    name="benefits_reviewer",
    model=MODEL,
    description="Reviews a proposal for benefits, upside, and strengths.",
    instruction=(
        "Analyze the user's proposal only for benefits, upside, and strengths. "
        "Return 2 to 4 concise bullets. Do not discuss risks except when needed "
        "to clarify a benefit."
    ),
    output_key="benefits_review",
)

risks_reviewer = Agent(
    name="risks_reviewer",
    model=MODEL,
    description="Reviews a proposal for risks, downsides, and missing checks.",
    instruction=(
        "Analyze the user's proposal only for risks, downsides, and missing "
        "checks. Return 2 to 4 concise bullets. Do not recommend a final "
        "decision yet."
    ),
    output_key="risks_review",
)

join_reviews = JoinNode(name="join_reviews")

synthesizer = Agent(
    name="synthesizer",
    model=MODEL,
    description="Combines parallel reviews into a short final recommendation.",
    instruction=(
        "Combine the benefits review and risks review into a balanced final "
        "recommendation. Use this structure:\n"
        "- Recommendation: one sentence.\n"
        "- Why: 2 bullets.\n"
        "- Watch-outs: 2 bullets.\n\n"
        "Benefits review:\n{benefits_review}\n\n"
        "Risks review:\n{risks_review}"
    ),
    output_key="final_recommendation",
)


root_agent = Workflow(
    name="parallel_review_workflow",
    description=(
        "A fan-out/fan-in workflow that reviews benefits and risks in parallel, "
        "then joins both branches for synthesis."
    ),
    edges=[
        (
            "START",
            (benefits_reviewer, risks_reviewer),
            join_reviews,
            synthesizer,
        )
    ],
)

