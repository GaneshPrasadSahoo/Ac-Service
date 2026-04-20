from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import urllib.parse
import os

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            date TEXT,
            message TEXT
        )
    ''')
    conn.close()

# ✅ IMPORTANT: initialize DB for Render (outside main)
init_db()

# ---------- WHATSAPP LINK ----------
def generate_whatsapp_link(phone, message):
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded_msg}"

# ---------- HOME / FORM ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        date = request.form['date']
        message = request.form['message']

        conn = sqlite3.connect('database.db')
        conn.execute(
            "INSERT INTO customers (name, phone, date, message) VALUES (?, ?, ?, ?)",
            (name, phone, date, message)
        )
        conn.commit()
        conn.close()

    return render_template('form.html')

# ---------- REMINDERS ----------
@app.route('/reminders')
def reminders():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    rows = cursor.execute("SELECT * FROM customers").fetchall()

    customers = []

    for row in rows:
        whatsapp_link = generate_whatsapp_link(row[2], row[4])

        customers.append({
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "date": row[3],
            "message": row[4],
            "link": whatsapp_link
        })

    conn.close()

    return render_template("reminders.html", customers=customers)

# ---------- DELETE ----------
@app.route('/delete/<int:id>')
def delete_customer(id):
    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('reminders'))

# ---------- RUN (LOCAL ONLY) ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)