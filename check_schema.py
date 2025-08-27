# check_schema.py
import sqlite3

DB_FILE = 'kazileo.db'

try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"--- Checking schema for '{DB_FILE}' ---")

    cursor.execute("PRAGMA table_info(user_sessions);")
    columns = cursor.fetchall()

    if not columns:
        print("\nERROR: The 'user_sessions' table does not exist.")
    else:
        print("\nColumns found in 'user_sessions' table:")
        print("-" * 30)
        for col in columns:
            print(f"- {col[1]} (Type: {col[2]})")
        print("-" * 30)

    conn.close()

except Exception as e:
    print(f"\nAn error occurred: {e}")