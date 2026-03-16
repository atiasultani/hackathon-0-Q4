#!/usr/bin/env python3
"""
File Watcher for Gold Tier AI Employee System
Monitors a drop folder for new project files and documents.
Creates task files in Needs_Action/ for processing.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict
import re

BASE_PATH = Path(__file__).parent.parent
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
LOGS_DIR = BASE_PATH / "Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(action_type: str, target: str, approval_status: str, result: str):
    """Create structured JSON log entry"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "action_type": action_type,
        "target": target,
        "approval_status": approval_status,
        "result": result
    }

    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    logs = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)


def create_task_from_file(filename: str, content: str, file_type: str, priority: str = "normal"):
    """Create a task file from a dropped file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_name = filename.replace(" ", "_").replace("/", "_")[:50]

    task_filename = f"FILE_{sanitized_name}_{timestamp}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    task_content = f"""---
type: file_drop
file_type: {file_type}
original_filename: {filename}
priority: {priority}
status: pending
received_at: {datetime.now().isoformat()}
---

# File Drop: {filename}

## File Details
- **Original Filename:** {filename}
- **File Type:** {file_type}
- **Size:** {len(content)} characters

## Content Preview
{content[:500]}{'...' if len(content) > 500 else ''}

## Action Required
Review this file and take appropriate action based on its content.
"""

    with open(task_path, 'w') as f:
        f.write(task_content)

    log_action("file_drop", task_filename, "auto", "success")
    print(f"File Watcher: Created task {task_filename}")


def detect_keywords(text: str) -> Dict[str, bool]:
    """Detect important keywords in file content"""
    text_lower = text.lower()
    return {
        'financial': bool(re.search(r'\$[\d,]+\.?\d*|payment|invoice|budget|cost|expense|revenue', text_lower)),
        'urgent': bool(re.search(r'urgent|asap|deadline|critical|immediate', text_lower)),
        'client': bool(re.search(r'client|customer|contract|agreement|proposal', text_lower)),
        'meeting': bool(re.search(r'meeting|agenda|minutes|attendees|schedule', text_lower)),
    }


def get_priority_from_keywords(keywords: Dict[str, bool]) -> str:
    """Determine priority based on detected keywords"""
    if keywords['urgent'] or keywords['financial']:
        return 'high'
    if keywords['client']:
        return 'medium'
    return 'normal'


def process_dropped_file(file_path: str):
    """Process a file dropped in the files folder"""
    filename = os.path.basename(file_path)
    file_ext = os.path.splitext(filename)[1].lower()

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Binary file
        content = f"[Binary file: {filename}]"

    keywords = detect_keywords(content)
    priority = get_priority_from_keywords(keywords)

    file_type_map = {
        '.txt': 'text',
        '.md': 'markdown',
        '.pdf': 'pdf',
        '.doc': 'document',
        '.docx': 'document',
        '.csv': 'spreadsheet',
        '.xlsx': 'spreadsheet',
        '.json': 'data',
        '.xml': 'data',
    }

    file_type = file_type_map.get(file_ext, 'unknown')

    create_task_from_file(filename, content, file_type, priority)

    # Clean up source file
    os.remove(file_path)


def watch():
    """Main watch loop"""
    print("File Watcher running...")
    log_action("watcher_start", "file_watcher", "auto", "started")

    # Create monitored directory
    files_dir = BASE_PATH / "watchers" / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            # Check for new files
            for file_path in files_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    process_dropped_file(str(file_path))

            time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            print("\nFile Watcher stopped by user")
            log_action("watcher_stop", "file_watcher", "auto", "stopped")
            break
        except Exception as e:
            print(f"Error in File Watcher: {e}")
            log_action("watcher_error", "file_watcher", "auto", f"error: {str(e)}")
            time.sleep(30)


if __name__ == "__main__":
    watch()
