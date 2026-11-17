"""Tavily web search — catch-all for sources not covered by a dedicated
scraper (professor lab pages, niche portals, unlisted openings). Also the
first step in the Phase 3 research lab discovery loop.

Falls back to Brave (brave_search.py) when Tavily errors — quota exhaustion,
plan restriction, or an outage shouldn't take the whole search run down.
"""

from tavily import TavilyClient

from agents.redact import err
from agents.search.scrapers import brave_search
from agents.search.scrapers.base import RawListing
from agents.search.scrapers.noise_filter import EXCLUDED_DOMAINS
from config import settings

SOURCE_NAME = "tavily"


def search(keywords: list[str], max_results_per_keyword: int = 5) -> list[RawListing]:
    try:
        return _search_tavily(keywords, max_results_per_keyword)
    except Exception as exc:  # noqa: BLE001 — any Tavily failure falls back, not just known types
        if not settings.BRAVE_API_KEY:
            raise
        print(f"[tavily] falling back to Brave search: {err(exc)}")
        return brave_search.search(keywords, max_results_per_keyword)


def _search_tavily(keywords: list[str], max_results_per_keyword: int) -> list[RawListing]:
    if not settings.TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY not set")

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    listings: list[RawListing] = []

    for keyword in keywords:
        query = (
            f'"{keyword}" (PhD OR MSc) (position OR studentship OR scholarship OR "call for applications")'
        )
        result = client.search(
            query=query, max_results=max_results_per_keyword, exclude_domains=EXCLUDED_DOMAINS
        )

        for item in result.get("results", []):
            listings.append(
                RawListing(
                    title=item.get("title", ""),
                    source_url=item.get("url", ""),
                    source_name=SOURCE_NAME,
                    snippet=item.get("content", "")[:1000],
                )
            )

    return listings
