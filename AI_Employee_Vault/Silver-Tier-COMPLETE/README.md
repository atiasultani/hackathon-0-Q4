# Silver Tier AI Employee - Personal Automation Assistant

## Overview

This is a local-first, semi-autonomous AI employee system that operates with human-in-the-loop oversight. The system follows a structured workflow for processing tasks, requesting approvals for sensitive actions, and maintaining a complete audit trail.

## Architecture

The system follows the Read → Think → Plan → Write → Request Approval workflow:

1. **Read** `/Needs_Action/` for new task files
2. **Interpret** the content and determine required actions
3. **Create** `/Plans/PLAN_<task>.md` with structured execution steps
4. **Request Approval** for sensitive actions via `/Pending_Approval/`
5. **Execute** approved actions via MCP servers
6. **Log** all actions to `/Logs/YYYY-MM-DD.json`
7. **Move** completed tasks to `/Done/`
8. **Update** `Dashboard.md`

## Project Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status summary
├── Company_Handbook.md       # AI behavior rules
├── CLAUDE.md                 # Operating instructions
├── README.md                 # This file
│
├── Needs_Action/             # Incoming tasks from Watchers
├── Plans/                    # Execution plans
├── Pending_Approval/         # Actions awaiting human approval
├── Approved/                 # Human-approved actions ready for execution
├── Rejected/                 # Denied actions
├── Done/                     # Completed tasks
└── Logs/                     # Audit trail (JSON)
└── automation/               # Core system scripts
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AI_Employee_Vault/Silver-Tier-COMPLETE
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Operation Guide

### Starting the System

To start the AI employee system, run:

```bash
python automation/run_system.py
```

Or directly run the orchestrator:

```bash
python automation/orchestrator.py
```

### Processing Tasks

#### Adding New Tasks

To add a new task for the AI employee, create a markdown file in the `/Needs_Action/` directory:

```bash
echo "# New Task
Send an email to john@example.com about the quarterly report" > Needs_Action/new_task.md
```

#### Automatic Processing

The system continuously monitors the `/Needs_Action/` directory and will:

1. Automatically detect new task files
2. Create a corresponding plan in `/Plans/`
3. Determine if approval is required
4. If approval is needed, create an approval request in `/Pending_Approval/`
5. Move the original task to `/Done/` (approval file tracks the action)
6. If no approval is needed, move the task directly to `/Done/`

#### Approval Process

For sensitive actions (emails, payments, social media posts), the system will:

1. Create an approval request in `/Pending_Approval/`
2. Wait for human approval before executing

To approve an action:
```bash
mv Pending_Approval/ACTION_*.md Approved/
```

To reject an action:
```bash
mv Pending_Approval/ACTION_*.md Rejected/
```

### Monitoring System Status

Check the `Dashboard.md` file for real-time status information:
- System status (RUNNING/STOPPED)
- Task metrics (pending, approval, completed)
- Recent activity
- Directory status

### Checking Logs

View the daily logs in the `/Logs/` directory (e.g., `Logs/2026-03-04.json`) for a complete audit trail of all actions.

## Security Features

### Approval Requirements

The system requires human approval for:
- ✉️ Sending emails
- 📱 LinkedIn/social media posts
- 💰 Payments or financial transactions
- 👥 Creating new contacts
- 📢 Any public-facing communication
- 🔐 Actions involving sensitive data

### Auto-Executable Actions

The system can auto-execute without approval:
- Internal file organization
- Drafting content (without sending)
- Reading/searching data
- Updating Dashboard
- Creating logs

### Audit Trail

All actions are logged with:
- Timestamp
- Action type
- Target
- Approval status
- Result
- Plan reference
- Additional details

## Configuration

### Environment Variables

Create a `.env` file to store sensitive information:
```
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-app-password
LINKEDIN_TOKEN=your-linkedin-token
```

### System Settings

Adjust settings in the `automation/orchestrator.py` file:
- Polling intervals
- Directory paths
- Logging configuration

## Troubleshooting

### System Not Responding

1. Check that the orchestrator is running
2. Verify file permissions in all directories
3. Review logs for error messages

### Failed Actions

1. Check the `Dashboard.md` for failed task notices
2. Look for files with `_FAILED` suffix in `/Needs_Action/`
3. Review the corresponding logs for error details

### Approval Not Working

1. Ensure files are moved to the correct directories (`/Approved/` or `/Rejected/`)
2. Check that the orchestrator is monitoring the `/Approved/` directory

## Development

### Adding New MCP Servers

To extend the system with new capabilities:
1. Create a new MCP server script in the `automation/` directory
2. Update the orchestrator to recognize and call the new server
3. Add appropriate approval checks for the new action type

### Customizing Workflows

Modify the `automation/orchestrator.py` to customize:
- Approval heuristics
- Task processing logic
- Notification systems
- Error handling

## Best Practices

- Always monitor the dashboard for system status
- Regularly review logs for audit purposes
- Keep approval requests clear and concise
- Test new workflows in a separate branch first
- Maintain backup copies of important data

## Support

For support with this system:
- Review the `CLAUDE.md` file for detailed operational procedures
- Check the logs for troubleshooting information
- Report issues through the repository's issue tracker