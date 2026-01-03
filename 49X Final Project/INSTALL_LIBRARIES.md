# Installation Guide for Database Libraries

## Quick Installation

### Option 1: Using pip (Recommended)
```bash
pip install -r requirements.txt
```

### Option 2: Using Python module
```bash
python -m pip install -r requirements.txt
```

### Option 3: Using Python Launcher (Windows)
```bash
py -m pip install -r requirements.txt
```

## Required Libraries for Database Operations

The main libraries needed to open and work with the `.db` files are:

1. **sqlite3** - Built-in to Python (no installation needed)
2. **pandas** - For data manipulation and reading SQLite databases
3. **sqlalchemy** - For advanced database operations (optional but recommended)

### Minimal Installation (Just for Database Viewing)
```bash
pip install pandas
```

### Full Installation (All Project Dependencies)
```bash
pip install -r requirements.txt
```

## Using the Database Viewer

After installing the libraries, you can view all databases using:

```bash
python view_database.py
```

Or:
```bash
py view_database.py
```

## Manual Database Viewing

If you prefer to view databases manually, you can use:

### Using Python Interactive Shell
```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('Data/corpus.db')

# Read into pandas DataFrame
df = pd.read_sql_query("SELECT * FROM articles LIMIT 10;", conn)
print(df)

# Close connection
conn.close()
```

### Using SQLite Command Line Tool
If you have SQLite installed:
```bash
sqlite3 "Data/corpus.db"
.tables
SELECT * FROM articles LIMIT 10;
.quit
```

### Using DB Browser for SQLite (GUI Tool)
Download from: https://sqlitebrowser.org/
- Free, open-source GUI tool
- Easy to browse and edit SQLite databases
- No Python installation needed

