import sqlite3

conn = sqlite3.connect("news.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS news (

id INTEGER PRIMARY KEY AUTOINCREMENT,

title TEXT NOT NULL,

article TEXT NOT NULL,

image TEXT,

video TEXT,

location TEXT,

category TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()

conn.close()

print("Database updated")