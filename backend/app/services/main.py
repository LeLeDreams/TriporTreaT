from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict, Union
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TripTreat API")

API_KEY = os.getenv("API_KEY")
API_HOST = "tripadvisor-scraper.p.rapidapi.com"


@app.get("/hotels")
async def list_hotels(
    city: str = Query(..., description="City to search (e.g., 'new york')"),
    page: int = Query(1, ge=1, description="Result page number, default 1"),
) -> Dict[str, Any]:
    """Proxy to TripAdvisor scraper. Always return a dict."""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Missing API_KEY in environment")

    url = "https://tripadvisor-scraper.p.rapidapi.com/hotels/list"
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
    params = {"query": city, "page": page}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()

        payload: Union[dict, list] = resp.json()

        # Force top-level dict
        if isinstance(payload, list):
            payload = {"results": payload}
        results: list = []
        if isinstance(payload.get("results"), list):
            results = payload["results"]
        elif isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("results"), list):
            results = payload["data"]["results"]
        elif isinstance(payload.get("items"), list):
            results = payload["items"]
        else:
            results = []

        by_id: Dict[Union[int, str], Dict[str, Any]] = {}

        def coerce_id(h: dict) -> Union[int, str, None]:
            # try several common keys
            cand = (
                h.get("id")
                or h.get("location_id")
                or h.get("hotel_id")
                or h.get("hotelId")
            )
            if cand is None:
                return None
            # normalize to int when possible
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
                continue  # skip items without any usable id
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

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
