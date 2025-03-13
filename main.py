from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

# Connect to PostgreSQL using the Render database URL
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.get("/")
def home():
    return {"message": "FastAPI is connected to PostgreSQL!"}
