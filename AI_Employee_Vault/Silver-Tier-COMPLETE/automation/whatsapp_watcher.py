#!/usr/bin/env python3
"""
WhatsApp Watcher for Silver Tier AI Employee System
Monitors WhatsApp for keywords and creates task files
Uses Playwright for browser automation
"""

import os
import time
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Playwright not installed. Using mock implementation.")

BASE_PATH = Path(__file__).parent
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
LOGS_DIR = BASE_PATH / "Logs"

class WhatsAppWatcher:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_running = False

    def log_action(self, message):
        """Log action to file"""
        log_file = LOGS_DIR / "whatsapp_watcher_log.md"
        with open(log_file, "a") as f:
            f.write(f"\n## {datetime.now()}\n{message}\n")

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

        self.log_action(f"Created task from WhatsApp message from {sender}, keywords: {', '.join(keywords)}, priority: {priority}")
        print(f"WhatsApp Watcher: Created task {task_filename}")

    def scan_messages_mock(self):
        """Mock method to simulate scanning WhatsApp messages"""
        # Simulate finding messages with keywords occasionally
        import random

        # Random chance to find a message with keywords
        if random.randint(1, 20) == 1:  # 5% chance every call
            possible_senders = ["Client_A", "Vendor_B", "Team_Member_C", "Customer_D"]
            possible_messages = [
                "Hi, please send the invoice for last month's work",
                "Urgent: We need to discuss the payment terms",
                "Can we schedule a meeting next week?",
                "Thanks for your help with the project",
                "Payment reminder: Invoice #12345 is due soon"
            ]

            sender = random.choice(possible_senders)
            message = random.choice(possible_messages)
            keywords = self.detect_keywords(message)

            if keywords:
                self.create_task_from_message(sender, message, keywords)

    def scan_whatsapp_messages(self):
        """Scan WhatsApp Web for new messages with keywords"""
        if not HAS_PLAYWRIGHT:
            # Use mock implementation if Playwright is not available
            self.scan_messages_mock()
            return

        try:
            if not self.browser:
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(headless=True)
                self.page = self.browser.new_page()

                # Navigate to WhatsApp Web
                self.page.goto('https://web.whatsapp.com')

                # Wait for user to scan QR code
                print("Please scan the QR code in the browser to log in to WhatsApp Web...")
                self.page.wait_for_selector('#pane-side', timeout=60000)  # Wait up to 60 seconds

            # Find chat messages (this is simplified - real implementation would be more complex)
            # Look for new messages in the chat list
            chat_elements = self.page.query_selector_all('[data-testid="conversation"]')

            for element in chat_elements:
                # Extract chat info (simplified)
                chat_text = element.text_content()[:200]  # First 200 chars
                keywords = self.detect_keywords(chat_text)

                if keywords:
                    # In a real implementation, we'd extract the actual sender and message
                    # For now, we'll use a placeholder
                    self.create_task_from_message("Unknown Contact", chat_text, keywords)

        except Exception as e:
            print(f"WhatsApp Watcher Error: {e}")
            self.log_action(f"Error scanning WhatsApp: {str(e)}")

    def watch(self):
        """Main watch loop"""
        print("WhatsApp Watcher running...")
        self.log_action("WhatsApp Watcher started")

        self.is_running = True

        while self.is_running:
            try:
                self.scan_whatsapp_messages()

                # Wait 30 seconds before next scan
                time.sleep(30)
            except KeyboardInterrupt:
                print("\nWhatsApp Watcher stopped by user")
                self.log_action("WhatsApp Watcher stopped")
                break
            except Exception as e:
                print(f"Error in WhatsApp Watcher: {e}")
                self.log_action(f"Error in watch loop: {str(e)}")
                time.sleep(60)  # Wait longer if there's an error

        # Cleanup
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

if __name__ == "__main__":
    watcher = WhatsAppWatcher()
    watcher.watch()