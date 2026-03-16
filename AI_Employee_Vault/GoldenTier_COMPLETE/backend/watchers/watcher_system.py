"""
File Watcher System for Golden AI Employee
Implements the required watchers for monitoring different sources
"""
import os
import time
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class WatcherBase(FileSystemEventHandler):
    """Base class for all watchers"""

    def __init__(self, monitored_directory, target_directory="Needs_Action"):
        self.monitored_directory = monitored_directory
        self.target_directory = os.path.join(BASE_PATH, target_directory)
        self.observer = Observer()

    def start(self):
        """Start watching the directory"""
        self.observer.schedule(self, self.monitored_directory, recursive=False)
        self.observer.start()
        print(f"Started watching: {self.monitored_directory}")

    def stop(self):
        """Stop watching the directory"""
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.handle_new_file(event.src_path)

    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.handle_modified_file(event.src_path)

    def handle_new_file(self, file_path):
        """Override in subclasses to handle new files"""
        pass

    def handle_modified_file(self, file_path):
        """Override in subclasses to handle modified files"""
        pass

class GmailWatcher(WatcherBase):
    """Watches for new emails and creates task files"""

    def __init__(self):
        super().__init__(os.path.join(BASE_PATH, "watchers", "gmail"), "Needs_Action")
        os.makedirs(self.monitored_directory, exist_ok=True)

    def handle_new_file(self, file_path):
        """Process new email file and create task"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract email info
        subject_match = re.search(r'Subject:\s*(.*)', content)
        sender_match = re.search(r'From:\s*(.*)', content)

        subject = subject_match.group(1) if subject_match else "No Subject"
        sender = sender_match.group(1) if sender_match else "Unknown Sender"

        # Determine priority and financial review requirement
        priority = "medium"
        requires_financial_review = bool(re.search(r'\$(\d+)|payment|bill|expense|cost', content, re.IGNORECASE))

        if requires_financial_review:
            priority = "high"

        # Create structured markdown file
        task_content = f"""---
type: email
source: gmail
priority: {priority}
requires_financial_review: {str(requires_financial_review).lower()}
status: pending
sender: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
---

# Email from {sender}

## Subject: {subject}

{content}

"""

        # Create task file
        task_filename = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path).replace('.txt', '')}.md"
        task_path = os.path.join(self.target_directory, task_filename)

        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        print(f"Created email task: {task_filename}")

        # Clean up source file
        os.remove(file_path)

class WhatsAppWatcher(WatcherBase):
    """Watches for new WhatsApp messages and creates task files"""

    def __init__(self):
        super().__init__(os.path.join(BASE_PATH, "watchers", "whatsapp"), "Needs_Action")
        os.makedirs(self.monitored_directory, exist_ok=True)

    def handle_new_file(self, file_path):
        """Process new WhatsApp message and create task"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract contact info
        contact_match = re.search(r'Contact:\s*(.*)', content)
        contact = contact_match.group(1) if contact_match else "Unknown Contact"

        # Determine priority and financial review requirement
        priority = "medium"
        requires_financial_review = bool(re.search(r'\$(\d+)|payment|invoice|money|cost', content, re.IGNORECASE))

        if requires_financial_review:
            priority = "high"

        # Create structured markdown file
        task_content = f"""---
type: whatsapp
source: whatsapp
priority: {priority}
requires_financial_review: {str(requires_financial_review).lower()}
status: pending
contact: {contact}
received: {datetime.now().isoformat()}
---

# WhatsApp Message from {contact}

{content}

"""

        # Create task file
        task_filename = f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path).replace('.txt', '')}.md"
        task_path = os.path.join(self.target_directory, task_filename)

        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        print(f"Created WhatsApp task: {task_filename}")

        # Clean up source file
        os.remove(file_path)

class FinanceWatcher(WatcherBase):
    """Watches for new bank transaction files and creates task files"""

    def __init__(self):
        super().__init__(os.path.join(BASE_PATH, "watchers", "finance"), "Needs_Action")
        os.makedirs(self.monitored_directory, exist_ok=True)

    def handle_new_file(self, file_path):
        """Process new finance transaction and create task"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract transaction info
        amount_match = re.search(r'Amount:\s*\$?(\d+(?:\.\d+)?)', content)
        merchant_match = re.search(r'Merchant:\s*(.*)', content)

        amount = amount_match.group(1) if amount_match else "0"
        merchant = merchant_match.group(1) if merchant_match else "Unknown Merchant"

        # Determine priority
        priority = "high" if float(amount) > 100 else "medium"
        requires_financial_review = True  # All financial transactions need review

        # Create structured markdown file
        task_content = f"""---
