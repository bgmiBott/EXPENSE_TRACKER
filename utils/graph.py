import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
import os

DB_NAME = "expense_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def generate_graph(user_id, month):
    """Generates a financial overview graph for the given user and month."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                date,
                SUM(CASE WHEN type='Income' THEN amount ELSE 0 END) AS income,
                SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END) AS expense,
                SUM(CASE WHEN type='Savings' THEN amount ELSE 0 END) AS savings
            FROM transactions
            WHERE user_id=? AND substr(date,1,7)=?
            GROUP BY date
            ORDER BY date
        """, (user_id, month))

        rows = cursor.fetchall()

        if not rows:
            return None

        # SQLite stores date as TEXT (YYYY-MM-DD)
        dates = [row["date"][-2:] for row in rows]  # day part
        income = [float(row["income"]) for row in rows]
        expenses = [float(row["expense"]) for row in rows]
        savings = [float(row["savings"]) for row in rows]

        # ---- Cumulative values ----
        cum_income, cum_expenses, cum_savings = [], [], []
        ti = te = ts = 0

        for i, e, s in zip(income, expenses, savings):
            ti += i
            te += e
            ts += s
            cum_income.append(ti)
            cum_expenses.append(te)
            cum_savings.append(ts)

        # ---- Plot ----
        plt.figure(figsize=(6,3))
        bar_width = 0.25
        x = range(len(dates))

        plt.bar([i - bar_width for i in x], cum_income, width=bar_width, label='Income', color='green')
        plt.bar(x, cum_expenses, width=bar_width, label='Expenses', color='red')
        plt.bar([i + bar_width for i in x], cum_savings, width=bar_width, label='Savings', color='blue')

        plt.xticks(x, dates)
        plt.title(f'Financial Overview - {datetime.strptime(month, "%Y-%m").strftime("%B %Y")}')
        plt.xlabel('Day of Month')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid(True)

        os.makedirs('static/graphs', exist_ok=True)
        file_name = f'graph_{user_id}_{month}.png'
        file_path = os.path.join('static/graphs', file_name)

        plt.savefig(file_path, dpi=100, bbox_inches='tight')
        plt.close()

        return f'graphs/{file_name}'

    except Exception as e:
        print("Graph error:", e)
        return None

    finally:
        cursor.close()
        conn.close()
