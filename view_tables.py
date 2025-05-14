import sqlite3

# Connect to the database
conn = sqlite3.connect('crypto_wallet.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT * FROM sqlite_master;")
tables = cursor.fetchall()

print("\nDatabase contents:")
print("------------------")
for table in tables:
    print(f"\nType: {table[0]}")
    print(f"Name: {table[1]}")
    print(f"SQL: {table[4]}")

conn.close() 