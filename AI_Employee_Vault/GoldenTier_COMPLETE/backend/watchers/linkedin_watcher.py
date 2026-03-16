#!/usr/bin/env python3
"""
LinkedIn Watcher for Gold Tier AI Employee System
Monitors LinkedIn for engagement (mentions, comments, messages, connection requests)
and creates task files in Needs_Action/

Supports both real LinkedIn API and mock mode.
Set LINKEDIN_ACCESS_TOKEN in .env for real API.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_PATH = Path(__file__).parent.parent
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
LOGS_DIR = BASE_PATH / "Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Check for LinkedIn API credentials
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_ID = os.getenv("LINKEDIN_PERSON_ID")
HAS_LINKEDIN_API = bool(LINKEDIN_ACCESS_TOKEN and HAS_REQUESTS)

if not HAS_LINKEDIN_API:
    print("LinkedIn API credentials not found. Using mock implementation.")
    print("Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID in .env for real API.")


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


def create_task_from_engagement(engagement_type: str, sender: str, content: str, priority: str = "normal"):
    """Create a task file from LinkedIn engagement"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_sender = sender.replace(" ", "_").replace("/", "_")[:50]

    task_filename = f"LINKEDIN_{engagement_type.upper()}_{sanitized_sender}_{timestamp}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    task_content = f"""---
type: linkedin_engagement
engagement_type: {engagement_type}
from: {sender}
priority: {priority}
status: pending
received_at: {datetime.now().isoformat()}
---

# LinkedIn {engagement_type.title()} from {sender}

## Content
{content}

## Action Required
Review this LinkedIn {engagement_type} and take appropriate action.
"""

    with open(task_path, 'w') as f:
        f.write(task_content)

    log_action("linkedin_engagement", task_filename, "auto", "success")
    print(f"LinkedIn Watcher: Created task {task_filename}")


def detect_keywords(text: str) -> List[str]:
    """Detect important keywords in engagement text"""
    keywords = []
    keyword_patterns = {
        'urgent': ['urgent', 'asap', 'immediately', 'critical'],
        'business': ['partnership', 'collaboration', 'opportunity', 'deal', 'contract'],
        'payment': ['payment', 'invoice', 'billing', 'cost', 'price', '$'],
        'meeting': ['meeting', 'call', 'schedule', 'appointment', 'zoom'],
        'job': ['hiring', 'job', 'position', 'role', 'career', 'apply']
    }

    text_lower = text.lower()
    for category, patterns in keyword_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                keywords.append(category)
                break

    return keywords


def get_priority(keywords: List[str]) -> str:
    """Determine priority from keywords"""
    if any(k in ['urgent', 'business', 'payment'] for k in keywords):
        return 'high'
    return 'normal'


# =============================================================================
# REAL API IMPLEMENTATION
# =============================================================================

def check_linkedin_notifications_real():
    """Check for new LinkedIn notifications using real API"""
    try:
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Get notifications from LinkedIn API
        response = requests.get(
            'https://api.linkedin.com/v2/notifications',
            headers=headers,
            params={'q': 'viewer', 'count': 10},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            notifications = data.get('elements', [])

            for notif in notifications:
                notif_type = notif.get('notificationType', 'unknown')
                actor = notif.get('actor', {})
                actor_name = actor.get('name', 'Unknown User')
                message = notif.get('text', {}).get('text', '')

                # Map notification types
                type_map = {
                    'CONNECTION_INVITATION': 'connection_request',
                    'COMMENT_ON_POST': 'comment',
                    'MENTION': 'mention',
                    'LIKE_POST': 'post_reaction',
                    'MESSAGE': 'message'
                }
                engagement_type = type_map.get(notif_type, notif_type.lower())

                keywords = detect_keywords(message)
                priority = get_priority(keywords)

                create_task_from_engagement(engagement_type, actor_name, message, priority)

        elif response.status_code == 401:
            print("LinkedIn API: Invalid or expired token")
            log_action("linkedin_api_error", "linkedin_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"LinkedIn API Error: {e}")
        log_action("linkedin_api_error", "linkedin_watcher", "auto", f"failed: {str(e)}")


def check_linkedin_messages_real():
    """Check for LinkedIn messages using real API"""
    try:
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        response = requests.get(
            'https://api.linkedin.com/v2/messages',
            headers=headers,
            params={'q': 'conversations', 'count': 10},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            messages = data.get('elements', [])

            for msg in messages:
                sender = msg.get('from', {}).get('name', 'Unknown')
                subject = msg.get('subject', 'No Subject')
                body = msg.get('body', '')

                content = f"Subject: {subject}\n\n{body}"
                keywords = detect_keywords(content)
                priority = get_priority(keywords)

                create_task_from_engagement('message', sender, content, priority)

    except Exception as e:
        print(f"LinkedIn Messages API Error: {e}")


# =============================================================================
# MOCK IMPLEMENTATION
# =============================================================================

def check_linkedin_engagement_mock():
    """Mock implementation for testing without real LinkedIn API"""
    import random

    if random.randint(1, 30) == 1:  # ~3% chance every check
        engagement_types = ['mention', 'comment', 'connection_request', 'message', 'post_reaction']
        senders = [
            "John Smith - CEO at TechCorp",
            "Sarah Johnson - Marketing Director",
            "Mike Chen - Sales Manager",
            "Lisa Wong - Product Manager",
            "David Brown - Consultant"
        ]
        sample_contents = {
            'mention': "Mentioned you in a post about AI automation trends in business",
            'comment': "Great insights on your latest post about digital transformation!",
            'connection_request': "Would like to connect and discuss potential collaboration opportunities",
            'message': "Hi, I saw your profile and would love to discuss a partnership opportunity. Can we schedule a call?",
            'post_reaction': "Liked your post about company growth metrics"
        }

        engagement_type = random.choice(engagement_types)
        sender = random.choice(senders)
        content = sample_contents.get(engagement_type, "New LinkedIn engagement")

        keywords = detect_keywords(content)
        priority = get_priority(keywords)

        create_task_from_engagement(engagement_type, sender, content, priority)


# =============================================================================
# MAIN WATCH LOOP
# =============================================================================

def check_linkedin():
    """Check LinkedIn - uses real API if credentials available, otherwise mock"""
    if HAS_LINKEDIN_API:
        check_linkedin_notifications_real()
        check_linkedin_messages_real()
    else:
        check_linkedin_engagement_mock()


def watch():
    """Main watch loop"""
    mode = "REAL API" if HAS_LINKEDIN_API else "MOCK"
    print(f"LinkedIn Watcher running ({mode})...")
    log_action("watcher_start", "linkedin_watcher", "auto", f"started_{mode.lower()}")

    while True:
        try:
            check_linkedin()
            time.sleep(60)  # Check every 60 seconds
        except KeyboardInterrupt:
            print("\nLinkedIn Watcher stopped by user")
            log_action("watcher_stop", "linkedin_watcher", "auto", "stopped")
            break
        except Exception as e:
            print(f"Error in LinkedIn Watcher: {e}")
            log_action("watcher_error", "linkedin_watcher", "auto", f"error: {str(e)}")
            time.sleep(120)


if __name__ == "__main__":
    watch()
