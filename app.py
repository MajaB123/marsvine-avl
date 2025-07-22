from supabase import create_client
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from flask_bcrypt import Bcrypt
import os

# 🧩 Supabase import og setup
SUPABASE_URL = "https://dhffpzifxweschuiwiqr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRoZmZwemlmeHdlc2NodWl3aXFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU0OTQ5NDksImV4cCI6MjAyMTA3MDk0OX0.cGpOxk-cn8h0bgVa3iER0nm-T4yymGBt_l5ess08iec"  # Erstat med din Supabase API-nøgle
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database.db')  # Sørg for, at din database fil hedder 'database.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 🎬 Flask setup
app = Flask(__name__)
app.secret_key = 'aZ47&}Sl5|0V'  # Skift til noget unikt

bcrypt = Bcrypt(app)

# Oprettelse af bruger (almindelig bruger)
@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    error = None
    if request.method == 'POST':
        # Hent data fra formularen
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        membership_number = request.form['membership_number']

        print(f"Trying to find membership number: {membership_number}")  # Debugging: viser medlemsnummeret

        # Test med en simpel forespørgsel for at hente data fra Supabase
        response = supabase.table('breeders').select('*').limit(1).execute()
        print(f"Supabase response data: {response.data}")  # Vi fokuserer på at vise dataene fra en simpel forespørgsel

        # Test af medlemsnummeret
        response = supabase.table('breeders').select('*').eq('membership_number', membership_number).execute()
        print(f"Supabase response data with membership_number: {response.data}")  # Se om dataen er tom her

        user_data = response.data  # Hvis svaret er korrekt
        print(f"User data received: {user_data}")  # Debugging: viser hvad Supabase returnerer

        if not user_data:
            error = 'Medlemsnummer ikke fundet i systemet.'
        else:
            # Hvis medlemsnummeret findes, opret ny bruger
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

            db = get_db()
            db.execute('''
                INSERT INTO user (email, name, password, membership_number, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, name, hashed_pw, membership_number, 0))  # Almindelig bruger
            db.commit()
            db.close()

            return redirect('/')

    return render_template('create_user.html', error=error)



# Oprettelse af admin-bruger
@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    error = None
    if request.method == 'POST':
        # Hent data fra formularen
        name = request.form['name']
        password = request.form['password']

        # Hvis det er admin, opretter vi admin uden medlemsnummer
        email = "bonde_44@hotmail.com"  # Admin email
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        db = get_db()
        db.execute('''
            INSERT INTO user (email, name, password, membership_number, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, name, hashed_pw, None, 1))  # Admin har ikke medlemsnummer
        db.commit()
        db.close()
        return redirect('/')

    return render_template('create_admin.html', error=error)

if __name__ == "__main__":
    print("🚧 Starter server og tjekker admin-bruger...")  # Debugging

    # Tjek om admin allerede findes i databasen
    db = get_db()
    existing_admin = db.execute('SELECT * FROM user WHERE is_admin = 1').fetchone()

    if existing_admin:
        print("✅ Admin findes allerede i databasen.")
    else:
        # Hvis admin ikke findes, opret en
        email = "bonde_44@hotmail.com"
        name = "Maja"
        password = "mithemmeligekodeord"
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        db.execute('''
            INSERT INTO user (email, name, password, membership_number, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, name, hashed_pw, None, 1))  # Admin har ikke medlemsnummer
        db.commit()

        print("✅ Admin oprettet!")

    db.close()

    # Kør Flask app
    app.run(debug=True, host="0.0.0.0", port=5013)

