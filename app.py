from supabase_client import supabase
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # pip install python-dateutil
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_bcrypt import Bcrypt
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🧩 Supabase import og setup
from supabase import create_client
SUPABASE_URL = "https://dhffpzifxweschuiwiqr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRoZmZwemlmeHdlc2NodWl3aXFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU0OTQ5NDksImV4cCI6MjAyMTA3MDk0OX0.cGpOxk-cn8h0bgVa3iER0nm-T4yymGBt_l5ess08iec"  # ← din anonyme nøgle her
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🎬 Flask setup
app = Flask(__name__)
app.secret_key = 'aZ47&}Sl5|0V'  # Skift til noget unikt!


bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Forbindelse til databasen
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Funktion til at hente gyldige medlemsnumre fra Google Sheet
def get_valid_membership_numbers():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        '/etc/secrets/gspread-credentials.json', scope
    )
    
    client = gspread.authorize(creds)
    sheet = client.open_by_key('1lMO8pqkDTpiAeoUa21y9XUUevMzdPyrnMoEEj8693S4').sheet1
    values = sheet.col_values(1)
    return values


# User-klasse
class User(UserMixin):
    def __init__(self, id, email, is_admin):
        self.id = id
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    db.close()
    if user:
        return User(user['id'], user['email'], user['is_admin'])
    return None

