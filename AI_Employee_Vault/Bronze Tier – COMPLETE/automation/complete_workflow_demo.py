#!/usr/bin/env python3
"""
Complete Workflow Demo
Demonstrates the full workflow from payment request to post-approval processing
"""

from subscription_payment import SubscriptionPaymentSystem
from post_approval_processor import PostApprovalProcessor


def demo_complete_workflow():
    """Demonstrate the complete workflow for a $250 software subscription"""
    print("Complete Software Subscription Payment Workflow")
    print("=" * 55)

    # Initialize systems
    payment_system = SubscriptionPaymentSystem()
    post_processor = PostApprovalProcessor(payment_system)

    # Step 1: Submit payment request for $250 software subscription
    print("\nStep 1: Submitting payment request...")
    payment_request = payment_system.submit_payment_request(
        amount=250.00,
        vendor="Software Vendor Inc.",
        description="Annual software subscription license",
        requester="John Doe"
    )

    # Step 2: Approve the payment
    print("\nStep 2: Approving the payment...")
    approved_payment = payment_system.approve_payment(
        payment_id=payment_request['id'],
        approver="Jane Smith"
    )

    # Step 3: Process post-approval tasks
    print("\nStep 3: Processing post-approval tasks...")
    post_approval_results = post_processor.process_post_approval_tasks(approved_payment['id'])

    # Step 4: Show final status
    print("\nStep 4: Final payment status and documentation...")
    final_payment = payment_system.view_payment_details(approved_payment['id'])
    print(f"Payment #{final_payment['id']}: ${final_payment['amount']} - {final_payment['status']}")
    print(f"Vendor: {final_payment['vendor']}")
    print(f"Requester: {final_payment['requester']}")
    print(f"Approver: {final_payment['approver']}")

    if 'receipt_file' in post_approval_results.get('summary', {}):
        print(f"Receipt: {post_approval_results['summary']['receipt_file']}")

    print(f"Post-approval tasks completed: {len(post_approval_results['tasks_completed'])}")
    print(f"Post-approval tasks failed: {len(post_approval_results['tasks_failed'])}")


if __name__ == "__main__":
    demo_complete_workflow()