type: finance
source: bank_transaction
priority: {priority}
requires_financial_review: {str(requires_financial_review).lower()}
status: pending
amount: ${amount}
merchant: {merchant}
received: {datetime.now().isoformat()}
---

# Bank Transaction Alert

**Merchant:** {merchant}
**Amount:** ${amount}

{content}

"""

        # Create task file
        task_filename = f"finance_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path).replace('.txt', '')}.md"
        task_path = os.path.join(self.target_directory, task_filename)

        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        print(f"Created finance task: {task_filename}")

        # Clean up source file
        os.remove(file_path)

class FileWatcher(WatcherBase):
    """Watches for new project drop files and creates task files"""

    def __init__(self):
        super().__init__(os.path.join(BASE_PATH, "watchers", "files"), "Needs_Action")
        os.makedirs(self.monitored_directory, exist_ok=True)

    def handle_new_file(self, file_path):
        """Process new file drop and create task"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determine priority and financial review requirement
        priority = "medium"
        requires_financial_review = bool(re.search(r'\$(\d+)|payment|invoice|budget|cost', content, re.IGNORECASE))

        if requires_financial_review:
            priority = "high"

        # Create structured markdown file
        task_content = f"""---
type: file_drop
source: local_project
priority: {priority}
requires_financial_review: {str(requires_financial_review).lower()}
status: pending
filename: {os.path.basename(file_path)}
received: {datetime.now().isoformat()}
---

# Project File Drop

**Original Filename:** {os.path.basename(file_path)}

{content}

"""

        # Create task file
        task_filename = f"filedrop_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path).replace('.txt', '')}.md"
        task_path = os.path.join(self.target_directory, task_filename)

        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        print(f"Created file drop task: {task_filename}")

        # Clean up source file
        os.remove(file_path)

class SocialWatcher(WatcherBase):
    """Watches for new social engagement alerts and creates task files"""

    def __init__(self):
        super().__init__(os.path.join(BASE_PATH, "watchers", "social"), "Needs_Action")
        os.makedirs(self.monitored_directory, exist_ok=True)

    def handle_new_file(self, file_path):
        """Process new social engagement and create task"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract social info
        platform_match = re.search(r'Platform:\s*(.*)', content)
        user_match = re.search(r'User:\s*(.*)', content)

        platform = platform_match.group(1) if platform_match else "Unknown Platform"
        user = user_match.group(1) if user_match else "Unknown User"

        # Determine priority
        priority = "low"
        if re.search(r'mention|tag|dm|message', content, re.IGNORECASE):
            priority = "medium"
        if re.search(r'complaint|issue|problem', content, re.IGNORECASE):
            priority = "high"

        requires_financial_review = bool(re.search(r'\$(\d+)|payment|sponsor|ad|cost', content, re.IGNORECASE))

        # Create structured markdown file
        task_content = f"""---
type: social
source: {platform}
priority: {priority}
requires_financial_review: {str(requires_financial_review).lower()}
status: pending
platform: {platform}
user: {user}
received: {datetime.now().isoformat()}
---

# Social Media Engagement

**Platform:** {platform}
**User:** {user}

{content}

"""

        # Create task file
        task_filename = f"social_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path).replace('.txt', '')}.md"
        task_path = os.path.join(self.target_directory, task_filename)

        with open(task_path, 'w', encoding='utf-8') as f:
            f.write(task_content)

        print(f"Created social task: {task_filename}")

        # Clean up source file
        os.remove(file_path)

class WatcherManager:
    """Manages all watchers"""

    def __init__(self):
        self.watchers = [
            GmailWatcher(),
            WhatsAppWatcher(),
            FinanceWatcher(),
            FileWatcher(),
            SocialWatcher()
        ]

    def start_all(self):
        """Start all watchers"""
        print("Starting all watchers...")
        for watcher in self.watchers:
            watcher.start()

    def stop_all(self):
        """Stop all watchers"""
        print("Stopping all watchers...")
        for watcher in self.watchers:
            watcher.stop()

def main():
    """Main function to run the watcher system"""
    manager = WatcherManager()

    try:
        manager.start_all()
        print("All watchers started. Press Ctrl+C to stop.")

        # Create directories if they don't exist
        for subdir in ["gmail", "whatsapp", "finance", "files", "social"]:
            os.makedirs(os.path.join(BASE_PATH, "watchers", subdir), exist_ok=True)

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down watchers...")
        manager.stop_all()
        print("All watchers stopped.")

if __name__ == "__main__":
    main()