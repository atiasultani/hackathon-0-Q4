#!/usr/bin/env python3
"""
Social Media Watcher for Gold Tier AI Employee System
Monitors social media platforms (Facebook, Instagram, X/Twitter) for mentions,
comments, messages, and engagement. Creates task files in Needs_Action/

Supports both real social media APIs and mock mode.
Set API credentials in .env for real API.
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

# Check for social media API credentials
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
HAS_FACEBOOK_API = bool(FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN and HAS_REQUESTS)

INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
HAS_INSTAGRAM_API = bool(INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN and HAS_REQUESTS)

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
HAS_X_API = bool(X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET and HAS_REQUESTS)

if not HAS_FACEBOOK_API:
    print("Facebook API credentials not found. Using mock implementation.")
if not HAS_INSTAGRAM_API:
    print("Instagram API credentials not found. Using mock implementation.")
if not HAS_X_API:
    print("X/Twitter API credentials not found. Using mock implementation.")


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


def create_task_from_social(platform: str, engagement_type: str, user: str, content: str, priority: str = "normal"):
    """Create a task file from social media engagement"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_user = user.replace(" ", "_").replace("/", "_")[:50]

    task_filename = f"SOCIAL_{platform.upper()}_{engagement_type.upper()}_{sanitized_user}_{timestamp}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    task_content = f"""---
type: social_engagement
platform: {platform}
engagement_type: {engagement_type}
from: {user}
priority: {priority}
status: pending
received_at: {datetime.now().isoformat()}
---

# {platform.title()} {engagement_type.title()} from {user}

## Content
{content}

