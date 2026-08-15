import sqlite3
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database folder
DATA_DIR = BASE_DIR / "data"

# Create data folder if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Database file
DB_PATH = DATA_DIR / "businesses.db"


def get_connection():
    """
    Returns a SQLite connection.
    """
    return sqlite3.connect(DB_PATH)


def create_tables():
    """
    Creates the businesses table if it doesn't exist, and adds
    any new columns that older databases might be missing.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT,

            phone TEXT,

            website TEXT,

            rating REAL,

            reviews INTEGER,

            address TEXT,

            maps_url TEXT UNIQUE,

            contacted INTEGER DEFAULT 0,

            interested INTEGER DEFAULT 0,

            website_delivered INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # Migration: add whatsapp_failed column if it doesn't exist yet
    # (older databases created before this feature won't have it).
    cursor.execute("PRAGMA table_info(businesses)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "whatsapp_failed" not in existing_columns:
        cursor.execute(
            "ALTER TABLE businesses ADD COLUMN whatsapp_failed INTEGER DEFAULT 0"
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("✅ Database created successfully.")
