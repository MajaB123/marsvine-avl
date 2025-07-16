import sqlite3
from flask import Flask
from flask_bcrypt import Bcrypt

# Initialiser Flask og Bcrypt korrekt
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Admin-oplysninger
email = "bonde_44@hotmail.com"
password = "mithemmeligekodeord"
membership_number = "12345"
is_admin = 1

# Opret forbindelse
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Slet eksisterende bruger hvis den findes (undgår UNIQUE-fejl)
cursor.execute("DELETE FROM user WHERE email = ?", (email,))

# Hash password korrekt
hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

# Indsæt admin-bruger
cursor.execute('''
    INSERT INTO user (email, password, membership_number, is_admin)
    VALUES (?, ?, ?, ?)
''', (email, hashed_pw, membership_number, is_admin))

conn.commit()
conn.close()

print("✅ Admin oprettet med korrekt hash og medlemsnummer!")
