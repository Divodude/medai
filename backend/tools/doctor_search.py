"""
DuckDuckGo-powered doctor search tool.
No API key required — uses the duckduckgo_search package.
Includes fallback to state-level search for small/rural cities.
"""
import re
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Map of small Indian cities/towns to their parent state for broader searches
INDIA_CITY_STATE = {
    "una": "Himachal Pradesh",
    "bilaspur": "Himachal Pradesh",
    "hamirpur": "Himachal Pradesh",
    "kangra": "Himachal Pradesh",
    "mandi": "Himachal Pradesh",
    "kullu": "Himachal Pradesh",
    "chamba": "Himachal Pradesh",
    "sirmaur": "Himachal Pradesh",
    "solan": "Himachal Pradesh",
}


def _run_ddg_query(query: str, max_results: int) -> list[dict]:
    """Execute a single DuckDuckGo text search and parse results."""
    results = []
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results * 2))

        for item in raw:
            title = item.get("title", "").strip()
            body = item.get("body", "").strip()
            href = item.get("href", "")

            if not title or len(title) < 5:
                continue

            # Skip obvious portal/directory pages (not individual doctors)
            skip_keywords = ["find doctors", "search doctors", "list of", "top 10", "best doctors in", "how to find"]
            if any(kw in title.lower() for kw in skip_keywords):
                continue

            phone_match = re.search(r"[\+\(]?[\d\s\-\(\)]{7,15}", body)
            phone = phone_match.group(0).strip() if phone_match else None

            results.append({
                "title": title[:80],
                "body": body[:200],
                "href": href,
                "phone": phone,
            })

            if len(results) >= max_results:
                break
    except Exception as e:
        logger.error(f"DuckDuckGo search failed for query '{query}': {e}")

    return results


def search_doctors(specialty: str, city: str, max_results: int = 5) -> list[dict]:
    """
    Search for nearby doctors of a given specialty.
    Falls back to state/region-level if city search yields too few results.

    Returns a list of dicts with keys:
        name, specialty, address, phone, rating, maps_link, source_url
    """
    city = (city or "").strip()
    specialty = (specialty or "General Medicine").strip()

    # Build search queries (primary + fallback)
    queries = []
    if city:
        queries.append(f"best {specialty} doctor clinic in {city} India")
        queries.append(f"{specialty} doctor hospital {city}")

        # State-level fallback for small cities
        state = INDIA_CITY_STATE.get(city.lower())
        if state:
            queries.append(f"best {specialty} doctor in {state} India near {city}")
    else:
        queries.append(f"best {specialty} doctor near me India")

    all_raw = []
    for query in queries:
        raw = _run_ddg_query(query, max_results)
        all_raw.extend(raw)
        if len(all_raw) >= max_results:
            break

    # De-duplicate by title
    seen_titles = set()
    doctors = []
    for item in all_raw:
        if item["title"] in seen_titles:
            continue
        seen_titles.add(item["title"])

        maps_query = f"{item['title']} {city} India".replace(" ", "+")
        maps_link = f"https://www.google.com/maps/search/?api=1&query={maps_query}"

        doctors.append({
            "name": item["title"],
            "specialty": specialty,
            "address": city or "Location not specified",
            "phone": item["phone"],
            "rating": None,
            "maps_link": maps_link,
            "source_url": item["href"],
            "description": item["body"],
        })

    return doctors[:max_results]
