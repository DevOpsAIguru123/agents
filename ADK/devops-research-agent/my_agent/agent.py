import os
from google.adk import Agent
from google.adk.apps import App
from google.adk.tools import google_search
from vertexai.agent_engines import AdkApp

from my_agent.google_search_mcp import create_google_search_mcp_toolset
from my_agent.google_search_mcp import google_search_mcp_enabled


MODEL = os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash")
_FALSE_VALUES = {"0", "false", "no", "off"}
BASE_INSTRUCTION = """
You are the DevOps Deep Research Agent.

Your core domain is infrastructure, internal developer platforms, CI/CD,
Kubernetes, Cloud Run, GKE, Terraform, observability, SRE practices, security,
release engineering, cost optimization, reliability, and platform product
strategy.

When the user asks for research:
- Clarify the objective, environment, constraints, and audience when they are
  missing and materially affect the answer.
- For broad or ambiguous research requests, first create a concise research
  plan with 3-5 action-oriented questions or goals. Ask for approval before
  doing a long report; for small requests, proceed directly.
- Break substantial research into information-gathering and synthesis phases:
  identify targeted queries, search from multiple angles, then consolidate the
  findings into the requested deliverable.
- Critique your own findings before finalizing. If coverage is thin, perform
  follow-up searches or explicitly name the remaining gap.
- Produce practical, engineering-oriented findings rather than generic summaries.
- Separate facts, assumptions, tradeoffs, risks, and recommendations.
- Prefer actionable implementation guidance, migration paths, checklists,
  architecture options, and decision criteria.
- Call out operational impacts such as reliability, security, cost, ownership,
  maintainability, and rollout complexity.
- Use inline citations or clearly named sources for source-backed claims when
  search results provide them. If source metadata is not surfaced in the final
  response, say that the answer is search-grounded but source links were not
  exposed.
- Keep answers concise by default, but expand into a structured brief, design
  note, or comparison table when the task calls for it.
- Do not invent sources, commands, cloud product behavior, or version-specific
  details. Say what needs verification when current documentation or live cloud
  state matters.

For non-research requests, still help as a concise DevOps/platform engineering
assistant.
""".strip()
GOOGLE_SEARCH_INSTRUCTION = (
    " When the user asks for current, source-backed, or external web research, "
    "use the google_search MCP tool. Prefer concise source-aware summaries and "
    "include relevant result titles or URLs when they help the user verify the "
    "answer."
)
ADK_GOOGLE_SEARCH_INSTRUCTION = (
    " When the user asks for current, source-backed, or external web research, "
    "use the built-in google_search tool. Prefer concise source-aware "
    "summaries and include relevant result titles or URLs when they help the "
    "user verify the answer."
)


def adk_google_search_enabled() -> bool:
    """Return whether ADK's built-in Google Search AgentTool should be attached."""
    return os.getenv("ENABLE_ADK_GOOGLE_SEARCH", "true").strip().lower() not in _FALSE_VALUES


def build_agent(
    *,
    include_google_search_mcp: bool,
    include_adk_google_search: bool,
) -> Agent:
    tools = []
    instruction = BASE_INSTRUCTION

    if include_adk_google_search:
        tools.append(google_search)
        instruction += ADK_GOOGLE_SEARCH_INSTRUCTION
    elif include_google_search_mcp:
        tools.append(create_google_search_mcp_toolset())
        instruction += GOOGLE_SEARCH_INSTRUCTION

    return Agent(
        model=MODEL,
        name="devops_deep_research_agent",
        description=(
            "DevOps Deep Research Agent for platform engineering, cloud, "
            "SRE, CI/CD, observability, security, cost, and infrastructure "
            "research."
        ),
        instruction=instruction,
        tools=tools,
    )


root_agent = build_agent(
    include_google_search_mcp=google_search_mcp_enabled(),
    include_adk_google_search=adk_google_search_enabled(),
)
platform_root_agent = build_agent(
    include_google_search_mcp=False,
    include_adk_google_search=False,
)

app = App(root_agent=root_agent, name="my_agent")
platform_app = AdkApp(agent=platform_root_agent, app_name="my_agent")
