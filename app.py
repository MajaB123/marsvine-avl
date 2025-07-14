from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Husk at installere: pip install python-dateutil

app = Flask(__name__)

# Forbindelse til databasen
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Forside – vis liste over parringer
@app.route('/')
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
            p.expected_due_date
        FROM pairing p
        JOIN guinea_pig m ON p.male_id = m.id
        JOIN guinea_pig f ON p.female_id = f.id
    ''').fetchall()

    pairings = []
    for row in rows:
        pairing = dict(row)

        # Formatér sammensætningsdato
        pairing["pairing_date"] = datetime.strptime(pairing["pairing_date"], "%Y-%m-%d").strftime("%d-%m-%Y")

        # Udregn terminsinterval
        pairing_date_obj = datetime.strptime(pairing["pairing_date"], "%d-%m-%Y")
        early_due = pairing_date_obj + timedelta(days=68)
        late_due = pairing_date_obj + timedelta(days=72)
        pairing["term_interval"] = f"{early_due.strftime('%d-%m-%Y')} til {late_due.strftime('%d-%m-%Y')}"

        # Udregn alder for han og hun ved parring
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
def add():
    db = get_db()
    pigs = db.execute('SELECT * FROM guinea_pig').fetchall()

    if request.method == 'POST':
        male = request.form['male']
        female = request.form['female']
        date = request.form['date']
        due = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=59)

        db.execute(
            'INSERT INTO pairing (male_id, female_id, pairing_date, expected_due_date) VALUES (?, ?, ?, ?)',
            (male, female, date, due.date())
        )
        db.commit()
        db.close()
        return redirect('/')

    db.close()
    return render_template('add_pairing.html', pigs=pigs)

# Slet en parring
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db()
    db.execute('DELETE FROM pairing WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect('/')

# Start Flask-serveren
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
