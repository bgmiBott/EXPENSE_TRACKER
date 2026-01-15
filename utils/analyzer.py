import sqlite3
from decimal import Decimal

DB_NAME = "expense_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_spending(user_id, month):
    """Analyzes spending patterns and provides advice."""
    conn = get_db_connection()
    cursor = conn.cursor()

    advice = []

    try:
        # ---- Total income & expense for month ----
        cursor.execute("""
            SELECT 
                IFNULL(SUM(CASE WHEN type='Income' THEN amount ELSE 0 END), 0),
                IFNULL(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END), 0)
            FROM transactions
            WHERE user_id=? AND substr(date,1,7)=?
        """, (user_id, month))

        total_income, total_expense = cursor.fetchone()

        total_income = float(total_income)
        total_expense = float(total_expense)

        savings = total_income - total_expense

        # ---- Savings advice ----
        if total_income > 0:
            if savings < 0:
                advice.append("⚠️ You're spending more than you earn this month! Consider reducing expenses.")
            elif savings < (0.2 * total_income):
                advice.append("💡 You're saving some money, but try to save at least 20% of your income.")
            else:
                advice.append("✅ Great job! You're saving a healthy portion of your income.")

        # ---- Expense breakdown by category ----
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE user_id=? AND type='Expense' AND substr(date,1,7)=?
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """, (user_id, month))

        expenses_by_category = cursor.fetchall()

        if expenses_by_category and total_expense > 0:
            for row in expenses_by_category:
                category = row["category"]
                amount = float(row[1])

                percent = (amount / total_expense) * 100

                if percent > 50:
                    advice.append(
                        f"⚠️ You're spending {percent:.1f}% of your expenses on '{category}'. Consider diversifying."
                    )
                elif percent > 30:
                    advice.append(
                        f"💸 You're spending a lot on '{category}'. Maybe look for ways to reduce this expense."
                    )

        # ---- No expense / no income checks ----
        if total_income > 0 and total_expense == 0:
            advice.append("🌟 You haven't recorded any expenses this month. Great savings!")

        if total_income == 0:
            advice.append("🔄 You haven't recorded any income this month. Don't forget to track your earnings!")

        if not advice:
            advice.append("📊 Keep tracking your expenses for better insights.")

        return advice

    except Exception as e:
        print("Analyzer error:", e)
        return ["An error occurred while analyzing your spending."]
    finally:
        cursor.close()
        conn.close()
