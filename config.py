import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST", "aerodatabox.p.rapidapi.com")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "flight_analytics")

AIRPORT_CODES = [
    "AMD", "DEL", "BOM", "BLR", "MAA",
    "HYD", "CCU", "GOI", "COK", "PNQ"
]

DAYS_BACK = 3
