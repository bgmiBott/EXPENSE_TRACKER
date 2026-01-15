from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from utils.graph import generate_graph
from utils.analyzer import analyze_spending
from utils.filters import filter_data
import os
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'awsedrftgyhujikolp')
app.config['VERSION'] = str(datetime.now().timestamp())

DB_NAME = "expense_data.db"

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            currency TEXT DEFAULT '₹',
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    for command in commands:
        cursor.execute(command)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# ---------------- AUTH ROUTES ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form.get('action')

        conn = get_db_connection()
        cursor = conn.cursor()

        if action == 'login':
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['username'] = user['username']
                session['user_id'] = user['id']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password')

        elif action == 'register':
            try:
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, hashed_password)
                )
                conn.commit()
                flash('Registration successful! Please login.')
            except sqlite3.IntegrityError:
                flash('Username already exists')

        cursor.close()
        conn.close()

    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    current_month = datetime.now().strftime('%Y-%m')

    graph_path = generate_graph(user_id, current_month)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM transactions
        WHERE user_id=? AND type='Income' AND substr(date,1,7)=?
    """, (user_id, current_month))
    income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM transactions
        WHERE user_id=? AND type='Expense' AND substr(date,1,7)=?
    """, (user_id, current_month))
    expenses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(amount),0)
        FROM transactions
        WHERE user_id=? AND type='Savings' AND substr(date,1,7)=?
    """, (user_id, current_month))
    savings = cursor.fetchone()[0]

    balance = max(0, income - expenses - savings)

    cursor.execute("""
        SELECT IFNULL(SUM(CASE WHEN type='Income' THEN amount ELSE 0 END),0),
               IFNULL(SUM(CASE WHEN type IN ('Expense','Savings') THEN amount ELSE 0 END),0)
        FROM transactions
        WHERE user_id=?
    """, (user_id,))
    inc, out = cursor.fetchone()
    outstanding = max(out - inc, 0)

    cursor.execute("SELECT currency FROM profiles WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    currency = row['currency'] if row else '₹'

    cursor.close()
    conn.close()

    advice = analyze_spending(user_id, current_month)

    return render_template(
        'dashboard.html',
        graph_path=graph_path,
        income=income,
        expenses=expenses,
        savings=savings,
        balance=balance,
        outstanding=outstanding,
        advice=advice,
        currency=currency,
        config=app.config
    )

# ---------------- PROFILE ----------------
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO profiles (user_id, full_name, email, phone, address, currency)
            VALUES (?,?,?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
            full_name=excluded.full_name,
            email=excluded.email,
            phone=excluded.phone,
            address=excluded.address,
            currency=excluded.currency
        """, (
            user_id,
            request.form.get('full_name'),
            request.form.get('email'),
            request.form.get('phone'),
            request.form.get('address'),
            request.form.get('currency', '₹')
        ))
        conn.commit()
        flash('Profile updated successfully!')

    cursor.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,))
    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('profile.html', profile=profile)

# ---------------- ADD TRANSACTION ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, category, date)
            VALUES (?,?,?,?,?)
        """, (
            session['user_id'],
            request.form['type'],
            float(request.form['amount']),
            request.form['category'],
            request.form['date']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Transaction added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('add_expense.html', datetime=datetime)

# ---------------- STATISTICS ----------------
@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('statistics.html')

@app.route('/stats_result')
def stats_result():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category', '')

    data = filter_data(user_id, start_date, end_date, category)

    income = sum(t['amount'] for t in data if t['type'] == 'Income')
    expenses = sum(t['amount'] for t in data if t['type'] == 'Expense')
    savings = sum(t['amount'] for t in data if t['type'] == 'Savings')
    balance = income - expenses - savings

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT currency FROM profiles WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    currency = row['currency'] if row else '₹'
    cursor.close()
    conn.close()

    category_expenses = defaultdict(float)
    for t in data:
        if t['type'] == 'Expense':
            category_expenses[t['category']] += t['amount']

    return render_template(
        'stats_result.html',
        income=income,
        expenses=expenses,
        savings=savings,
        balance=balance,
        start_date=start_date,
        end_date=end_date,
        category_expenses=dict(category_expenses),
        category=category,
        currency=currency
    )

if __name__ == '__main__':
    app.run(debug=True)
