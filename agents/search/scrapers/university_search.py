"""Per-user targeted search: for users who named specific
`target_universities`, search each university for openings matching their
keywords/field of study. Uses Tavily with the university name folded into
the query text rather than domain filtering, since users type free-form
names ("ETH Zurich") rather than domains.

Falls back to Brave (brave_search.py) when Tavily errors — quota exhaustion,
plan restriction, or an outage shouldn't take the whole search run down.
"""

from tavily import TavilyClient

from agents.redact import err
from agents.search.scrapers import brave_search
from agents.search.scrapers.base import RawListing
from agents.search.scrapers.noise_filter import EXCLUDED_DOMAINS
from config import settings

SOURCE_NAME = "university_search"


def search_for_university(
    university: str, keywords: list[str], max_results_per_keyword: int = 3
) -> list[RawListing]:
    try:
        return _search_tavily(university, keywords, max_results_per_keyword)
    except Exception as exc:  # noqa: BLE001 — any Tavily failure falls back, not just known types
        if not settings.BRAVE_API_KEY:
            raise
        print(f"[university_search] falling back to Brave search for '{university}': {err(exc)}")
        return brave_search.search_for_university(university, keywords, max_results_per_keyword)


def _search_tavily(university: str, keywords: list[str], max_results_per_keyword: int) -> list[RawListing]:
    if not settings.TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY not set")

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    listings: list[RawListing] = []
    terms = keywords or [""]

    for keyword in terms:
        query = (
            f'"{university}" {keyword} (PhD OR Masters) '
            f'(open position OR studentship OR "call for applications")'
        ).strip()
        result = client.search(
            query=query, max_results=max_results_per_keyword, exclude_domains=EXCLUDED_DOMAINS
        )

        for item in result.get("results", []):
            listings.append(
                RawListing(
                    title=item.get("title", ""),
                    source_url=item.get("url", ""),
                    source_name=SOURCE_NAME,
                    university=university,
                    snippet=item.get("content", "")[:1000],
                )
            )

    return listings
