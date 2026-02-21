#!/usr/bin/env python3
"""
Software Subscription Payment System
Handles $250 software subscription payments with approval and logging workflow
"""

import datetime
import json
import os
from typing import Dict, Optional


class SubscriptionPaymentSystem:
    """Main class for handling subscription payments with approval workflow"""

    def __init__(self, log_file: str = "payment_log.json"):
        self.log_file = log_file
        self.payments = self._load_payments()

    def _load_payments(self) -> list:
        """Load existing payment logs from file"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_payments(self):
        """Save payment logs to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.payments, f, indent=2, default=str)

    def submit_payment_request(self, amount: float, vendor: str, description: str, requester: str) -> Dict:
        """
        Submit a payment request for approval
        """
        payment_request = {
            "id": len(self.payments) + 1,
            "amount": amount,
            "vendor": vendor,
            "description": description,
            "requester": requester,
            "status": "pending",
            "submitted_date": datetime.datetime.now(),
            "approver": None,
            "approved_date": None
        }

        self.payments.append(payment_request)
        self._save_payments()

        print(f"Payment request #{payment_request['id']} submitted successfully!")
        print(f"Amount: ${amount}")
        print(f"Vendor: {vendor}")
        print(f"Description: {description}")
        print(f"Requester: {requester}")
        print(f"Status: {payment_request['status']}")

        return payment_request

    def list_pending_payments(self) -> list:
        """List all pending payment requests"""
        return [p for p in self.payments if p["status"] == "pending"]

    def approve_payment(self, payment_id: int, approver: str) -> Optional[Dict]:
        """Approve a payment request"""
        for payment in self.payments:
            if payment["id"] == payment_id and payment["status"] == "pending":
                payment["status"] = "approved"
                payment["approver"] = approver
                payment["approved_date"] = datetime.datetime.now()

                self._save_payments()

                print(f"Payment #{payment_id} approved successfully!")
                print(f"Approved by: {approver}")
                print(f"Amount: ${payment['amount']}")

                # Process the actual payment
                self.process_payment(payment)

                return payment

        print(f"Payment #{payment_id} not found or already processed.")
        return None

    def reject_payment(self, payment_id: int, approver: str, reason: str = "") -> Optional[Dict]:
        """Reject a payment request"""
        for payment in self.payments:
            if payment["id"] == payment_id and payment["status"] == "pending":
                payment["status"] = "rejected"
                payment["approver"] = approver
                payment["rejection_reason"] = reason
                payment["rejected_date"] = datetime.datetime.now()

                self._save_payments()

                print(f"Payment #{payment_id} rejected!")
                print(f"Rejected by: {approver}")
                print(f"Reason: {reason}")

                return payment

        print(f"Payment #{payment_id} not found or already processed.")
        return None

    def process_payment(self, payment: Dict):
        """Process the actual payment (simulated)"""
        print(f"Processing payment of ${payment['amount']} to {payment['vendor']}")
        # In a real system, this would integrate with a payment processor
        payment["processed_date"] = datetime.datetime.now()
        payment["status"] = "paid"
        self._save_payments()
        print("Payment processed successfully!")

    def view_payment_history(self) -> list:
        """View all payment history"""
        return self.payments

    def view_payment_details(self, payment_id: int) -> Optional[Dict]:
        """View details of a specific payment"""
        for payment in self.payments:
            if payment["id"] == payment_id:
                return payment
        return None


def main():
    """Main function to demonstrate the subscription payment system"""
    system = SubscriptionPaymentSystem()

    print("Software Subscription Payment System")
    print("=" * 40)

    # Example usage
    while True:
        print("\nOptions:")
        print("1. Submit payment request")
        print("2. View pending payments")
        print("3. Approve payment")
        print("4. Reject payment")
        print("5. View payment history")
        print("6. View payment details")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            amount = float(input("Enter amount ($250 for software subscription): "))
            vendor = input("Enter vendor name: ")
            description = input("Enter description: ")
            requester = input("Enter requester name: ")

            system.submit_payment_request(amount, vendor, description, requester)

        elif choice == "2":
            pending_payments = system.list_pending_payments()
            if not pending_payments:
                print("No pending payments.")
            else:
                print("\nPending Payments:")
                for payment in pending_payments:
                    print(f"ID: {payment['id']}, Amount: ${payment['amount']}, "
                          f"Vendor: {payment['vendor']}, Requester: {payment['requester']}, "
                          f"Submitted: {payment['submitted_date']}")

        elif choice == "3":
            payment_id = int(input("Enter payment ID to approve: "))
            approver = input("Enter approver name: ")
            system.approve_payment(payment_id, approver)

        elif choice == "4":
            payment_id = int(input("Enter payment ID to reject: "))
            approver = input("Enter approver name: ")
            reason = input("Enter rejection reason (optional): ")
            system.reject_payment(payment_id, approver, reason)

        elif choice == "5":
            history = system.view_payment_history()
            if not history:
                print("No payment history.")
            else:
                print("\nPayment History:")
                for payment in history:
                    print(f"ID: {payment['id']}, Amount: ${payment['amount']}, "
                          f"Vendor: {payment['vendor']}, Status: {payment['status']}, "
                          f"Requester: {payment['requester']}")

        elif choice == "6":
            payment_id = int(input("Enter payment ID to view details: "))
            details = system.view_payment_details(payment_id)
            if details:
                print(f"\nPayment Details (ID: {details['id']}):")
                for key, value in details.items():
                    print(f"  {key}: {value}")
            else:
                print("Payment not found.")

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()