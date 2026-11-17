"""Brave Web Search API — fallback for tavily_search/university_search when
Tavily errors (quota, plan restriction, outage). Same RawListing shape, so
callers don't need to know which provider actually served a given run.
"""

from agents.search.scrapers.base import RawListing, scraper_client
from agents.search.scrapers.noise_filter import EXCLUDED_DOMAINS
from config import settings

SOURCE_NAME = "brave"

BASE_URL = "https://api.search.brave.com/res/v1/web/search"


def _headers() -> dict:
    return {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY,
    }


def _search_query(query: str, count: int) -> list[RawListing]:
    if not settings.BRAVE_API_KEY:
        raise RuntimeError("BRAVE_API_KEY not set")

    # No native domain-exclusion param; fold it into the query like Brave's
    # own `-site:` operator expects.
    excluded = " ".join(f"-site:{domain}" for domain in EXCLUDED_DOMAINS)
    full_query = f"{query} {excluded}"

    listings: list[RawListing] = []
    with scraper_client(_headers()) as client:
        resp = client.get(BASE_URL, params={"q": full_query, "count": min(count, 20)})
        if resp.status_code != 200:
            raise RuntimeError(f"Brave search failed (HTTP {resp.status_code})")

        for item in resp.json().get("web", {}).get("results", []):
            listings.append(
                RawListing(
                    title=item.get("title", ""),
                    source_url=item.get("url", ""),
                    source_name=SOURCE_NAME,
                    snippet=item.get("description", "")[:1000],
                )
            )

    return listings


def search(keywords: list[str], max_results_per_keyword: int = 5) -> list[RawListing]:
    listings: list[RawListing] = []
    for keyword in keywords:
        query = (
            f'"{keyword}" (PhD OR MSc) (position OR studentship OR scholarship OR "call for applications")'
        )
        listings.extend(_search_query(query, max_results_per_keyword))
    return listings


def search_for_university(
    university: str, keywords: list[str], max_results_per_keyword: int = 3
) -> list[RawListing]:
    listings: list[RawListing] = []
    terms = keywords or [""]
    for keyword in terms:
        query = (
            f'"{university}" {keyword} (PhD OR Masters) '
            f'(open position OR studentship OR "call for applications")'
        ).strip()
        listings.extend(
            RawListing(
                title=listing.title,
                source_url=listing.source_url,
                source_name=listing.source_name,
                university=university,
                snippet=listing.snippet,
            )
            for listing in _search_query(query, max_results_per_keyword)
        )
    return listings
