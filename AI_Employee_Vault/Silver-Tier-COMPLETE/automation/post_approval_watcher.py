import os
import time
import shutil
from datetime import datetime
import json
import re
from financial_summary import generate_summary
from daily_briefing import generate_daily_briefing
from dashboard import generate_dashboard

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPROVED = os.path.join(BASE_PATH, "Approved")
DONE = os.path.join(BASE_PATH, "Done")
LOGS = os.path.join(BASE_PATH, "Logs")
DATA = os.path.join(BASE_PATH, "data")

def log_action(message):
    log_file = os.path.join(LOGS, "execution_log.md")
    with open(log_file, "a") as f:
        f.write(f"\n## {datetime.now()}\n{message}\n")

def update_accounting(task_file, content):
    match = re.search(r"\$(\d+)", content)
    amount = int(match.group(1)) if match else 0

    ledger_path = os.path.join(DATA, "accounting_ledger.json")

    if not os.path.exists(ledger_path):
        with open(ledger_path, "w") as f:
            json.dump({"transactions": [], "total_expense": 0}, f, indent=4)

    with open(ledger_path, "r") as f:
        ledger = json.load(f)

    ledger["transactions"].append({
        "task": task_file,
        "amount": amount,
        "date": str(datetime.now())
    })

    ledger["total_expense"] += amount

    with open(ledger_path, "w") as f:
        json.dump(ledger, f, indent=4)

    log_action(f"Updated accounting ledger for {task_file} with ${amount}")

def execute_task(task_file):
    task_path = os.path.join(APPROVED, task_file)

    with open(task_path, "r") as f:
        content = f.read()

    update_accounting(task_file, content)
    # Auto-generate summary after executing the task
    generate_summary()
    # Regenerate daily briefing to reflect new changes
    generate_daily_briefing()
    # Regenerate dashboard to reflect new changes
    generate_dashboard()

    log_action(f"Executed approved task: {task_file}")
    shutil.move(task_path, os.path.join(DONE, task_file))

def watch():
    print("Post-Approval Watcher Running...")
    while True:
        files = os.listdir(APPROVED)
        for file in files:
            if file.endswith(".md"):
                execute_task(file)
        time.sleep(5)
    
if __name__ == "__main__":
    watch()