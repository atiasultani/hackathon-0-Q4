# Silver Tier AI Employee System

This is a complete implementation of the Silver Tier AI Employee system as defined in the SYSTEM_ARCHITECTURE.md document.

## Architecture Overview

The system follows the perception → reasoning → approval → action → logging → completion cycle:

```
External Sources
   │
   ▼
Watchers (Python)
   │
   ▼
/Needs_Action (Vault)
   │
   ▼
Claude Code (Reasoning)
   │
   ├── Create Plan.md
   ├── Create Approval File
   │
   ▼
Human Review
   │
   ▼
/Approved
   │
   ▼
MCP Server (Action)
   │
   ▼
External System (Email / LinkedIn)
   │
   ▼
Logs + /Done
```

## Components Implemented

### 1. Core System Components
- ✅ **Orchestrator** (`orchestrator.py`) - Main control process that coordinates all components
- ✅ **Directory Structure** - Complete vault structure with all required directories
- ✅ **Dashboard** (`Dashboard.md`) - Real-time status summary updated automatically

### 2. Perception Layer (2+ Watchers)
- ✅ **Gmail Watcher** (`gmail_watcher.py`) - Detects important emails and creates tasks
- ✅ **WhatsApp Watcher** (`whatsapp_watcher.py`) - Detects keywords in WhatsApp messages
- ✅ **Post Approval Watcher** (`automation/post_approval_watcher.py`) - Executes approved tasks

### 3. Reasoning Layer
- ✅ **Claude Integration** - The system is designed to work with Claude Code as the reasoning engine
- ✅ **Plan.md Workflow** - Creates structured plans in `/Plans/` directory

### 4. Action Layer (MCP Servers)
- ✅ **Email MCP Server** (`email_mcp_server.py`) - Handles email operations
- ✅ **LinkedIn MCP Server** (`linkedin_mcp_server.py`) - Handles LinkedIn posting

### 5. Human-in-the-Loop (HITL)
- ✅ **Approval Workflow** - Tasks requiring approval go to `/Pending_Approval`
- ✅ **Sensitive Operations** - Human approval required for payments, emails, and public posts

### 6. Additional Features
- ✅ **LinkedIn Auto-Posting** - Automatically generates and posts business-related content
- ✅ **Basic Scheduling** (`scheduler.py`) - Implements cron-like scheduling
- ✅ **Logging System** - Structured JSON logs in `/Logs/` directory
- ✅ **Security Boundaries** - Approval requirements for sensitive operations

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the complete system:
```bash
python run_system.py
```

This will start all components simultaneously:
- Orchestrator
- Email MCP Server (port 8000)
- LinkedIn MCP Server (port 8001)
- Scheduler
- Watchers (run separately if needed)

## Directory Structure
```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status summary
├── Company_Handbook.md       # AI behavior rules
├── Needs_Action/             # Incoming tasks from Watchers
├── Plans/                    # Claude-created execution plans
├── Pending_Approval/         # Sensitive action requests
├── Approved/                 # Human-approved actions
├── Rejected/                 # Human-rejected actions
├── Done/                     # Completed tasks
└── Logs/                     # Audit trail
```

## Key Features

- **Local-first privacy**: All data stored locally in the vault
- **Structured reasoning**: Plan.md files provide clear execution steps
- **Controlled autonomy**: Human approval for sensitive actions
- **File-based state machine**: Clear workflow through directory structure
- **Transparent approval**: Visible approval mechanism
- **Modular watcher system**: Easy to add new watchers

## MCP Server Endpoints

### Email MCP Server (Port 8000)
- `GET /health` - Health check
- `POST /send-email` - Send an email
- `POST /draft-email` - Draft an email
- `POST /search-emails` - Search emails

### LinkedIn MCP Server (Port 8001)
- `GET /health` - Health check
- `POST /publish-post` - Publish a LinkedIn post
- `POST /draft-post` - Draft a LinkedIn post
- `GET /published-posts` - Get published posts

## How to Operate the System

