#!/usr/bin/env python3
"""
Gmail Watcher for Silver Tier AI Employee System
Monitors Gmail for important emails and creates task files
"""

import os
import time
from datetime import datetime
from pathlib import Path
import json
import base64
from typing import Dict, List

try:
    import google.auth
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False
    print("Google API libraries not installed. Using mock implementation.")

BASE_PATH = Path(__file__).parent
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
LOGS_DIR = BASE_PATH / "Logs"

# If Google API is not available, use a mock implementation
if not HAS_GOOGLE_API:
    class MockGmailService:
        def users(self):
            return self

        def messages(self):
            return self

        def list(self, userId='me', q=None, maxResults=10):
            # Return mock response with some sample emails
            return self

        def execute(self):
            # Return mock emails
            return {
                'messages': [
                    {
                        'id': f'mock_email_{int(time.time())}',
                        'snippet': 'Sample important email about business'
                    }
                ] if time.time() % 120 < 10 else {}  # Create a mock email every ~120 seconds
            }

    def get_gmail_service():
        return MockGmailService()
else:
    def get_gmail_service():
        """Authenticate and return Gmail service object"""
        creds = None
        token_path = BASE_PATH / "token.json"
        credentials_path = BASE_PATH / "credentials.json"

        # Load existing token
        if token_path.exists():
            with open(token_path, 'r') as token:
                creds = google.auth.load_credentials_from_file(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        "credentials.json not found. Please set up Google API credentials."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, ['https://www.googleapis.com/auth/gmail.readonly']
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

def log_action(message):
    """Log action to file"""
    log_file = LOGS_DIR / "gmail_watcher_log.md"
    with open(log_file, "a") as f:
        f.write(f"\n## {datetime.now()}\n{message}\n")

def create_task_from_email(email_data: Dict):
    """Create a task file from email data"""
    email_id = email_data.get('id', 'unknown')
    snippet = email_data.get('snippet', 'No content')

    # Create task filename
    task_filename = f"EMAIL_{email_id}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    # Determine priority based on keywords
    high_priority_keywords = ['urgent', 'important', 'asap', 'critical', 'payment', 'invoice']
    priority = 'high' if any(keyword in snippet.lower() for keyword in high_priority_keywords) else 'normal'

    # Create task content with metadata
    task_content = f"""---
type: email
from: mock.sender@example.com
subject: Mock Email Subject
priority: {priority}
status: pending
received_at: {datetime.now().isoformat()}
---

# Email from mock.sender@example.com

## Subject
Mock Email Subject

## Content Preview
{snippet}

## Action Required
Please review this email and take appropriate action.
"""

    with open(task_path, 'w') as f:
        f.write(task_content)

    log_action(f"Created task from email {email_id}, priority: {priority}")
    print(f"Gmail Watcher: Created task {task_filename}")

def check_new_emails():
    """Check for new unread important emails"""
    try:
        service = get_gmail_service()

        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            q='is:unread category:primary',  # Only unread primary emails
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        for msg in messages:
            # Get full message details
            message = service.users().messages().get(
                userId='me',
                id=msg['id']
            ).execute()

            # Extract relevant information (simplified)
            snippet = message.get('snippet', '')

            # Create task if important
            create_task_from_email({
                'id': msg['id'],
                'snippet': snippet
            })

    except Exception as e:
        print(f"Gmail Watcher Error: {e}")
        log_action(f"Error checking emails: {str(e)}")

def watch():
    """Main watch loop"""
    print("Gmail Watcher running...")
    log_action("Gmail Watcher started")

    while True:
        try:
            # Check for new emails every 30 seconds
            check_new_emails()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nGmail Watcher stopped by user")
            log_action("Gmail Watcher stopped")
            break
        except Exception as e:
            print(f"Error in Gmail Watcher: {e}")
            time.sleep(60)  # Wait longer if there's an error

if __name__ == "__main__":
    watch()