from flask_bcrypt import Bcrypt
import sqlite3

# Admin-oplysninger
email = "bonde_44@hotmail.com"
password = "mithemmeligekodeord"
membership_number = "12345"
is_admin = 1
name = "Admin"

# Hash kodeordet
bcrypt = Bcrypt()
hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

# Tilslut database og opret admin
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Slet evt. tidligere bruger med samme email
c.execute("DELETE FROM user WHERE email = ?", (email,))

# Opret ny admin
c.execute("""
    INSERT INTO user (name, email, password, membership_number, is_admin)
    VALUES (?, ?, ?, ?, ?)
""", ("Admin", email, hashed_pw, membership_number, is_admin))

conn.commit()
conn.close()

print("✅ Admin oprettet!")

