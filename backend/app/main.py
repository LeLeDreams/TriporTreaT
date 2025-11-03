from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import os
from dotenv import load_dotenv
from app.db import models
from app.db.models import Item
from app.db.database import SessionLocal, engine, Base
import requests

from fastapi import FastAPI, Depends
from app.services.fetch_data import fetch_data_from_api, save_data_to_db
from pydantic import BaseModel

load_dotenv()  

DATABASE_URL = os.getenv("DATABASE_URL", "xxx")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables
Base.metadata.create_all(bind=engine)


def fetch_data_from_api():
    url = "https://api.example.com/data"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Returns JSON list/dict
    return []

def save_data_to_db(items):
    db: Session = SessionLocal()
    for i in items:
        item = Item(name=i["name"], description=i.get("description", ""))
        db.add(item)
    db.commit()
    db.close()


app = FastAPI()

@app.get("/fetch-and-store")
def fetch_and_store():
    data = fetch_data_from_api()
    if not data:
        return {"message": "No data fetched"}
    save_data_to_db(data)
    return {"message": f"Saved {len(data)} items to the database"}


class ItemSchema(BaseModel):
    name: str
    description: str | None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()