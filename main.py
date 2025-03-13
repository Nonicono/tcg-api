from fastapi import FastAPI
import psycopg2
import os

app = FastAPI(
    title="TCG Price Tracker API",
    description="An API for tracking TCG booster box prices and EV calculations",
    version="1.0",
    docs_url="/docs",  # Enable Swagger UI
    redoc_url="/redoc",  # Enable ReDoc UI
    openapi_url="/openapi.json"  # Ensure OpenAPI schema is available
)

# Connect to PostgreSQL using the Render database URL
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.get("/")
def home():
    return {"message": "FastAPI is connected to PostgreSQL!"}
