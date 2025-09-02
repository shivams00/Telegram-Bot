import sqlite3
import argparse
import pandas as pd
from datetime import datetime

DB_NAME = 'finance.db'

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            name TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add a transaction
def add_transaction(t_type, amount, category, name, date=None):
    try:
        amount = float(amount)
        assert amount > 0
    except:
        print("Amount must be a positive number.")
        return

    if t_type not in ['income', 'expense']:
        print("Type must be 'income' or 'expense'.")
        return

    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("Date must be in YYYY-MM-DD format.")
            return
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (type, amount, category, name, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (t_type, amount, category, name, date))
    conn.commit()
    conn.close()
    print("Transaction added.")

# View summary
def view_summary():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    if df.empty:
        print("No transactions yet.")
        return
    df['amount'] = df['amount'].astype(float)
    summary = df.groupby(['type'])['amount'].sum()
    print("\n--- Summary ---")
    print(summary)
    print("\nNet Savings: ${:.2f}".format(summary.get('income', 0) - summary.get('expense', 0)))

# Export to CSV
def export_csv(filename="finance_export.csv"):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    df.to_csv(filename, index=False)
    print(f"Exported to {filename}")

# List all transactions
def view_transactions():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
    conn.close()
    if df.empty:
        print("No transactions recorded.")
    else:
        print("\n--- Transaction List ---")
        print(df.to_string(index=False))

# Filter transactions
def filter_transactions(category=None, name=None):
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM transactions WHERE 1=1"
    if category:
        query += f" AND category='{category}'"
    if name:
        query += f" AND name='{name}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        print("No matching records found.")
    else:
        print("\n--- Filtered Transactions ---")
        print(df.to_string(index=False))

# CLI entry
def main():
    parser = argparse.ArgumentParser(description='📒 Personal Finance Tracker')
    parser.add_argument('--add', nargs=4, metavar=('type', 'amount', 'category', 'name'),
                        help='Add transaction: income/expense amount category name')
    parser.add_argument('--date', metavar='YYYY-MM-DD', help='Optional date for transaction')
    parser.add_argument('--summary', action='store_true', help='View income/expense summary')
    parser.add_argument('--export', metavar='filename', help='Export transactions to CSV')
    parser.add_argument('--list', action='store_true', help='List all transactions')
    parser.add_argument('--filter', nargs='*', metavar=('category', 'name'),
                        help='Filter transactions by category and/or name')

    args = parser.parse_args()
    init_db()

    if args.add:
        t_type, amount, category, name = args.add
        add_transaction(t_type, amount, category, name, args.date)
    elif args.summary:
        view_summary()
    elif args.export:
        export_csv(args.export)
    elif args.list:
        view_transactions()
    elif args.filter:
        category = args.filter[0] if len(args.filter) > 0 else None
        name = args.filter[1] if len(args.filter) > 1 else None
        filter_transactions(category, name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

 # Example usage:
#python finance.py --add income 2000 Salary Shivam

# Add expense with custom date
#python finance.py --add expense 500 Groceries Shivam --date 2025-07-26

# View summary
#python finance.py --summary

# List all transactions
#python finance.py --list

# Export to CSV
#python finance.py --export my_finance.csv

# Filter by category
#python finance.py --filter Groceries

# Filter by category and name
#python finance.py --filter Groceries Shivam