# Forside – vis liste over parringer
@app.route('/')
@login_required
def index():
    db = get_db()
    rows = db.execute('''
        SELECT
            p.id,
            m.name AS male_name,
            m.image AS male_image,
            m.birth_date AS male_birth,
            f.name AS female_name,
            f.image AS female_image,
            f.birth_date AS female_birth,
            p.pairing_date,
            p.expected_due_date,
            u.email AS creator_email
        FROM pairing p
        JOIN guinea_pig m ON p.male_id = m.id
        JOIN guinea_pig f ON p.female_id = f.id
        JOIN user u ON p.user_id = u.id
    ''').fetchall()



    pairings = []
    for row in rows:
        pairing = dict(row)

        pairing["pairing_date"] = datetime.strptime(pairing["pairing_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        pairing_date_obj = datetime.strptime(pairing["pairing_date"], "%d-%m-%Y")

        early_due = pairing_date_obj + timedelta(days=68)
        late_due = pairing_date_obj + timedelta(days=72)
        pairing["term_interval"] = f"{early_due.strftime('%d-%m-%Y')} til {late_due.strftime('%d-%m-%Y')}"

        male_birth = datetime.strptime(pairing["male_birth"], "%Y-%m-%d")
        female_birth = datetime.strptime(pairing["female_birth"], "%Y-%m-%d")

        male_age = relativedelta(pairing_date_obj, male_birth)
        female_age = relativedelta(pairing_date_obj, female_birth)

        pairing["male_age"] = f"{male_age.years} år, {male_age.months} mdr"
        pairing["female_age"] = f"{female_age.years} år, {female_age.months} mdr"

        pairings.append(pairing)

    db.close()
    return render_template('index.html', pairings=pairings)

# Formular til ny parring
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    from supabase_client import supabase  # sørg for at denne fil eksisterer

    # Hent marsvin fra Supabase
    pigs_data = supabase.table("guinea_pigs").select("*").execute().data

    pigs = []
    for pig in pigs_data:
        pigs.append({
            "id": pig["id"],
            "name": pig["name"],
            "gender": pig["sex"],  # så det matcher 'gender' i HTML-template
            "birth_date": pig["date_of_birth"],
            "pedigree_number": pig["pedigree_number"],
            "color": pig["color"],
            "titles": pig["titles"],
            "race_id": pig["race_id"]
        })

    if request.method == 'POST':
        male = request.form['male']
        female = request.form['female']
        date = request.form['date']
        due = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=59)

        db = get_db()
        db.execute(
            'INSERT INTO pairing (male_id, female_id, pairing_date, expected_due_date, user_id) VALUES (?, ?, ?, ?, ?)',
            (male, female, date, due.date(), current_user.id)
        )
        db.commit()
        db.close()
        return redirect('/')

    return render_template('add_pairing.html', pigs=pigs)

# Slet en parring – kun hvis ejer eller admin
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    db = get_db()
    pairing = db.execute('SELECT * FROM pairing WHERE id = ?', (id,)).fetchone()

    if not pairing:
        db.close()
        return "Parring ikke fundet", 404

    if pairing['user_id'] != current_user.id and not current_user.is_admin:
        db.close()
        return "Du har ikke tilladelse til at slette denne parring", 403

    db.execute('DELETE FROM pairing WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect('/')

# Login-rute
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        db.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(user['id'], user['email'], user['is_admin']))
            return redirect('/')
        else:
            error = 'Forkert e-mail eller kodeord'
    return render_template('login.html', error=error)


# Logout-rute
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
# Registrering af ny bruger
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None

    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        membership_number = request.form['membership_number']

        # Tjek medlemsnummer mod Google Sheet
        valid_numbers = get_valid_membership_numbers()
        if membership_number not in valid_numbers:
            error = "Medlemsnummeret findes ikke. Kontakt administrator."
        else:
            db = get_db()
            # Tjek om brugeren allerede findes
            existing = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
            if existing:
                error = "En bruger med denne e-mail findes allerede."
            else:
                hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
                db.execute(
                    'INSERT INTO user (name, email, password, membership_number, is_admin) VALUES (?, ?, ?, ?, ?)',
                    (name, email, hashed_pw, membership_number, 0)
                )
                db.commit()
                db.close()
                success = "Bruger oprettet! Du kan nu logge ind."

    return render_template('register.html', error=error, success=success)


# Midlertidig route til at oprette admin-bruger
@app.route('/create-admin')
def create_admin():
    email = "bonde_44@hotmail.com"
    password = "mithemmeligekodeord"
    membership_number = "12345"
    is_admin = 1

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    db = get_db()
    db.execute("DELETE FROM user WHERE email = ?", (email,))
    db.execute('''
        INSERT INTO user (email, password, membership_number, is_admin)
        VALUES (?, ?, ?, ?)
    ''', (email, hashed_pw, membership_number, is_admin))
    db.commit()
    db.close()

    return "✅ Admin oprettet med korrekt hash!"

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return "Adgang nægtet – kun for admins", 403

    query = request.args.get('q', '').lower()

    db = get_db()
    if query:
        users = db.execute('''
            SELECT * FROM user
            WHERE LOWER(name) LIKE ? OR LOWER(email) LIKE ?
        ''', (f'%{query}%', f'%{query}%')).fetchall()
    else:
        users = db.execute('SELECT * FROM user').fetchall()
    db.close()

    return render_template('admin_users.html', users=users)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        return "Adgang nægtet", 403

    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()
    db.close()
    return redirect('/admin/users')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin:
        return "Adgang nægtet", 403

    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

    if not user:
        db.close()
        return "Bruger ikke fundet", 404

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        membership_number = request.form['membership_number']
        is_admin = 1 if 'is_admin' in request.form else 0

        db.execute('''
            UPDATE user
            SET name = ?, email = ?, membership_number = ?, is_admin = ?
            WHERE id = ?
        ''', (name, email, membership_number, is_admin, user_id))
        db.commit()
        db.close()
        return redirect('/admin/users')

    db.close()
    return render_template('admin_edit_user.html', user=user)

@app.route('/edit/<int:pairing_id>', methods=['GET', 'POST'])
@login_required
def edit_pairing(pairing_id):
    db = get_db()
    pairing = db.execute('SELECT * FROM pairing WHERE id = ?', (pairing_id,)).fetchone()

    if not pairing:
        db.close()
        return "Parring ikke fundet", 404

    if pairing['user_id'] != current_user.id:
        db.close()
        return "Du har ikke adgang til at redigere denne parring", 403

    if request.method == 'POST':
        new_date = request.form['pairing_date']
        note = request.form['note']
        expected_due = datetime.strptime(new_date, "%Y-%m-%d") + timedelta(days=59)

        db.execute('''
            UPDATE pairing
            SET pairing_date = ?, expected_due_date = ?, note = ?
            WHERE id = ?
        ''', (new_date, expected_due.date(), note, pairing_id))
        db.commit()
        db.close()
        return redirect('/')

    db.close()
    return render_template('edit_pairing.html', pairing=pairing)


# Start Flask-serveren
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5004))
    app.run(debug=False, host="0.0.0.0", port=port)