### Prerequisites
- Python 3.8 or higher
- pip package manager
- For Gmail Watcher: Google API credentials (optional, mock mode available)
- For WhatsApp Watcher: Playwright library (optional, mock mode available)

### Installation
1. Clone the repository or navigate to the project directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

To install Playwright for WhatsApp watcher:
```bash
pip install playwright
playwright install chromium
```

### Starting the System
1. Start the complete system with a single command:
```bash
python run_system.py
```

This will start all components simultaneously:
- Orchestrator (coordinates the entire system)
- Email MCP Server (runs on port 8000)
- LinkedIn MCP Server (runs on port 8001)
- Scheduler (handles automated tasks)
- Watchers (monitor external sources)

### Manual Component Management
Alternatively, you can start components individually:

1. **Start Orchestrator** (essential for the system):
```bash
python orchestrator.py
```

2. **Start MCP Servers**:
```bash
python email_mcp_server.py    # Port 8000
python linkedin_mcp_server.py # Port 8001
```

3. **Start Watchers** (run in separate terminals):
```bash
python gmail_watcher.py
python whatsapp_watcher.py
```

4. **Start Scheduler**:
```bash
python scheduler.py
```

## Operating Workflow

### 1. Task Processing
- Watchers detect new tasks (emails, messages) and create files in `/Needs_Action`
- Orchestrator monitors `/Needs_Action` and triggers Claude reasoning
- Claude creates Plan.md files in `/Plans`
- Sensitive tasks are moved to `/Pending_Approval`

### 2. Human Approval Process
- Review files in `/Pending_Approval`
- Move approved files to `/Approved` to execute
- Files requiring human attention remain in `/Pending_Approval`

### 3. Automated Actions
- Once approved, MCP servers execute the requested actions
- Completed tasks are moved to `/Done`
- System logs all activities in `/Logs`

### 4. Monitoring
- Check `Dashboard.md` for real-time system status
- Review logs in `/Logs` for detailed activity records
- Monitor directory sizes for task progression

## How to Implement/Deploy

### Local Development Setup
1. Create a new directory for the AI Employee system
2. Copy all files to the directory
3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Start the system:
```bash
python run_system.py
```

### Production Deployment Considerations
1. **Environment Setup**:
   - Use a dedicated server or container
   - Set up proper user permissions
   - Configure firewall rules for MCP server ports (8000, 8001)

2. **Security Configuration**:
   - Store credentials securely (not in vault)
   - Set up SSL certificates for MCP servers
   - Implement proper backup strategies

3. **Monitoring**:
   - Set up system monitoring tools
   - Configure log rotation
   - Implement alerting for system failures

4. **Cron Jobs** (for scheduling):
   - Add cron entries for automated tasks:
   ```
   */10 * * * * cd /path/to/project && python scheduler.py
   ```

### Customization Options
1. **Adding New Watchers**:
   - Create new Python scripts following the watcher pattern
   - Add to the run_system.py startup script
   - Register with the orchestrator

2. **Extending MCP Servers**:
   - Add new endpoints to existing MCP servers
   - Create additional MCP server modules
   - Update orchestrator to use new endpoints

3. **Modifying Approval Workflows**:
   - Adjust the logic in orchestrator.py for different approval rules
   - Modify the metadata in task files to include more information

## Security Features
- No credentials stored in vault files
- DRY_RUN mode capability for testing
- Approval required for payments, new contacts, and public posts
- Complete audit logging for transparency

## Troubleshooting

### Common Issues
1. **MCP Server Ports Already in Use**:
   - Check if servers are already running
   - Kill existing processes or use different ports

2. **Permission Errors**:
   - Verify file permissions for all directories
   - Ensure Python has write access to all folders

3. **Missing Dependencies**:
   - Run `pip install -r requirements.txt` again
   - Install Playwright if using WhatsApp watcher: `pip install playwright`

### Debugging
- Check log files in `/Logs` directory
- Monitor Dashboard.md for system status
- Use individual component startup for targeted debugging