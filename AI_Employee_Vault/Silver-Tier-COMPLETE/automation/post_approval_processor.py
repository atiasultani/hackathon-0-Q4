#!/usr/bin/env python3
"""
Post-Approval Processing for Subscription Payments
Handles tasks that occur after payment approval like vendor notifications and receipts
"""

import datetime
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import uuid


class PostApprovalProcessor:
    """Handles post-approval tasks for subscription payments"""

    def __init__(self, payment_system, log_file: str = "post_approval_log.json"):
        self.payment_system = payment_system
        self.log_file = log_file
        self.processing_logs = self._load_processing_logs()

    def _load_processing_logs(self) -> list:
        """Load existing processing logs from file"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_processing_logs(self):
        """Save processing logs to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.processing_logs, f, indent=2, default=str)

    def notify_vendor(self, payment: Dict) -> bool:
        """Simulate sending payment notification to vendor"""
        try:
            print(f"Sending payment notification to vendor: {payment['vendor']}")

            # Log the vendor notification
            notification_log = {
                "id": str(uuid.uuid4()),
                "payment_id": payment['id'],
                "action": "vendor_notification",
                "timestamp": datetime.datetime.now(),
                "vendor": payment['vendor'],
                "amount": payment['amount'],
                "status": "sent"
            }

            self.processing_logs.append(notification_log)
            self._save_processing_logs()

            print(f"Notification sent to {payment['vendor']} for payment #{payment['id']}")
            return True

        except Exception as e:
            print(f"Error sending vendor notification: {str(e)}")
            return False

    def generate_receipt(self, payment: Dict) -> str:
        """Generate a receipt for the payment"""
        try:
            receipt_data = {
                "receipt_id": f"REC-{payment['id']}-{int(datetime.datetime.now().timestamp())}",
                "payment_id": payment['id'],
                "amount": payment['amount'],
                "vendor": payment['vendor'],
                "description": payment['description'],
                "requester": payment['requester'],
                "approver": payment['approver'],
                "payment_date": payment.get('processed_date', str(datetime.datetime.now())),
                "status": "paid"
            }

            # Save receipt to file
            receipt_filename = f"receipt_{payment['id']}_{int(datetime.datetime.now().timestamp())}.json"
            with open(receipt_filename, 'w') as f:
                json.dump(receipt_data, f, indent=2, default=str)

            print(f"Receipt generated: {receipt_filename}")

            # Log the receipt generation
            receipt_log = {
                "id": str(uuid.uuid4()),
                "payment_id": payment['id'],
                "action": "receipt_generation",
                "timestamp": datetime.datetime.now(),
                "receipt_file": receipt_filename,
                "status": "generated"
            }

            self.processing_logs.append(receipt_log)
            self._save_processing_logs()

            return receipt_filename

        except Exception as e:
            print(f"Error generating receipt: {str(e)}")
            return ""

    def update_accounting_system(self, payment: Dict) -> bool:
        """Simulate updating accounting system with payment information"""
        try:
            print(f"Updating accounting system with payment #{payment['id']}")

            # Simulate integration with accounting system
            accounting_entry = {
                "entry_id": f"ACC-{payment['id']}-{int(datetime.datetime.now().timestamp())}",
                "payment_id": payment['id'],
                "amount": payment['amount'],
                "vendor": payment['vendor'],
                "description": payment['description'],
                "date": str(datetime.datetime.now()),
                "category": "software_subscription",
                "status": "posted"
            }

            # Save to accounting ledger
            ledger_filename = "accounting_ledger.json"
            ledger = []
            if os.path.exists(ledger_filename):
                with open(ledger_filename, 'r') as f:
                    ledger = json.load(f)

            ledger.append(accounting_entry)

            with open(ledger_filename, 'w') as f:
                json.dump(ledger, f, indent=2, default=str)

            print(f"Accounting entry posted: {accounting_entry['entry_id']}")

            # Log the accounting update
            accounting_log = {
                "id": str(uuid.uuid4()),
                "payment_id": payment['id'],
                "action": "accounting_update",
                "timestamp": datetime.datetime.now(),
                "accounting_entry_id": accounting_entry['entry_id'],
                "status": "completed"
            }

            self.processing_logs.append(accounting_log)
            self._save_processing_logs()

            return True

        except Exception as e:
            print(f"Error updating accounting system: {str(e)}")
            return False

    def send_internal_notification(self, payment: Dict) -> bool:
        """Send internal notification about completed payment"""
        try:
            print(f"Sending internal notification for payment #{payment['id']}")

            # Simulate sending internal notification (email, Slack, etc.)
            internal_notification = {
                "notification_id": str(uuid.uuid4()),
                "payment_id": payment['id'],
                "action": "internal_notification",
                "timestamp": datetime.datetime.now(),
                "recipients": [payment['requester'], payment['approver']],
                "subject": f"Payment #{payment['id']} Completed: ${payment['amount']} to {payment['vendor']}",
                "status": "sent"
            }

            # Log the internal notification
            self.processing_logs.append(internal_notification)
            self._save_processing_logs()

            print(f"Internal notification sent to {payment['requester']} and {payment['approver']}")
            return True

        except Exception as e:
            print(f"Error sending internal notification: {str(e)}")
            return False

    def process_post_approval_tasks(self, payment_id: int) -> Dict:
        """Execute all post-approval tasks for a payment"""
        print(f"\nStarting post-approval processing for payment #{payment_id}")

        # Get the payment details
        payment = self.payment_system.view_payment_details(payment_id)
        if not payment:
            print(f"Payment #{payment_id} not found")
            return {"success": False, "error": "Payment not found"}

        if payment['status'] != 'paid':
            print(f"Payment #{payment_id} is not in 'paid' status")
            return {"success": False, "error": "Payment not in paid status"}

        # Execute post-approval tasks
        results = {
            "payment_id": payment_id,
            "timestamp": datetime.datetime.now(),
            "tasks_completed": [],
            "tasks_failed": [],
            "summary": {}
        }

        # 1. Notify vendor
        if self.notify_vendor(payment):
            results["tasks_completed"].append("vendor_notification")
        else:
            results["tasks_failed"].append("vendor_notification")

        # 2. Generate receipt
        receipt_file = self.generate_receipt(payment)
        if receipt_file:
            results["tasks_completed"].append("receipt_generation")
            results["summary"]["receipt_file"] = receipt_file
        else:
            results["tasks_failed"].append("receipt_generation")

        # 3. Update accounting system
        if self.update_accounting_system(payment):
            results["tasks_completed"].append("accounting_update")
        else:
            results["tasks_failed"].append("accounting_update")

        # 4. Send internal notification
        if self.send_internal_notification(payment):
            results["tasks_completed"].append("internal_notification")
        else:
            results["tasks_failed"].append("internal_notification")

        # Log the overall processing result
        processing_result = {
            "id": str(uuid.uuid4()),
            "payment_id": payment_id,
            "action": "post_approval_processing",
            "timestamp": datetime.datetime.now(),
            "tasks_completed": results["tasks_completed"],
            "tasks_failed": results["tasks_failed"],
            "status": "completed" if not results["tasks_failed"] else "partial_success"
        }

        self.processing_logs.append(processing_result)
        self._save_processing_logs()

        print(f"\nPost-approval processing completed for payment #{payment_id}")
        print(f"Tasks completed: {len(results['tasks_completed'])}")
        print(f"Tasks failed: {len(results['tasks_failed'])}")

        return results


