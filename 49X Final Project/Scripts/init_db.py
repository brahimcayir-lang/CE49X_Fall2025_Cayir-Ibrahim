import sqlite3
import os

# Define the path to the database
# This ensures it always finds the 'data' folder relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'corpus.db')


def init_db():
    """
    Creates the SQLite database and the 'articles' table.
    """
    # 1. Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # 2. Connect to the database (this creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 3. Create the table
    # We use 'IF NOT EXISTS' so you can run this script multiple times safely.
    # The 'UNIQUE(url)' constraint is critical: it prevents duplicate articles.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        publication_date TEXT,
        source_domain TEXT,
        url TEXT UNIQUE,
        full_text TEXT,
        search_keywords TEXT,
        category_tag TEXT
    );
    """

    cursor.execute(create_table_query)

    conn.commit()
    conn.close()

    print(f"✅ Database initialized successfully at: {DB_PATH}")
    print("   Table 'articles' is ready.")


if __name__ == "__main__":
    init_db()