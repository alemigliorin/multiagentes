import sqlite3
conn = sqlite3.connect('tmp/storage.db')
cur = conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
for row in cur.fetchall():
    print(f"Table: {row[0]}")
    print(row[1])
    print("-" * 40)
