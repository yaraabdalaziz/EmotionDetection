import sqlite3

conn = sqlite3.connect('emotion_detection.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    api_key TEXT NOT NULL UNIQUE,
    quota INTEGER DEFAULT 50,
    available_requests INTEGER DEFAULT 50
)
''')

# Create History table
cursor.execute('''
CREATE TABLE IF NOT EXISTS requests_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input TEXT NOT NULL,
    prediction TEXT NOT NULL,
    probability REAL,        
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# Save and close
conn.commit()
conn.close()
