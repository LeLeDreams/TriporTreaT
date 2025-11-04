from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict
from app.services import fetch_data

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TripTreat API")

API_KEY = os.getenv("DAPI_KEY")
API_HOST = "tripadvisor-scraper.p.rapidapi.com"


@app.get("/hotels")
async def list_hotels(
    city: str = Query(..., description="City to search (e.g., 'new york')"),
    page: int = Query(1, ge=1, description="Result page number, default 1"),
) -> Dict[str, Any]:
    """
    Fetch hotels from TripAdvisor scraper using fetchdata.py service.
    Always return a dictionary.
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Missing API_KEY in environment")

    try:
        data = await fetchdata.fetch_hotels(city=city, page=page, api_key=API_KEY, api_host=API_HOST)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
