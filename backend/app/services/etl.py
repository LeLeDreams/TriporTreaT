from app.db.database import get_connection

def save_hotels_to_db(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    by_id = data.get("by_id", {})
    city = data.get("city")
    page = data.get("page")

    for hotel_id, info in by_id.items():
        cur.execute(
            """
            INSERT INTO hotels (id, name, rating, address, price_min, price_max, link, lat, lng, city, page)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                rating = EXCLUDED.rating,
                address = EXCLUDED.address,
                price_min = EXCLUDED.price_min,
                price_max = EXCLUDED.price_max,
                link = EXCLUDED.link,
                lat = EXCLUDED.lat,
                lng = EXCLUDED.lng,
                city = EXCLUDED.city,
                page = EXCLUDED.page;
            """,
            (
                hotel_id,
                info.get("name"),
                info.get("rating"),
                info.get("address"),
                info.get("price_min"),
                info.get("price_max"),
                info.get("link"),
                info.get("lat"),
                info.get("lng"),
                city,
                page,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
