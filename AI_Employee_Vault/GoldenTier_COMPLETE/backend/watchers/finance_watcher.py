#!/usr/bin/env python3
"""
Finance Watcher for Gold Tier AI Employee System
Monitors for bank transaction alerts and financial notifications.
Creates task files in Needs_Action/ for review and processing.

Supports both real bank API and mock mode.
Set bank API credentials in .env for real API (Plaid, Stripe, etc).
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re

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

# Check for bank API credentials
BANK_API_PROVIDER = os.getenv("BANK_API_PROVIDER", "")  # 'plaid', 'stripe', or 'custom'
BANK_API_KEY = os.getenv("BANK_API_KEY")
BANK_API_SECRET = os.getenv("BANK_API_SECRET")
BANK_ACCOUNT_ID = os.getenv("BANK_ACCOUNT_ID")
HAS_BANK_API = bool(BANK_API_PROVIDER and BANK_API_KEY and HAS_REQUESTS)

if not HAS_BANK_API:
    print("Bank API credentials not found. Using mock implementation.")
    print("Set BANK_API_PROVIDER, BANK_API_KEY in .env for real API.")


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


def create_task_from_transaction(transaction_type: str, amount: float, merchant: str,
                                  description: str, priority: str = "medium"):
    """Create a task file from financial transaction"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_merchant = merchant.replace(" ", "_").replace("/", "_")[:50]

    task_filename = f"FINANCE_{transaction_type.upper()}_{sanitized_merchant}_{timestamp}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    task_content = f"""---
type: finance_transaction
transaction_type: {transaction_type}
amount: {amount}
merchant: {merchant}
priority: {priority}
requires_approval: {'true' if amount > 100 else 'false'}
status: pending
received_at: {datetime.now().isoformat()}
---

# Financial Alert: {transaction_type.title()}

## Transaction Details
- **Merchant:** {merchant}
- **Amount:** ${amount:.2f}
- **Type:** {transaction_type}
- **Requires Approval:** {'Yes (over $100)' if amount > 100 else 'No'}

## Description
{description}

