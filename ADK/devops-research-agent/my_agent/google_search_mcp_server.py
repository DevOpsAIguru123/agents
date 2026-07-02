import email.utils
import html
import urllib.parse
import xml.etree.ElementTree as ET

import requests
from mcp.server.fastmcp import FastMCP


DEFAULT_LANGUAGE = "en-US"
DEFAULT_REGION = "US"
DEFAULT_LIMIT = 10


mcp = FastMCP(
    "adk-google-search",
    instructions=(
        "Searches Google News RSS and returns current source metadata for "
        "research and news queries."
    ),
)


def _normalise_region(region: str | None) -> str:
    if not region:
        return DEFAULT_REGION
    if region.lower() == "com":
        return "US"
    return region.upper()


def _normalise_language(language: str | None) -> str:
    return language or DEFAULT_LANGUAGE


def _build_url(query: str, language: str, region: str) -> str:
    params = {
        "q": query,
        "hl": language,
        "gl": region,
        "ceid": f"{region}:en",
    }
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)


def _parse_pub_date(value: str | None) -> str | None:
    if not value:
        return None
    parsed = email.utils.parsedate_to_datetime(value)
    return parsed.isoformat()


@mcp.tool(description="Search Google News for current web/news results.")
def search(
    query: str,
    limit: int = DEFAULT_LIMIT,
    timeout: int = 30000,
    language: str = DEFAULT_LANGUAGE,
    region: str = DEFAULT_REGION,
) -> dict:
    region = _normalise_region(region)
    language = _normalise_language(language)
    bounded_limit = max(1, min(int(limit or DEFAULT_LIMIT), 20))
    timeout_seconds = max(1, min(float(timeout or 30000) / 1000, 60))
    url = _build_url(query, language, region)

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 ADK local research agent"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall("./channel/item")
    results = []
    for item in items[:bounded_limit]:
        title = html.unescape(item.findtext("title", default="")).strip()
        link = item.findtext("link", default="").strip()
        source = item.find("source")
        results.append(
            {
                "title": title,
                "url": link,
                "source": html.unescape(source.text).strip() if source is not None and source.text else None,
                "published_at": _parse_pub_date(item.findtext("pubDate")),
                "snippet": html.unescape(item.findtext("description", default="")).strip(),
            }
        )

    return {
        "query": query,
        "results": results,
        "language": language,
        "region": region,
        "source": "Google News RSS",
    }


if __name__ == "__main__":
    mcp.run("stdio")
