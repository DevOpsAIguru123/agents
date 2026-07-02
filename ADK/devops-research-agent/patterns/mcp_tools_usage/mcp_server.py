import re

from mcp.server.fastmcp import FastMCP


KNOWLEDGE_BASE = {
    "gemini-oauth-adk": {
        "title": "Gemini OAuth setup for ADK",
        "summary": (
            "Use Google Cloud Application Default Credentials, enable Vertex "
            "AI, and avoid setting GOOGLE_API_KEY for this OAuth sample."
        ),
        "tags": ["adk", "gemini", "oauth", "vertex-ai"],
        "steps": [
            "gcloud auth application-default login",
            "gcloud auth application-default set-quota-project YOUR_PROJECT_ID",
            "gcloud services enable aiplatform.googleapis.com --project YOUR_PROJECT_ID",
        ],
    },
    "smoke-test-api": {
        "title": "Two-step API smoke test",
        "summary": (
            "Keep smoke tests small: call one representative endpoint, then "
            "verify status code, shape, and one critical field."
        ),
        "tags": ["testing", "api", "smoke-test"],
        "steps": [
            "Send a happy-path request to the representative endpoint.",
            "Verify the status code, response schema, and one key field.",
        ],
    },
    "human-approval": {
        "title": "Human approval workflow",
        "summary": (
            "Pause with RequestInput, resume the approval node, then route "
            "approved and rejected decisions with Event(route=...)."
        ),
        "tags": ["adk", "human-in-the-loop", "approval"],
        "steps": [
            "Return RequestInput when resume input is missing.",
            "Use rerun_on_resume=True so the node sees ctx.resume_inputs.",
            "Return Event(route='approved') or Event(route='rejected').",
        ],
    },
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "me",
    "note",
    "notes",
    "of",
    "on",
    "search",
    "the",
    "to",
}


mcp = FastMCP(
    "adk-local-knowledge-base",
    instructions=(
        "A tiny local MCP server that exposes ADK sample notes as tools."
    ),
)


def _searchable_text(entry: dict) -> str:
    return " ".join(
        [
            entry["title"],
            entry["summary"],
            " ".join(entry["tags"]),
            " ".join(entry["steps"]),
        ]
    ).lower()


def _query_tokens(query: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", query.lower())
        if token not in STOP_WORDS
    ]


def _match_score(query: str, entry: dict) -> int:
    searchable_text = _searchable_text(entry)
    if query.lower() in searchable_text:
        return len(query) + 100

    return sum(1 for token in _query_tokens(query) if token in searchable_text)


@mcp.tool(description="Search the local ADK sample knowledge base.")
def knowledge_base_search(query: str) -> dict:
    matches = []
    for slug, entry in KNOWLEDGE_BASE.items():
        score = _match_score(query, entry)
        if score:
            matches.append(
                {
                    "slug": slug,
                    "title": entry["title"],
                    "summary": entry["summary"],
                    "tags": entry["tags"],
                    "score": score,
                }
            )

    matches.sort(key=lambda match: match["score"], reverse=True)

    return {
        "query": query,
        "matches": matches,
    }


@mcp.tool(description="Fetch a runbook by slug from the local knowledge base.")
def get_runbook(slug: str) -> dict:
    entry = KNOWLEDGE_BASE.get(slug)
    if entry is None:
        return {
            "status": "not_found",
            "slug": slug,
            "available_slugs": sorted(KNOWLEDGE_BASE),
        }

    return {
        "status": "ok",
        "slug": slug,
        **entry,
    }


if __name__ == "__main__":
    mcp.run("stdio")
