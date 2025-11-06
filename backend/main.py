from fastapi import FastAPI, HTTPException, Query
from typing import Any, Dict
from app.services import fetch_data,etl
from app.services.api.hotel_api import router as hotel_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

import os
from dotenv import load_dotenv


app = FastAPI(title="TripTreat API")
app.include_router(hotel_router)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

load_dotenv()



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


@app.get("/hotels")
async def list_hotels(
    city: str = Query(..., description="City to search (e.g., 'new york')"),
) -> Dict[str, Any]:
    """
    Fetch all hotel pages for a city and store them in DB.
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Missing API_KEY in environment")

    try:
        data = await fetch_data.fetch_hotels_all(city=city, api_key=API_KEY, api_host=API_HOST)
        etl.save_hotels_to_db(data)
        return {"message": f"Fetched and saved {data['count']} hotels for {city}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Hotel API is running!"}

