# AI Employee - Bronze Architecture

## Core Workflow

1. New tasks are created in /Needs_Action
2. Claude generates execution plans in /Plans
3. Tasks requiring approval move to /Pending_Approval
4. Human moves files to /Approved or /Rejected
5. Approved tasks are executed
6. Logs are generated in /Logs
7. Completed items move to /Done

## Human-in-the-Loop

- No financial or email action happens without approval.
- Folder movement = state change.

## Security Model

- Payments above $100 require approval.
- Credentials are never exposed.
