#!/usr/bin/env python3
"""
Test script for the subscription payment workflow
Demonstrates the full workflow for a $250 software subscription
"""

from subscription_payment import SubscriptionPaymentSystem


def demo_subscription_payment():
    """Demonstrate the full workflow for a $250 software subscription"""
    print("Demo: Software Subscription Payment Workflow")
    print("=" * 50)

    # Initialize the payment system
    system = SubscriptionPaymentSystem()

    # Step 1: Submit payment request for $250 software subscription
    print("\nStep 1: Submitting payment request...")
    payment_request = system.submit_payment_request(
        amount=250.00,
        vendor="Software Vendor Inc.",
        description="Annual software subscription license",
        requester="John Doe"
    )

    print("\nStep 2: Listing pending payments...")
    pending_payments = system.list_pending_payments()
    for payment in pending_payments:
        print(f"  Pending Payment: #{payment['id']} - ${payment['amount']} to {payment['vendor']}")

    # Step 3: Approve the payment
    print("\nStep 3: Approving the payment...")
    approved_payment = system.approve_payment(
        payment_id=payment_request['id'],
        approver="Jane Smith"
    )

    # Step 4: Show payment history
    print("\nStep 4: Showing updated payment history...")
    history = system.view_payment_history()
    for payment in history:
        print(f"  Payment #{payment['id']}: ${payment['amount']} - {payment['status']} - {payment['vendor']}")


if __name__ == "__main__":
    demo_subscription_payment()