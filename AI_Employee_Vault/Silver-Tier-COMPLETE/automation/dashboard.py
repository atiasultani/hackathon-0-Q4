import os
import json
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE_PATH, "data")
PENDING = os.path.join(BASE_PATH, "Pending_Approval")

def generate_dashboard():
    ledger_path = os.path.join(DATA, "accounting_ledger.json")

    if not os.path.exists(ledger_path):
        print("No ledger found.")
        return

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    total_expense = ledger.get("total_expense", 0)
    transactions = ledger.get("transactions", [])
    pending_count = len(os.listdir(PENDING))

    html_content = f"""
    <html>
    <head>
        <title>AI Employee Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background-color: #f4f4f4;
                padding: 40px;
            }}
            .card {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>AI Employee Silver Dashboard</h1>

        <div class="card">
            <h2>Total Expense</h2>
            <p>${total_expense}</p>
        </div>

        <div class="card">
            <h2>Total Transactions</h2>
            <p>{len(transactions)}</p>
        </div>

        <div class="card">
            <h2>Pending Approvals</h2>
            <p>{pending_count}</p>
        </div>

        <div class="card">
            <h2>Last 5 Transactions</h2>
            <ul>
                {''.join([f"<li>{t['task']} - ${t['amount']}</li>" for t in transactions[-5:]])}
            </ul>
        </div>

        <div class="card">
            <h2>System Status</h2>
            <p>Operational</p>
            <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """

    dashboard_path = os.path.join(BASE_PATH, "dashboard.html")

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Dashboard generated successfully.")

if __name__ == "__main__":
    generate_dashboard()