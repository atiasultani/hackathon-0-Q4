import os
import time
import shutil
from datetime import datetime

BASE_PATH = os.getcwd()

NEEDS_ACTION = os.path.join(BASE_PATH, "Needs_Action")
PLANS = os.path.join(BASE_PATH, "Plans")
PENDING_APPROVAL = os.path.join(BASE_PATH, "Pending_Approval")
LOGS = os.path.join(BASE_PATH, "Logs")

def log_action(message):
    log_file = os.path.join(LOGS, "watcher_log.md")
    with open(log_file, "a") as f:
        f.write(f"\n## {datetime.now()}\n{message}\n")

def process_task(task_file):
    task_path = os.path.join(NEEDS_ACTION, task_file)

    # Create plan file
    plan_filename = f"PLAN_{task_file}"
    plan_path = os.path.join(PLANS, plan_filename)

    with open(task_path, "r") as f:
        task_content = f.read()

    with open(plan_path, "w") as f:
        f.write(f"# Plan for {task_file}\n\n")
        f.write("1. Review task\n2. Prepare execution\n3. Request approval\n")

    # Move task to Pending Approval
    shutil.move(task_path, os.path.join(PENDING_APPROVAL, task_file))

    log_action(f"Processed task {task_file} and moved to Pending_Approval")

def watch():
    print("Watcher running...")
    while True:
        tasks = os.listdir(NEEDS_ACTION)
        for task in tasks:
            if task.endswith(".md"):
                process_task(task)
        time.sleep(5)

if __name__ == "__main__":
    watch()