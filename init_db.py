import os
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Opret nødvendige tabeller
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    membership_number TEXT,
    is_admin INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pairing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    male_id TEXT NOT NULL,
    female_id TEXT NOT NULL,
    pairing_date DATE NOT NULL,
    expected_due_date DATE NOT NULL,
    note TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id)
)
''')

conn.commit()
conn.close()
print("✅ Database-tabeller oprettet!")

