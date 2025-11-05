from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict
from app.services import fetch_data,etl
from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="TripTreat API")

origins = [
    "http://localhost",
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # you can use ["*"] for all origins during local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_KEY = os.getenv("API_KEY")
API_HOST = "tripadvisor-scraper.p.rapidapi.com"

print("API_KEY loaded:", API_KEY)



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
        data = await fetch_data.fetch_hotels(city=city, page=page, api_key=API_KEY, api_host=API_HOST)
        etl.save_hotels_to_db(data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
