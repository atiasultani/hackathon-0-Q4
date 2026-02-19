#!/usr/bin/env python3
"""
Workflow Management and Reporting Dashboard
Provides overview and reporting for the subscription payment workflow
"""

import json
import os
from datetime import datetime
from subscription_payment import SubscriptionPaymentSystem
from post_approval_processor import PostApprovalProcessor


class WorkflowDashboard:
    """Dashboard for monitoring and reporting on subscription payment workflows"""

    def __init__(self):
        self.payment_system = SubscriptionPaymentSystem()
        self.processor = PostApprovalProcessor(self.payment_system)

    def generate_workflow_report(self) -> dict:
        """Generate a comprehensive report of the workflow status"""
        all_payments = self.payment_system.view_payment_history()

        report = {
            "report_generated": datetime.now().isoformat(),
            "total_payments": len(all_payments),
            "by_status": {},
            "total_amount_processed": 0.0,
            "recent_payments": [],
            "processing_completion_rate": 0.0
        }

        # Count payments by status
        for payment in all_payments:
            status = payment['status']
            report['by_status'][status] = report['by_status'].get(status, 0) + 1

            if payment['status'] in ['paid', 'approved']:
                report['total_amount_processed'] += payment['amount']

        # Get recent payments
        recent = sorted(all_payments, key=lambda x: x.get('submitted_date', ''), reverse=True)[:5]
        for payment in recent:
            report['recent_payments'].append({
                'id': payment['id'],
                'amount': payment['amount'],
                'vendor': payment['vendor'],
                'status': payment['status'],
                'requester': payment['requester'],
                'submitted_date': payment.get('submitted_date', 'N/A')
            })

        # Calculate processing completion rate
        if report['total_payments'] > 0:
            completed = report['by_status'].get('paid', 0)
            report['processing_completion_rate'] = (completed / report['total_payments']) * 100

        return report

    def print_workflow_summary(self):
        """Print a formatted summary of the workflow"""
        report = self.generate_workflow_report()

        print("=" * 60)
        print("SUBSCRIPTION PAYMENT WORKFLOW DASHBOARD")
        print("=" * 60)
        print(f"Report Generated: {report['report_generated']}")
        print()
        print("PAYMENT SUMMARY:")
        print(f"  Total Payments: {report['total_payments']}")
        print(f"  Total Amount Processed: ${report['total_amount_processed']:,.2f}")
        print(f"  Processing Completion Rate: {report['processing_completion_rate']:.1f}%")
        print()
        print("PAYMENTS BY STATUS:")
        for status, count in report['by_status'].items():
            print(f"  {status.upper()}: {count}")
        print()
        print("RECENT PAYMENTS:")
        for payment in report['recent_payments']:
            print(f"  #{payment['id']} - ${payment['amount']} - {payment['vendor']} - {payment['status']}")
        print("=" * 60)

    def export_workflow_data(self, filename: str = "workflow_export.json"):
        """Export all workflow data to a JSON file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "payments": self.payment_system.view_payment_history(),
            "post_approval_logs": self.processor.processing_logs,
            "accounting_ledger": []
        }

        # Load accounting ledger if it exists
        if os.path.exists("accounting_ledger.json"):
            with open("accounting_ledger.json", 'r') as f:
                export_data["accounting_ledger"] = json.load(f)

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"Workflow data exported to {filename}")


def main():
    """Main function for the dashboard"""
    dashboard = WorkflowDashboard()

    while True:
        print("\nWorkflow Dashboard Options:")
        print("1. View workflow summary report")
        print("2. Export workflow data")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            dashboard.print_workflow_summary()

        elif choice == "2":
            filename = input("Enter export filename (default: workflow_export.json): ").strip()
            if not filename:
                filename = "workflow_export.json"
            dashboard.export_workflow_data(filename)

        elif choice == "3":
            print("Exiting dashboard...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()