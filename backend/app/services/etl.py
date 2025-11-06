import psycopg2
from psycopg2.extras import execute_values
import os

def save_hotels_to_db(data):
    conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

    cur = conn.cursor()

    hotels = []
    for hotel_id, h in data["by_id"].items():
        hotels.append((
            hotel_id,
            data["city"],
            h["name"],
            h["rating"],
            h["address"],
            h["price_min"],
            h["price_max"],
            h["price_avg"],
            h["link"],
            h["lat"],
            h["lng"]
        ))

    query = """
        INSERT INTO hotels (
            id, city, name, rating, address, price_min, price_max, price_avg, link, lat, lng
        ) VALUES %s
        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name,
            rating = EXCLUDED.rating,
            address = EXCLUDED.address,
            price_min = EXCLUDED.price_min,
            price_max = EXCLUDED.price_max,
            price_avg = EXCLUDED.price_avg,
            link = EXCLUDED.link,
            lat = EXCLUDED.lat,
            lng = EXCLUDED.lng;
    """

    execute_values(cur, query, hotels)
    conn.commit()
    cur.close()
    conn.close()
