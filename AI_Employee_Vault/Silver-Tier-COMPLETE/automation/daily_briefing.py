import os
import json
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE_PATH, "data")
BRIEFINGS = os.path.join(BASE_PATH, "Briefings")
PENDING = os.path.join(BASE_PATH, "Pending_Approval")

def generate_daily_briefing():
    ledger_path = os.path.join(DATA, "accounting_ledger.json")

    if not os.path.exists(ledger_path):
        return

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    total_expense = ledger.get("total_expense", 0)
    total_transactions = len(ledger.get("transactions", []))
    pending_count = len(os.listdir(PENDING))

    briefing_file = os.path.join(
        BRIEFINGS,
        f"Daily_Briefing_{datetime.now().strftime('%Y_%m_%d')}.md"
    )

    with open(briefing_file, "w", encoding="utf-8") as f:
        f.write("# Daily Executive Briefing\n\n")
        f.write(f"## Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"### Total Expense: ${total_expense}\n")
        f.write(f"### Total Transactions: {total_transactions}\n")
        f.write(f"### Pending Approvals: {pending_count}\n\n")

        f.write("System Status: Operational\n")

    print("Daily briefing generated.")

if __name__ == "__main__":
    generate_daily_briefing()