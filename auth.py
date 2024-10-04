import sqlite3
import bcrypt

def create_connection():
    conn = sqlite3.connect('personal_finance.db')  # Save to a file for persistence
    return conn

def initialize_db(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS incomes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT,
                        date TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT,
                        date TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        budget_amount REAL NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()

def register_user(conn, username, password):
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return "User registered successfully."
    except sqlite3.IntegrityError:
        return "Error: Username already exists. Please choose a different username."

def login_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return user
    return None

def add_income(conn, user_id, amount, category, description, date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO incomes (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, amount, category, description, date))
    conn.commit()

def update_income(conn, income_id, user_id, amount, category, description, date):
    cursor = conn.cursor()
    cursor.execute('''UPDATE incomes SET amount = ?, category = ?, description = ?, date = ?
                      WHERE id = ? AND user_id = ?''',
                   (amount, category, description, date, income_id, user_id))
    conn.commit()

def add_expense(conn, user_id, amount, category, description, date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, amount, category, description, date))
    conn.commit()

def update_expense(conn, expense_id, user_id, amount, category, description, date):
    cursor = conn.cursor()
    cursor.execute('''UPDATE expenses SET amount = ?, category = ?, description = ?, date = ?
                      WHERE id = ? AND user_id = ?''',
                   (amount, category, description, date, expense_id, user_id))
    conn.commit()

def set_budget(conn, user_id, category, budget_amount):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO budgets (user_id, category, budget_amount) VALUES (?, ?, ?)",
                   (user_id, category, budget_amount))
    conn.commit()

def check_budget(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT category, budget_amount FROM budgets WHERE user_id=?", (user_id,))
    budgets = cursor.fetchall()
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (user_id,))
    expenses = cursor.fetchall()
    expense_dict = {category: total for category, total in expenses}
    budget_info = []
    for category, budget_amount in budgets:
        total_expense = expense_dict.get(category, 0)
        budget_info.append((category, budget_amount, total_expense, total_expense > budget_amount))
    return budget_info

def view_income_details(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incomes WHERE user_id=?", (user_id,))
    return cursor.fetchall()

def view_expense_details(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))
    return cursor.fetchall()

def view_monthly_transactions(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incomes WHERE user_id=? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')", (user_id,))
    incomes = cursor.fetchall()
    cursor.execute("SELECT * FROM expenses WHERE user_id=? AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')", (user_id,))
    expenses = cursor.fetchall()
    return incomes, expenses

def view_yearly_transactions(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incomes WHERE user_id=? AND strftime('%Y', date) = strftime('%Y', 'now')", (user_id,))
    incomes = cursor.fetchall()
    cursor.execute("SELECT * FROM expenses WHERE user_id=? AND strftime('%Y', date) = strftime('%Y', 'now')", (user_id,))
    expenses = cursor.fetchall()
    return incomes, expenses

def generate_report(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM incomes WHERE user_id=?", (user_id,))
    total_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    total_expense = cursor.fetchone()[0] or 0
    savings = total_income - total_expense
    return total_income, total_expense, savings

def delete_income(conn, transaction_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM incomes WHERE id=?", (transaction_id,))
    conn.commit()

def delete_expense(conn, transaction_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (transaction_id,))
    conn.commit()

def backup_data(conn, backup_file):
    with open(backup_file, 'w') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')

def restore_data(conn, backup_file):
    cursor = conn.cursor()
    with open(backup_file, 'r') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
