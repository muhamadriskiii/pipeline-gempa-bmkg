import os
from dotenv import load_dotenv
from pathlib import Path
import psycopg2

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

def get_conn():
    return psycopg2.connect(
        dbname= "db_gempa",
        user= "postgres",
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("GEMPA_DB_HOST", "localhost"),
    )