## Action Required
Review this {platform} {engagement_type} and respond appropriately.
"""

    with open(task_path, 'w') as f:
        f.write(task_content)

    log_action("social_engagement", task_filename, "auto", "success")
    print(f"Social Watcher: Created task {task_filename}")


def detect_keywords(text: str) -> Dict[str, List[str]]:
    """Detect important keywords and categorize them"""
    categories = {
        'urgent': [],
        'business': [],
        'complaint': [],
        'positive': [],
        'payment': []
    }

    keyword_map = {
        'urgent': ['urgent', 'asap', 'emergency', 'critical', 'immediately'],
        'business': ['partnership', 'collaboration', 'deal', 'proposal', 'opportunity', 'contract'],
        'complaint': ['complaint', 'issue', 'problem', 'terrible', 'worst', 'unhappy', 'disappointed', 'angry'],
        'positive': ['great', 'awesome', 'love', 'excellent', 'amazing', 'thank', 'wonderful'],
        'payment': ['payment', 'invoice', 'refund', 'charge', 'billing', 'cost', '$']
    }

    text_lower = text.lower()
    for category, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in text_lower:
                categories[category].append(keyword)

    return categories


def get_priority_from_keywords(keyword_categories: Dict[str, List[str]]) -> str:
    """Determine priority based on detected keywords"""
    if keyword_categories['urgent']:
        return 'high'
    if keyword_categories['complaint']:
        return 'high'
    if keyword_categories['payment']:
        return 'high'
    if keyword_categories['business']:
        return 'medium'
    return 'normal'


# =============================================================================
# FACEBOOK - REAL API & MOCK
# =============================================================================

def check_facebook_real():
    """Check Facebook page notifications using Graph API"""
    try:
        # Get page notifications
        url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/notifications"
        params = {
            'access_token': FACEBOOK_ACCESS_TOKEN,
            'limit': 10
        }

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            notifications = data.get('data', [])

            for notif in notifications:
                notif_type = notif.get('type', 'unknown')
                from_user = notif.get('from', {}).get('name', 'Unknown')
                message = notif.get('title', '') + ' ' + notif.get('message', '')

                # Get comments if available
                if notif_type in ['comment', 'mention']:
                    comment_url = f"https://graph.facebook.com/v18.0/{notif.get('id')}/comments"
                    comment_resp = requests.get(comment_url, params={'access_token': FACEBOOK_ACCESS_TOKEN}, timeout=10)
                    if comment_resp.status_code == 200:
                        comments = comment_resp.json().get('data', [])
                        for comment in comments:
                            content = comment.get('message', '')
                            keywords = detect_keywords(content)
                            priority = get_priority_from_keywords(keywords)
                            create_task_from_social('facebook', 'comment', comment.get('from', {}).get('name', 'Unknown'), content, priority)

                keywords = detect_keywords(message)
                priority = get_priority_from_keywords(keywords)
                create_task_from_social('facebook', notif_type.lower(), from_user, message, priority)

        elif response.status_code == 401:
            print("Facebook API: Invalid or expired token")
            log_action("facebook_api_error", "social_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"Facebook API Error: {e}")
        log_action("facebook_api_error", "social_watcher", "auto", f"failed: {str(e)}")


def check_facebook_mock():
    """Mock implementation for Facebook"""
    import random

    if random.randint(1, 50) == 1:  # ~2% chance
        engagement_types = ['comment', 'message', 'mention', 'review', 'tag']
        users = ['John D.', 'Sarah M.', 'Tech Enthusiast', 'Happy Customer', 'Business Owner']
        contents = [
            "Love your products! Can you tell me more about pricing?",
            "Had an issue with my last order. Need urgent help!",
            "Great post about AI automation. Would love to collaborate!",
            "Your service is amazing. Keep up the great work!",
            "Can we schedule a call? I have a business proposal for you."
        ]

        engagement_type = random.choice(engagement_types)
        user = random.choice(users)
        content = random.choice(contents)

        keywords = detect_keywords(content)
        priority = get_priority_from_keywords(keywords)

        create_task_from_social('facebook', engagement_type, user, content, priority)


# =============================================================================
# INSTAGRAM - REAL API & MOCK
# =============================================================================

def check_instagram_real():
    """Check Instagram business account using Graph API"""
    try:
        # Get Instagram media and comments
        url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
        params = {
            'access_token': INSTAGRAM_ACCESS_TOKEN,
            'fields': 'id,caption,comments_count,like_count,timestamp',
            'limit': 5
        }

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            media_items = data.get('data', [])

            for media in media_items:
                media_id = media.get('id')

                # Get comments on each media
                comment_url = f"https://graph.facebook.com/v18.0/{media_id}/comments"
                comment_resp = requests.get(
                    comment_url,
                    params={'access_token': INSTAGRAM_ACCESS_TOKEN, 'limit': 10},
                    timeout=10
                )

                if comment_resp.status_code == 200:
                    comments = comment_resp.json().get('data', [])
                    for comment in comments:
                        user = comment.get('username', 'Unknown')
                        text = comment.get('text', '')
                        keywords = detect_keywords(text)
                        priority = get_priority_from_keywords(keywords)
                        create_task_from_social('instagram', 'comment', f"@{user}", text, priority)

        elif response.status_code == 401:
            print("Instagram API: Invalid or expired token")
            log_action("instagram_api_error", "social_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"Instagram API Error: {e}")
        log_action("instagram_api_error", "social_watcher", "auto", f"failed: {str(e)}")


def check_instagram_mock():
    """Mock implementation for Instagram"""
    import random

    if random.randint(1, 50) == 1:  # ~2% chance
        engagement_types = ['comment', 'dm', 'mention', 'story_mention']
        users = ['@techfan', '@businesspro', '@digital_marketer', '@startup_guru', '@ai_enthusiast']
        contents = [
            "DM: Hi! I saw your post and wanted to discuss a collaboration opportunity",
            "Comment: This is exactly what I needed! Can you share more details?",
            "Mention: Check out this amazing AI company! @our_company",
            "DM: Urgent - need help with an order issue please",
            "Comment: Your content is always so helpful. Thank you!"
        ]

        engagement_type = random.choice(engagement_types)
        user = random.choice(users)
        content = random.choice(contents)

        keywords = detect_keywords(content)
        priority = get_priority_from_keywords(keywords)

        create_task_from_social('instagram', engagement_type, user, content, priority)


# =============================================================================
# X/TWITTER - REAL API & MOCK
# =============================================================================

def check_x_real():
    """Check X/Twitter mentions and DMs using API v2"""
    try:
        import base64
        import hmac
        import hashlib
        import urllib.parse

        # OAuth 1.0a signature for Twitter API v2
        def get_oauth_headers(method, url, params=None):
            oauth_params = {
                'oauth_consumer_key': X_API_KEY,
                'oauth_nonce': base64.b64encode(os.urandom(32)).decode(),
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': str(int(time.time())),
                'oauth_token': X_ACCESS_TOKEN,
                'oauth_version': '1.0'
            }

            all_params = {**(params or {}), **oauth_params}
            sorted_params = '&'.join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted(all_params.items()))
            base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
            signing_key = f"{urllib.parse.quote(X_API_SECRET, safe='')}&{urllib.parse.quote(X_ACCESS_TOKEN_SECRET, safe='')}"
            signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
            oauth_params['oauth_signature'] = signature
            return {'Authorization': 'OAuth ' + ', '.join(f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items()))}

        # Get mentions timeline
        url = 'https://api.twitter.com/2/users/me/mentions'
        headers = get_oauth_headers('GET', url)
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            tweets = data.get('data', [])

            for tweet in tweets:
                text = tweet.get('text', '')
                tweet_id = tweet.get('id', '')
                keywords = detect_keywords(text)
                priority = get_priority_from_keywords(keywords)
                create_task_from_social('x_twitter', 'mention', f"Tweet {tweet_id}", text, priority)

        elif response.status_code == 401:
            print("X/Twitter API: Invalid or expired credentials")
            log_action("x_api_error", "social_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"X/Twitter API Error: {e}")
        log_action("x_api_error", "social_watcher", "auto", f"failed: {str(e)}")


def check_x_mock():
    """Mock implementation for X/Twitter"""
    import random

    if random.randint(1, 50) == 1:  # ~2% chance
        engagement_types = ['mention', 'reply', 'dm', 'quote_tweet']
        users = ['@techceo', '@startupguy', '@ai_researcher', '@business_dev', '@automation_fan']
        contents = [
            "@our_company Great thread on AI automation! Would love to connect",
            "Reply: I've been using your service for months. Game changer!",
            "DM: Hey, I have a business proposal. Can we chat?",
            "Quote: This is the future of work. Thread by @our_company is spot on",
            "Mention: Urgent question about pricing - can someone help?"
        ]

        engagement_type = random.choice(engagement_types)
        user = random.choice(users)
        content = random.choice(contents)

        keywords = detect_keywords(content)
        priority = get_priority_from_keywords(keywords)

        create_task_from_social('x_twitter', engagement_type, user, content, priority)


# =============================================================================
# MAIN WATCH LOOP
# =============================================================================

def watch():
    """Main watch loop"""
    modes = []
    if HAS_FACEBOOK_API:
        modes.append("Facebook:REAL")
    else:
        modes.append("Facebook:MOCK")
    if HAS_INSTAGRAM_API:
        modes.append("Instagram:REAL")
    else:
        modes.append("Instagram:MOCK")
    if HAS_X_API:
        modes.append("X:REAL")
    else:
        modes.append("X:MOCK")

    mode_str = " | ".join(modes)
    print(f"Social Media Watcher running ({mode_str})...")
    log_action("watcher_start", "social_watcher", "auto", f"started_{mode_str}")

    while True:
        try:
            # Facebook
            if HAS_FACEBOOK_API:
                check_facebook_real()
            else:
                check_facebook_mock()

            # Instagram
            if HAS_INSTAGRAM_API:
                check_instagram_real()
            else:
                check_instagram_mock()

            # X/Twitter
            if HAS_X_API:
                check_x_real()
            else:
                check_x_mock()

            time.sleep(60)  # Check every 60 seconds
        except KeyboardInterrupt:
            print("\nSocial Media Watcher stopped by user")
            log_action("watcher_stop", "social_watcher", "auto", "stopped")
            break
        except Exception as e:
            print(f"Error in Social Media Watcher: {e}")
            log_action("watcher_error", "social_watcher", "auto", f"error: {str(e)}")
            time.sleep(120)


if __name__ == "__main__":
    watch()
