# services/fetchdata.py
import httpx
from typing import Any, Dict, Union

async def fetch_hotels(city: str, page: int, api_key: str, api_host: str) -> Dict[str, Any]:
    url = "https://tripadvisor-scraper.p.rapidapi.com/hotels/list"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": api_host}
    params = {"query": city, "page": page}

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        payload: Union[dict, list] = resp.json()

    if isinstance(payload, list):
        payload = {"results": payload}

    results: list = []
    if isinstance(payload.get("results"), list):
        results = payload["results"]
    elif isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("results"), list):
        results = payload["data"]["results"]
    elif isinstance(payload.get("items"), list):
        results = payload["items"]

    by_id: Dict[Union[int, str], Dict[str, Any]] = {}

    def coerce_id(h: dict) -> Union[int, str, None]:
        cand = h.get("id") or h.get("location_id") or h.get("hotel_id") or h.get("hotelId")
        if cand is None:
            return None
        try:
            return int(cand)
        except (TypeError, ValueError):
            return str(cand)

    def project(h: dict) -> dict:
        pr = h.get("price_range_usd") or {}
        return {
            "name": h.get("name"),
            "rating": h.get("rating"),
            "address": h.get("address"),
            "price_min": pr.get("min"),
            "price_max": pr.get("max"),
            "link": h.get("link"),
            "lat": h.get("latitude"),
            "lng": h.get("longitude"),
        }

    for h in results:
        key = coerce_id(h)
        if key is None:
            continue
        by_id[key] = project(h)

    return {
        "city": city,
        "page": page,
        "count": len(by_id),
        "ids": list(by_id.keys()),
        "by_id": by_id,
        "meta": {
            "link": payload.get("link"),
            "total_pages": payload.get("total_pages"),
            "current_page": payload.get("current_page"),
            "total_items_count": payload.get("total_items_count"),
            "items_count": payload.get("items_count"),
        },
    }
