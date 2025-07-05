import sqlite3
import os

# Set this to the exact path of your database file.
DB_FILE = "/media/pope/projecteo/github_proj/SageScript/chroma_db/chroma.sqlite3"

def inspect_raw_sqlite_file():
    """
    Connects to the chroma.sqlite3 file directly and prints its raw table structure.
    """
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    print(f"--- Raw inspection of SQLite file: '{DB_FILE}' ---")
    
    try:
        # 1. Connect to the SQLite database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 2. Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        if not table_names:
            print("This database file contains no tables.")
            return
            
        print(f"\nFound {len(table_names)} tables: {table_names}")

        # 3. For each table, print its schema and a few sample rows
        for table_name in table_names:
            print("\n" + "="*50)
            print(f"Table Name: '{table_name}'")
            print("="*50)

            # Print schema
            print("--- Schema ---")
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()
            # cid, name, type, notnull, dflt_value, pk
            for column in schema:
                print(f"  - Column: {column[1]} (Type: {column[2]})")

            # Print a few sample rows
            print("\n--- Sample Data (up to 3 rows) ---")
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                if not rows:
                    print("  (Table is empty or contains no data)")
                for i, row in enumerate(rows):
                    print(f"  Row {i+1}: {row}")
            except Exception as e:
                print(f"Could not fetch rows from {table_name}. Error: {e}")


    except sqlite3.Error as e:
        print(f"\nAn SQLite error occurred: {e}")
    finally:
        # 4. Make sure to close the connection
        if 'conn' in locals() and conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    inspect_raw_sqlite_file()