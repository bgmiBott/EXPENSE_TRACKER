import sqlite3

DB_NAME = "expense_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def filter_data(user_id, start_date, end_date, category=None):
    """Filters transaction data based on user criteria."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT type, amount, category, date
            FROM transactions
            WHERE user_id=? AND date BETWEEN ? AND ?
        """
        params = [user_id, start_date, end_date]

        if category:
            query += " AND category=?"
            params.append(category)

        query += " ORDER BY date"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "type": row["type"],
                "amount": float(row["amount"]),
                "category": row["category"],
                "date": row["date"]   # already YYYY-MM-DD string
            })

        return result

    except Exception as e:
        print("Filter error:", e)
        return []

    finally:
        cursor.close()
        conn.close()