def main():
    """Main function to demonstrate post-approval processing"""
    from subscription_payment import SubscriptionPaymentSystem

    print("Post-Approval Processing System")
    print("=" * 40)

    # Initialize the payment system and post-approval processor
    payment_system = SubscriptionPaymentSystem()
    processor = PostApprovalProcessor(payment_system)

    # Example usage
    while True:
        print("\nOptions:")
        print("1. Process post-approval tasks for a payment")
        print("2. View post-approval processing logs")
        print("3. View accounting ledger")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            payment_id = int(input("Enter payment ID to process (must be in 'paid' status): "))
            result = processor.process_post_approval_tasks(payment_id)
            print(f"\nProcessing result: {result}")

        elif choice == "2":
            logs = processor.processing_logs
            if not logs:
                print("No processing logs found.")
            else:
                print("\nPost-Approval Processing Logs:")
                for log in logs[-10:]:  # Show last 10 logs
                    print(f"  {log}")

        elif choice == "3":
            if os.path.exists("accounting_ledger.json"):
                with open("accounting_ledger.json", 'r') as f:
                    ledger = json.load(f)
                print("\nAccounting Ledger:")
                for entry in ledger[-5:]:  # Show last 5 entries
                    print(f"  {entry}")
            else:
                print("No accounting ledger found.")

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()