## Action Required
{'This transaction requires human approval before processing.' if amount > 100 else 'Review and log this transaction in accounting.'}
"""

    with open(task_path, 'w') as f:
        f.write(task_content)

    log_action("finance_transaction", task_filename, "auto", "success")
    print(f"Finance Watcher: Created task {task_filename}")


def process_transaction_file(file_path: str):
    """Process a transaction file dropped in the finance folder"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract transaction info
    amount_match = re.search(r'Amount:\s*\$?(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    merchant_match = re.search(r'Merchant:\s*(.*)', content, re.IGNORECASE)
    type_match = re.search(r'Type:\s*(.*)', content, re.IGNORECASE)

    amount = float(amount_match.group(1)) if amount_match else 0.0
    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown Merchant"
    transaction_type = type_match.group(1).strip() if type_match else "unknown"

    priority = "high" if amount > 100 else "medium"

    create_task_from_transaction(transaction_type, amount, merchant, content, priority)

    # Clean up source file
    os.remove(file_path)


# =============================================================================
# REAL API IMPLEMENTATIONS
# =============================================================================

def check_plaid_transactions():
    """Check transactions using Plaid API"""
    try:
        # Get recent transactions from Plaid
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        headers = {
            'PLAID-CLIENT-ID': BANK_API_KEY,
            'PLAID-SECRET': BANK_API_SECRET,
            'Content-Type': 'application/json'
        }

        payload = {
            'access_token': BANK_ACCOUNT_ID,
            'start_date': start_date,
            'end_date': end_date,
            'options': {
                'count': 20
            }
        }

        response = requests.post(
            'https://production.plaid.com/transactions/get',
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])

            for txn in transactions:
                amount = abs(txn.get('amount', 0))
                merchant = txn.get('merchant_name', txn.get('name', 'Unknown'))
                txn_type = 'debit' if txn.get('amount', 0) > 0 else 'credit'
                category = ', '.join(txn.get('category', []))
                description = f"Category: {category}"

                priority = "high" if amount > 100 else "medium"
                create_task_from_transaction(txn_type, amount, merchant, description, priority)

        elif response.status_code == 401:
            print("Plaid API: Invalid credentials")
            log_action("plaid_api_error", "finance_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"Plaid API Error: {e}")
        log_action("plaid_api_error", "finance_watcher", "auto", f"failed: {str(e)}")


def check_stripe_transactions():
    """Check transactions using Stripe API"""
    try:
        headers = {
            'Authorization': f'Bearer {BANK_API_KEY}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Get recent charges
        response = requests.get(
            'https://api.stripe.com/v1/charges',
            headers=headers,
            params={'limit': 20},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            charges = data.get('data', [])

            for charge in charges:
                amount = charge.get('amount', 0) / 100  # Stripe uses cents
                merchant = charge.get('description', 'Unknown')
                status = charge.get('status', 'unknown')
                txn_type = 'credit' if charge.get('refunded', False) else 'debit'
                description = f"Status: {status}, Customer: {charge.get('customer', 'N/A')}"

                priority = "high" if amount > 100 else "medium"
                create_task_from_transaction(txn_type, amount, merchant, description, priority)

        elif response.status_code == 401:
            print("Stripe API: Invalid API key")
            log_action("stripe_api_error", "finance_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"Stripe API Error: {e}")
        log_action("stripe_api_error", "finance_watcher", "auto", f"failed: {str(e)}")


def check_custom_bank_api():
    """Check transactions using custom bank API endpoint"""
    try:
        bank_api_url = os.getenv("BANK_API_URL")
        if not bank_api_url:
            print("BANK_API_URL not set")
            return

        headers = {
            'Authorization': f'Bearer {BANK_API_KEY}',
            'Content-Type': 'application/json'
        }

        params = {
            'account_id': BANK_ACCOUNT_ID,
            'from_date': (datetime.now() - timedelta(days=1)).isoformat(),
            'to_date': datetime.now().isoformat()
        }

        response = requests.get(
            f"{bank_api_url}/transactions",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', data.get('data', []))

            for txn in transactions:
                amount = abs(float(txn.get('amount', 0)))
                merchant = txn.get('merchant', txn.get('description', 'Unknown'))
                txn_type = txn.get('type', 'unknown')
                description = txn.get('description', '')

                priority = "high" if amount > 100 else "medium"
                create_task_from_transaction(txn_type, amount, merchant, description, priority)

        elif response.status_code == 401:
            print("Custom Bank API: Invalid credentials")
            log_action("bank_api_error", "finance_watcher", "auto", "auth_failed")

    except Exception as e:
        print(f"Custom Bank API Error: {e}")
        log_action("bank_api_error", "finance_watcher", "auto", f"failed: {str(e)}")


# =============================================================================
# MOCK IMPLEMENTATION
# =============================================================================

def check_transaction_alerts_mock():
    """Mock implementation for testing without real bank API"""
    import random

    if random.randint(1, 60) == 1:  # ~1.7% chance every check
        transactions = [
            {'type': 'debit', 'amount': 45.99, 'merchant': 'Office Supplies Inc', 'desc': 'Monthly office supply order'},
            {'type': 'debit', 'amount': 299.00, 'merchant': 'Software License Co', 'desc': 'Annual software subscription renewal'},
            {'type': 'credit', 'amount': 1500.00, 'merchant': 'Client Payment - ABC Corp', 'desc': 'Invoice #1234 payment received'},
            {'type': 'debit', 'amount': 89.50, 'merchant': 'Cloud Hosting Services', 'desc': 'Monthly hosting fee'},
            {'type': 'credit', 'amount': 750.00, 'merchant': 'Client Payment - XYZ Ltd', 'desc': 'Consulting fee payment'},
            {'type': 'debit', 'amount': 1200.00, 'merchant': 'Marketing Agency', 'desc': 'Q1 marketing campaign payment'},
        ]

        txn = random.choice(transactions)
        priority = "high" if txn['amount'] > 100 else "medium"
        create_task_from_transaction(
            txn['type'], txn['amount'], txn['merchant'], txn['desc'], priority
        )


# =============================================================================
# MAIN WATCH LOOP
# =============================================================================

def check_transactions():
    """Check transactions - uses real API if credentials available, otherwise mock"""
    if HAS_BANK_API:
        provider = BANK_API_PROVIDER.lower()
        if provider == 'plaid':
            check_plaid_transactions()
        elif provider == 'stripe':
            check_stripe_transactions()
        elif provider == 'custom':
            check_custom_bank_api()
        else:
            print(f"Unknown bank API provider: {provider}. Using mock.")
            check_transaction_alerts_mock()
    else:
        check_transaction_alerts_mock()


def watch():
    """Main watch loop"""
    mode = f"REAL API ({BANK_API_PROVIDER})" if HAS_BANK_API else "MOCK"
    print(f"Finance Watcher running ({mode})...")
    log_action("watcher_start", "finance_watcher", "auto", f"started_{mode.lower()}")

    # Create monitored directory for file drops
    finance_dir = BASE_PATH / "watchers" / "finance"
    finance_dir.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            # Check for dropped transaction files
            for file_path in finance_dir.glob("*.txt"):
                process_transaction_file(str(file_path))

            # Check API or mock
            check_transactions()

            time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\nFinance Watcher stopped by user")
            log_action("watcher_stop", "finance_watcher", "auto", "stopped")
            break
        except Exception as e:
            print(f"Error in Finance Watcher: {e}")
            log_action("watcher_error", "finance_watcher", "auto", f"error: {str(e)}")
            time.sleep(60)


if __name__ == "__main__":
    watch()
