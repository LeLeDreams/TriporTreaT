import httpx
from typing import Any, Dict, Union


async def fetch_hotels_all(city: str, api_key: str, api_host: str) -> Dict[str, Any]:
    """
    Fetch ALL hotels for a given city by paging through all API results.
    """
    base_url = "https://tripadvisor-scraper.p.rapidapi.com/hotels/list"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": api_host}

    page = 1
    all_by_id: Dict[Union[int, str], Dict[str, Any]] = {}
    total_pages = None

    async with httpx.AsyncClient(timeout=20.0) as client:
        while True:
            print(f"Fetching page {page} for {city}...")
            params = {"query": city, "page": page}
            resp = await client.get(base_url, headers=headers, params=params)
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
                price_min = pr.get("min")
                price_max = pr.get("max")
                price_avg = (price_min + price_max) / 2 if price_min is not None and price_max is not None else None

                return {
                    "name": h.get("name"),
                    "rating": h.get("rating"),
                    "address": h.get("address"),
                    "price_min": price_min,
                    "price_max": price_max,
                    "price_avg": price_avg,
                    "link": h.get("link"),
                    "lat": h.get("latitude"),
                    "lng": h.get("longitude"),
                }

            for h in results:
                key = coerce_id(h)
                if key is None:
                    continue
                all_by_id[key] = project(h)

            # Stop if last page
            total_pages = payload.get("total_pages") or 1
            if page >= total_pages:
                break
            page += 1

    return {
        "city": city,
        "count": len(all_by_id),
        "by_id": all_by_id,
    }
