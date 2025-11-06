# api/hotel_api.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db_cursor   # <-- relative import (works when run from backend/)
import psycopg2
import pandas as pd
import os

router = APIRouter()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

API_KEY = os.getenv("API_KEY")

class HotelFilter(BaseModel):
    rating_min: float
    rating_max: float
    price_min: Optional[float] = None
    price_max: Optional[float] = None


@router.post("/hotels/filter")
def filter_hotels(filters: HotelFilter):

    sql = """
        SELECT id, name, rating, address,
               price_min, price_max, price_avg,
               link, lat, lng, city
        FROM hotels
        WHERE rating >= %s AND rating <= %s
    """
    params: list[float | str] = [filters.rating_min, filters.rating_max]

    if filters.price_min is not None:
        sql += " AND price_avg >= %s"
        params.append(filters.price_min)
    if filters.price_max is not None:
        sql += " AND price_avg <= %s"
        params.append(filters.price_max)


    count_sql = "SELECT COUNT(*) FROM hotels WHERE " + sql.split("WHERE", 1)[1]

    sql += " ORDER BY rating DESC, price_avg ASC"


    try:
        with get_db_cursor() as cursor:
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            columns = [
                "id", "name", "rating", "address",
                "price_min", "price_max", "price_avg",
                "link", "lat", "lng", "city"
            ]
            hotels = [dict(zip(columns, row)) for row in rows]

            # Round rating to one decimal place (for the graph)
            for h in hotels:
                h["rating"] = round(h["rating"], 1)

            return {
                "data": hotels,
                "total": total
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/api/hotels")
def get_hotels(
    min_price: float = Query(0),
    max_price: float = Query(10000),
    min_rating: float = Query(0),
    max_rating: float = Query(5)
):
    """
    Return hotels from PostgreSQL filtered by price_avg and rating.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        df = pd.read_sql("""
            SELECT name, rating, price_min, price_max, price_avg
            FROM hotels
            WHERE price_min IS NOT NULL AND price_max IS NOT NULL
        """, conn)
        conn.close()

        filtered_df = df[
            (df['price_avg'] >= min_price) &
            (df['price_avg'] <= max_price) &
            (df['rating'] >= min_rating) &
            (df['rating'] <= max_rating)
        ]

        return filtered_df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
