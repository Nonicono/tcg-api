from fastapi import FastAPI
import psycopg2
import os
import requests

app = FastAPI(
    title="TCG Price Tracker API",
    description="An API for tracking TCG booster box prices and EV calculations",
    version="1.0",
    docs_url="/docs",  # Manually enable Swagger UI
    redoc_url="/redoc",  # Alternative API docs
    openapi_url="/openapi.json"  # Ensure OpenAPI schema is available
)

# Get environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
CARD_KINGDOM_API_KEY = os.getenv("CARD_KINGDOM_API_KEY")

# Connect to PostgreSQL
if DATABASE_URL:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
else:
    raise ValueError("DATABASE_URL is not set!")

# Function to create the booster box price tracking table
def create_price_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booster_box_prices (
            id SERIAL PRIMARY KEY,
            set_name TEXT NOT NULL,
            booster_box_name TEXT NOT NULL,
            current_price DECIMAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# Function to create the card price tracking table
def create_card_price_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_prices (
            id SERIAL PRIMARY KEY,
            set_name TEXT NOT NULL,
            card_name TEXT NOT NULL UNIQUE,
            current_price DECIMAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# Create tables when the app starts
create_price_table()
create_card_price_table()

# Function to fetch card prices from Card Kingdom API
def fetch_card_kingdom_price(card_name):
    url = f"https://api.cardkingdom.com/v1/prices?name={card_name}"
    headers = {"Authorization": f"Bearer {CARD_KINGDOM_API_KEY}"}

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if "prices" in data and len(data["prices"]) > 0:
            return float(data["prices"][0]["market_price"])  # Adjust key if needed
    return None

# Function to store card prices in PostgreSQL
def update_card_price(set_name, card_name):
    price = fetch_card_kingdom_price(card_name)
    
    if isinstance(price, float):
        cursor.execute("""
            INSERT INTO card_prices (set_name, card_name, current_price)
            VALUES (%s, %s, %s)
            ON CONFLICT (card_name) 
            DO UPDATE SET current_price = EXCLUDED.current_price, last_updated = CURRENT_TIMESTAMP
        """, (set_name, card_name, price))
        conn.commit()
        return {"message": f"Updated {card_name} price: ${price}"}
    
    return {"error": "Price not found"}

# API route to fetch & store card prices from Card Kingdom API
@app.get("/fetch-card-price/{set_name}/{card_name}")
def fetch_card_price_route(set_name: str, card_name: str):
    return update_card_price(set_name, card_name)

# Home endpoint
@app.get("/")
def home():
    return {"message": "FastAPI is connected to PostgreSQL!"}
