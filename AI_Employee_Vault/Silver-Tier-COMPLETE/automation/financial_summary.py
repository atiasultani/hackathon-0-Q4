import os
import json
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE_PATH, "data")
BRIEFINGS = os.path.join(BASE_PATH, "Briefings")

def generate_summary():
    ledger_path = os.path.join(DATA, "accounting_ledger.json")

    if not os.path.exists(ledger_path):
        print("No ledger found.")
        return

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    total = ledger.get("total_expense", 0)
    transactions = ledger.get("transactions", [])

    summary_file = os.path.join(
        BRIEFINGS,
        f"Financial_Summary_{datetime.now().strftime('%Y_%m_%d')}.md"
    )

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# Financial Summary\n\n")
        f.write(f"## Total Expense: ${total}\n\n")
        f.write("## Recent Transactions:\n\n")

        for tx in transactions[-5:]:
            f.write(f"- {tx['task']} → ${tx['amount']}\n")

    print("Financial summary generated.")

if __name__ == "__main__":
    generate_summary()