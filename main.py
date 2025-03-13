from fastapi import FastAPI
import psycopg2
import os

app = FastAPI(
    title="TCG Price Tracker API",
    description="An API for tracking TCG booster box prices and EV calculations",
    version="1.0",
    docs_url="/docs",  # Manually enable Swagger UI
    redoc_url="/redoc",  # Alternative API docs
    openapi_url="/openapi.json"  # Ensure OpenAPI schema is available
)

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
if DATABASE_URL:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
else:
    raise ValueError("DATABASE_URL is not set!")

# Function to create the price tracking table
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

# Call the function to create the table when the app starts
create_price_table()

@app.get("/")
def home():
    return {"message": "FastAPI is connected to PostgreSQL!"}
