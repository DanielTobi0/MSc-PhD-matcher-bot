"""Every scraper that shares the plain `search(keywords) -> list[RawListing]`
signature, so the search agent can loop over them generically instead of
hardcoding each call. Tavily (different
result shape / used as an explicit catch-all) are wired separately in
agents/search/tools.py.
"""

from agents.search.scrapers import (
    daad,
    erasmus_mundus,
    euraxess,
    fulbright,
    phdportal,
    profellow,
    universitypositions,
)

GLOBAL_KEYWORD_SCRAPERS = {
    "phdportal": phdportal.search,
    "universitypositions": universitypositions.search,
    "euraxess": euraxess.search,
    "erasmus_mundus": erasmus_mundus.search,
    "profellow": profellow.search,
    "daad": daad.search,
    "fulbright": fulbright.search,
}
