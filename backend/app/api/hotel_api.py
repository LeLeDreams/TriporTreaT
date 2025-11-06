# api/hotel_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..db.database import get_db_cursor   # <-- relative import (works when run from backend/)

router = APIRouter()


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