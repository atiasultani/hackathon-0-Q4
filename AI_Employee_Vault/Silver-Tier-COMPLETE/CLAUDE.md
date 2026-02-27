# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an AI Employee Vault system designed for managing business workflows with human-in-the-loop approval processes. The system focuses on secure handling of financial transactions like software subscriptions while maintaining compliance and audit trails.

## Architecture

The system follows a folder-based workflow where directories represent different states in a task lifecycle:
- `/Needs_Action` - New tasks awaiting processing
- `/Plans` - Execution plans created by Claude
- `/Pending_Approval` - Tasks waiting for human approval
- `/Approved` - Approved tasks ready for execution
- `/Rejected` - Tasks that were denied
- `/Done` - Completed tasks
- `/Logs` - Execution logs and audit trails

Core components include:
- `subscription_payment.py`: Handles payment creation, approval, and processing
- `post_approval_processor.py`: Manages post-approval tasks like notifications and receipts
- `workflow_dashboard.py`: Provides monitoring and reporting capabilities
- Various demo and test scripts that demonstrate the complete workflow

## Key Features

1. **Payment Processing**: Secure handling of subscription payments with approval requirements for amounts over $100
2. **Post-Approval Automation**: Automated vendor notifications, receipt generation, accounting updates, and internal notifications
3. **Audit Trail**: Comprehensive logging of all actions and state changes
4. **Human Oversight**: Mandatory approval for financial transactions

## Common Development Tasks

### Running the Complete Workflow Demo
```bash
python3 complete_workflow_demo.py
```

### Running Individual Components
```bash
# Run the subscription payment system interactively
python3 subscription_payment.py

# Run the post-approval processor
python3 post_approval_processor.py

# Run the workflow dashboard
python3 workflow_dashboard.py

# Run the quick summary
python3 quick_summary.py
```

### Testing
```bash
# Run the test workflow
python3 test_subscription_workflow.py
```

## Important Files

- `payment_log.json` - Stores all payment records with status tracking
- `post_approval_log.json` - Logs all post-approval processing activities
- `accounting_ledger.json` - Financial records for accounting integration
- `receipt_*.json` - Individual receipt files for each payment
- `SYSTEM_ARCHITECTURE.md` - High-level system architecture documentation
- `Company_Handbook.md.md` - Business rules and security policies

## Security Model

- All payments above $100 require explicit human approval
- No financial actions occur without proper authorization
- Credentials are never exposed in the codebase
- Complete audit trail maintained for all transactions