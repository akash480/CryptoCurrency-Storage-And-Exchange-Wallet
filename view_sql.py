import sqlite3
import os

def execute_sql_query(query, table_name):
    print(f"\n=== {table_name.upper()} TABLE ===")
    print(f"SQL Query: {query}")
    print("-" * 50)
    
    # Check if database file exists
    if not os.path.exists('crypto_wallet.db'):
        print("Error: Database file 'crypto_wallet.db' not found!")
        print("Please run the Flask application first to create the database.")
        return
    
    conn = sqlite3.connect('crypto_wallet.db')
    cursor = conn.cursor()
    
    try:
        # First, let's get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nAvailable tables in database:")
        for table in tables:
            print(f"- {table[0]}")
        print("-" * 50)
        
        # Now execute the query
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Print column names
        print("Columns:", ", ".join(columns))
        print(f"\nNumber of records: {len(rows)}")
        print("\nData:")
        
        # Print each row
        for row in rows:
            print("-" * 50)
            for col_name, value in zip(columns, row):
                print(f"{col_name}: {value}")
                
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# SQL queries for each table
queries = {
    "user": "SELECT * FROM user",
    "wallet": "SELECT * FROM wallet",
    "transaction": "SELECT * FROM transaction"
}

# Execute each query
for table, query in queries.items():
    execute_sql_query(query, table) 