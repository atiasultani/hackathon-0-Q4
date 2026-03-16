#!/usr/bin/env python3
"""
WhatsApp Watcher for Silver Tier AI Employee System
Monitors WhatsApp for keywords and creates task files
Uses mock implementation for environments without browser support (like WSL without GUI)
"""

import os
import time
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import random

BASE_PATH = Path(__file__).parent.parent  # Go up one level to the main directory
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
LOGS_DIR = BASE_PATH / "Logs"
# Ensure Logs folder exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(action_type: str, target: str, approval_status: str, result: str):
    """Create structured JSON log entry (compliant with CLAUDE.md)"""
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


class WhatsAppWatcher:
    def __init__(self):
        self.is_running = False

    def detect_keywords(self, message_text: str) -> List[str]:
        """Detect important keywords in message text"""
        keywords = []
        keyword_patterns = {
            'invoice': r'\binvoice\b|\b(?:pro)?forma.*bill\b|\bquote\b',
            'urgent': r'\burgent\b|\basap\b|\bimmediate\b|\bcritical\b',
            'payment': r'\bpaid\b|\bpayment\b|\bpay\b|\bbill\b|\bamount\b|\$\d+',
            'meeting': r'\bmeet\b|\bcall\b|\bappointment\b|\bschedule\b',
            'client': r'\bclient\b|\bcustomer\b|\bcontact\b'
        }

        for keyword, pattern in keyword_patterns.items():
            if re.search(pattern, message_text, re.IGNORECASE):
                keywords.append(keyword)

        return keywords

    def create_task_from_message(self, sender: str, message: str, keywords: List[str]):
        """Create a task file from WhatsApp message"""
        # Sanitize sender name for filename
        sanitized_sender = re.sub(r'[^\w\s-]', '_', sender)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        task_filename = f"WHATSAPP_{sanitized_sender}_{timestamp}.md"
        task_path = NEEDS_ACTION_DIR / task_filename

        # Determine priority based on keywords
        high_priority_keywords = ['urgent', 'invoice', 'payment']
        priority = 'high' if any(kw in keywords for kw in high_priority_keywords) else 'normal'

        # Create task content with metadata
        task_content = f"""---
type: whatsapp_message
from: {sender}
keywords: {', '.join(keywords)}
priority: {priority}
status: pending
received_at: {datetime.now().isoformat()}
---

# WhatsApp Message from {sender}

## Message Content
{message}

## Detected Keywords
{', '.join(keywords)}

## Action Required
Please review this WhatsApp message and take appropriate action.
"""

        with open(task_path, 'w') as f:
            f.write(task_content)

        log_action("message_detected", task_filename, "auto", "success")
        print(f"WhatsApp Watcher: Created task {task_filename}")

    def scan_messages_mock(self):
        """Mock method to simulate scanning WhatsApp messages"""
        # Simulate finding messages with keywords occasionally
        # Increased frequency for demo purposes
        if random.randint(1, 10) == 1:  # 10% chance every call
            possible_senders = ["Client_A", "Vendor_B", "Team_Member_C", "Customer_D", "Business_Partner", "Project_Manager"]
            possible_messages = [
                "Hi, please send the invoice for last month's work",
                "Urgent: We need to discuss the payment terms",
                "Can we schedule a meeting next week?",
                "Thanks for your help with the project",
                "Payment reminder: Invoice #12345 is due soon",
                "Could you provide an update on the project status?",
                "We need to finalize the contract by Friday",
                "Are you available for a quick call tomorrow?",
                "Don't forget about our meeting next Monday",
                "Please review the attached document and provide feedback"
            ]

            sender = random.choice(possible_senders)
            message = random.choice(possible_messages)
            keywords = self.detect_keywords(message)

            if keywords:
                self.create_task_from_message(sender, message, keywords)

    def watch(self):
        """Main watch loop - uses mock implementation for WSL compatibility"""
        print("WhatsApp Watcher running (mock implementation for WSL)...")
        print("Note: This is a simulation since browser automation is not available in this environment.")
        print("In a production environment with GUI support, this would connect to WhatsApp Web.")
        log_action("watcher_start", "whatsapp_watcher", "auto", "started")

        self.is_running = True

        while self.is_running:
            try:
                # Use the mock implementation since we're in WSL without GUI support
                self.scan_messages_mock()

                # Wait 30 seconds before next scan
                print("Waiting 30 seconds before next scan...")
                time.sleep(30)
            except KeyboardInterrupt:
                print("\nWhatsApp Watcher stopped by user")
                log_action("watcher_stop", "whatsapp_watcher", "auto", "stopped")
                break
            except Exception as e:
                print(f"Error in WhatsApp Watcher: {e}")
                log_action("watcher_error", "whatsapp_watcher", "auto", f"error: {str(e)}")
                time.sleep(60)  # Wait longer if there's an error


if __name__ == "__main__":
    print("Starting WhatsApp Watcher (WSL-compatible version)...")
    watcher = WhatsAppWatcher()
    watcher.watch()