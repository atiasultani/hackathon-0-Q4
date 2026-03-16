# AI Employee Vault — Backend

**Gold Tier** autonomous AI employee system — a fully autonomous, cross-domain, local-first Digital FTE (Full-Time Employee). Processes business tasks across accounting, communication, marketing, and executive reporting with human oversight for sensitive operations.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Perception Layer (Watchers)                       │
│  ┌────────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐ │
│  │   Gmail    │ │  WhatsApp   │ │  LinkedIn  │ │ Calendar │ │  Social  │ │
│  │  Watcher   │ │   Watcher   │ │  Watcher   │ │ Watcher  │ │ Watcher  │ │
│  └─────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘ └────┬─────┘ │
│        │               │              │             │            │         │
│  ┌─────┴──────┐ ┌──────┴──────┐ ┌─────┴──────┐ ┌────┴─────┐ ┌───┴──────┐│
│  │  Finance   │ │    File     │ │            │ │          │ │          ││
│  │  Watcher   │ │   Watcher   │ │            │ │          │ │          ││
│  └─────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘ └───┬──────┘│
│        │               │              │             │            │         │
│        └───────────────┴──────────────┴─────┬───────┴────────────┘         │
│                                             ▼                               │
│                                    Needs_Action/                            │
│                                             │                               │
├─────────────────────────────────────────────┼───────────────────────────────┤
│                                             ▼     Orchestration Layer       │
│                                  ┌─────────────────┐                        │
│                                  │  run_system.py  │ (Entry Point)          │
│                                  └────────┬────────┘                        │
│                                           │                                 │
│              ┌────────────────┬───────────┼───────────┬──────────┐         │
│              ▼                ▼           ▼           ▼          ▼         │
│        ┌──────────┐   ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐   │
│        │Orchestr. │   │ AI Router│ │ Scheduler│ │Ralph    │ │  API   │   │
│        │ :monitor │   │:classify │ │  :cron   │ │ Loop    │ │ Server │   │
│        └────┬─────┘   └──────────┘ └──────────┘ └─────────┘ └───┬────┘   │
│             │                                                    │         │
│             ▼                                                    ▼         │
│  ┌──────────────────────────────────────────────────┐   ┌──────────────┐  │
│  │            Action Layer (MCP Servers)             │   │  Frontend    │  │
│  ├──────────┬──────────┬──────────┬──────────┬───────┤   │ (golden-ui)  │  │
│  │  Email   │  Odoo    │ Browser  │ Calendar │ Social│   │  port 3000   │  │
│  │  :8001   │  :8003   │  :8008   │  :8009   │ :8004 │   └──────────────┘  │
│  └──────────┴──────────┴──────────┴──────────┴───────┘                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Vault (Obsidian) — Local-first state management & audit trail              │
│  Needs_Action → Plans → Pending_Approval → Approved → Done                  │
│  Logs/ (90-day retention)  │  Dashboard.md (real-time metrics)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
backend/
├── .env                          # Environment variables (not committed)
├── .env.example                  # Environment template with all options
├── requirements.txt              # Python dependencies (48 packages)
├── README.md                     # This file
├── CLAUDE.md                     # AI instructions for task processing
├── SYSTEM_ARCHITECTURE.md        # Gold Tier architecture specification
├── Business_Goals.md             # Revenue targets and KPIs
├── Company_Handbook.md           # Behavior rules and policies
├── Dashboard.md                  # Real-time executive overview
│
├── api_server.py                 # REST API for frontend dashboard (port 8000)
│
├── orchestration/                # Core orchestration layer
│   ├── run_system.py             # Entry point — starts all MCP servers
│   ├── orchestrator.py           # Central controller: monitoring, routing, MCP dispatch
│   ├── scheduler.py              # Cron-based scheduled jobs
│   ├── ai_router.py              # Claude-powered task classification (accounting/ops/executive)
│   └── ralph_loop.py             # Persistent multi-step execution engine
│
├── mcp/                          # MCP (Model Context Protocol) servers
│   ├── email_mcp_server.py       # Email send/draft/search (port 8001)
│   ├── linkedin_mcp_server.py    # LinkedIn posting (port 8002)
│   ├── social_media_mcp_server.py# Unified social: Facebook, Instagram, X (port 8004)
│   ├── odoo_mcp_server.py        # Odoo ERP: invoices, payments, accounting (port 8003)
│   ├── browser_mcp_server.py     # Playwright browser automation for payments (port 8008)
│   ├── calendar_mcp_server.py    # Google Calendar events (port 8009)
│   ├── facebook_mcp_server.py    # Facebook page posting (port 8005)
│   ├── instagram_mcp_server.py   # Instagram business posting (port 8006)
│   └── x_mcp_server.py           # X/Twitter posting (port 8007)
│
├── watchers/                     # Perception layer — monitors external systems
│   ├── gmail_watcher.py          # Monitors Gmail for important emails
│   ├── whatsapp_watcher.py       # Monitors WhatsApp for client messages
│   ├── linkedin_watcher.py       # Monitors LinkedIn engagement (mentions, messages)
│   ├── calendar_watcher.py       # Monitors calendar events and creates reminders
│   ├── social_watcher.py         # Monitors Facebook, Instagram, X for engagement
│   ├── finance_watcher.py        # Monitors bank transactions (Plaid/Stripe/Custom)
│   ├── file_watcher.py           # Watches drop folder for new project files
│   └── watcher_system.py         # Legacy watcher manager (deprecated)
│
├── Needs_Action/                 # Incoming tasks awaiting processing
├── Plans/                        # Generated execution plans (YAML + checkboxes)
├── Pending_Approval/             # Tasks awaiting human approval
├── Approved/                     # Approved tasks ready for execution
├── Rejected/                     # Rejected tasks
├── Done/                         # Completed tasks
├── Active_Projects/              # Current projects in progress
├── Logs/                         # JSON audit logs (90-day retention)
├── Briefings/                    # Weekly CEO business briefings
├── Accounting/                   # Transaction records and reconciliation
├── Invoices/                     # Invoice documents
├── Drafts/                       # Draft content (social posts, emails)
└── integrations/                 # OAuth credentials (Gmail, Google Calendar)
```

## Prerequisites

- **Python** 3.10 or higher (tested on 3.12)
- **pip** (Python package manager)
- **Node.js** 18+ (for frontend)
- **Anthropic API key** (required — for AI routing and task classification)
- **Google OAuth credentials** (optional — for Gmail and Calendar)
- **Odoo ERP instance** (optional — for accounting and invoicing)
- **Social media API keys** (optional — for Facebook, Instagram, X, LinkedIn)
- **Bank API credentials** (optional — for finance watcher: Plaid/Stripe/Custom)

## Installation

### 1. Clone and navigate

```bash
git clone <repository-url>
cd Golden-COMPLETED/backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs 48 packages including:
- `anthropic` — Claude API for AI routing
- `fastapi`, `uvicorn` — API server and MCP server framework
- `aiohttp`, `requests` — HTTP clients
- `playwright` — Browser automation
- `google-api-python-client` — Google services (Calendar, Gmail)
- `schedule` — Cron job scheduling

### 4. Install Playwright browsers (if using payment automation)

```bash
playwright install chromium
```

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Optional — Odoo ERP
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password

# Optional — Google Calendar
GOOGLE_CALENDAR_ID=primary

# Optional — Social Media APIs
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
X_API_KEY=your_twitter_key
X_API_SECRET=your_twitter_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret

# Optional — LinkedIn API (for LinkedIn Watcher)
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_PERSON_ID=your_person_id

# Optional — Bank API (for Finance Watcher)
BANK_API_PROVIDER=plaid  # or stripe, custom
BANK_API_KEY=your_bank_key
BANK_API_SECRET=your_bank_secret
BANK_ACCOUNT_ID=your_account_id
```

### 6. Set up Google OAuth (optional — Gmail and Calendar)

Place your Google OAuth credentials file at:
```
integrations/gmail/credentials.json
```

The token (`integrations/gmail/token.json`) is generated automatically on first use.

### 7. Install frontend dependencies (if using dashboard)

```bash
cd ../golden-ui
npm install
```

## Running the System

### Option 1: Run Backend + Frontend Together

```bash
cd Golden-COMPLETED
python run_all.py
```

This starts:
- **API Server** on http://localhost:8000
- **Frontend Dashboard** on http://localhost:3000

### Option 2: Run Backend Only

#### Start MCP servers and orchestration

```bash
cd backend
python -m orchestration.run_system
```

This starts 7 components in order:

1. **Orchestrator** — monitors directories, routes tasks, dispatches MCP calls
2. **Email MCP Server** (port 8001) — send, draft, and search emails
3. **LinkedIn MCP Server** (port 8002) — publish and draft LinkedIn posts
4. **Odoo MCP Server** (port 8003) — create invoices, process payments, accounting
5. **Browser MCP Server** (port 8008) — automate payment portals via Playwright
6. **Calendar MCP Server** (port 8009) — create and manage calendar events
7. **Scheduler** — runs periodic jobs in the background

#### Start API Server (for frontend dashboard)

```bash
cd backend
python -m api_server
```

API available at http://localhost:8000 with docs at http://localhost:8000/docs

### Option 3: Start Frontend Only

```bash
cd golden-ui
npm run dev
```

Dashboard at http://localhost:3000 (requires API server running)

### Stop the system

Press `Ctrl+C`. All child processes shut down gracefully with termination logging.

### Run individual components

For development or debugging, run components independently:

```bash
# Core orchestration
python -m orchestration.orchestrator
python -m orchestration.scheduler
python -m orchestration.ralph_loop
python -m orchestration.ai_router

# API Server
python -m api_server

# MCP servers
python -m mcp.email_mcp_server
python -m mcp.odoo_mcp_server
python -m mcp.browser_mcp_server
python -m mcp.calendar_mcp_server
python -m mcp.social_media_mcp_server

# Watchers
python -m watchers.gmail_watcher
python -m watchers.whatsapp_watcher
python -m watchers.linkedin_watcher
python -m watchers.calendar_watcher
python -m watchers.social_watcher
python -m watchers.finance_watcher
python -m watchers.file_watcher
```

## API Server Reference (Port 8000)

The API server provides REST endpoints for the frontend dashboard:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/dashboard/stats` | GET | Dashboard statistics |
| `/api/system/status` | GET | System component status |
| `/api/tasks` | GET | List all tasks (paginated) |
| `/api/tasks/{id}` | GET | Get specific task |
| `/api/approvals` | GET | List pending approvals |
| `/api/approvals/{id}/approve` | POST | Approve a request |
| `/api/approvals/{id}/reject` | POST | Reject a request |
| `/api/finance/summary` | GET | Financial summary |
| `/api/logs` | GET | Audit logs (paginated) |
| `/api/social/posts` | GET | Social media posts |
| `/api/system/start` | POST | Start backend system |
| `/api/system/stop` | POST | Stop backend system |
| `/api/system/restart` | POST | Restart backend system |

## MCP Server Reference

| Server | Port | Endpoints | Auth Method |
|--------|------|-----------|-------------|
| Email | 8001 | `/send-email`, `/draft-email`, `/search-emails`, `/health` | Google OAuth2 |
| LinkedIn | 8002 | `/publish-post`, `/draft-post`, `/published-posts`, `/health` | MCP internal |
| Social Media | 8004 | `/post_content` | API tokens (env) |
| Odoo | 8003 | `/create_invoice`, `/get_invoices`, `/health` | XML-RPC credentials |
| Browser | 8008 | `/create_session`, `/process_payment`, `/close_session` | Playwright |
| Calendar | 8009 | `/create_event`, `/list_events`, `/delete_event`, `/health` | Google OAuth2 |
| Facebook | 8005 | `/post_content` | Page access token |
| Instagram | 8006 | `/post_content` | Business account token |
| X (Twitter) | 8007 | `/post_content` | OAuth1.0a (API key/secret) |

## Watcher Reference

Watchers monitor external systems and create task files in `Needs_Action/`.

| Watcher | Monitors | Mode | Required Credentials |
|---------|----------|------|---------------------|
| Gmail | Inbox for unread emails | Mock/Real | `integrations/gmail/credentials.json` |
| WhatsApp | Client messages | Mock/Real | Playwright browser |
| LinkedIn | Mentions, messages, connections | Mock/Real | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_ID` |
| Calendar | Upcoming events & reminders | Mock/Real | Google OAuth (same as Gmail) |
| Social | Facebook, Instagram, X engagement | Mock/Real | `FACEBOOK_*`, `INSTAGRAM_*`, `X_*` tokens |
| Finance | Bank transactions | Mock/Real | `BANK_API_PROVIDER`, `BANK_API_KEY` |
| File | Drop folder for project files | Always Real | None |

**Mock mode:** Watchers simulate events randomly for testing without API credentials.
**Real mode:** Watchers use actual APIs when credentials are set in `.env`.

## How It Works

### Task Lifecycle

```
Needs_Action ──► Plans ──► Pending_Approval ──► Approved ──► Done
                     │                              │
                     ▼                              ▼
               (auto-execute                  (MCP execution
                if no approval                via orchestrator)
                required)
```

### 1. Task Ingestion

Drop a `.md` file into `Needs_Action/`. The orchestrator scans every 10 seconds.

**Watcher automation** creates task files automatically:
- Gmail watcher monitors inbox for important emails
- WhatsApp watcher monitors client messages
- LinkedIn watcher monitors mentions and messages
- Calendar watcher creates reminders for upcoming events
- Social watcher monitors Facebook, Instagram, X engagement
- Finance watcher monitors bank transactions
- File watcher monitors the drop folder for new files

### 2. AI Classification

The AI router (`ai_router.py`) classifies each task into one of three domains:
- **accounting** — payments, invoices, financial operations
- **operations** — email, social media, general tasks
- **executive** — reports, summaries, strategic analysis

Uses Claude Haiku for fast classification with keyword-based fallback.

### 3. Plan Generation

Claude creates a structured plan in `Plans/` with:
- YAML frontmatter: `created`, `domain`, `status`
- Checkbox-based step tracking: `- [ ]` pending, `- [x]` completed
- Objective statement and verification steps

### 4. Approval Gate (Human-in-the-Loop)

Tasks containing these keywords require human approval:
- `email`, `send`, `payment`, `post`, `linkedin`

Approval files are created in `Pending_Approval/`. **To approve:** move to `Approved/`. **To reject:** move to `Rejected/`.

You can also approve/reject via the dashboard at http://localhost:3000/approvals

### 5. MCP Execution

Approved tasks are routed to the appropriate MCP server:
- Email tasks → Email MCP
- Social/LinkedIn tasks → Social Media MCP
- Invoice/accounting tasks → Odoo MCP
- Payment tasks → Browser MCP
- Calendar tasks → Calendar MCP

### 6. Completion

Successful tasks move to `Done/`. Failures return to `Needs_Action/` with a `_FAILED` suffix for manual review.

### Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Morning Summary | Daily at 08:00 | Generate daily status log in `Logs/` |
| LinkedIn Post | Monday at 10:00 | Create LinkedIn post draft in `Pending_Approval/` |
| Inbox Sweep | Every 10 minutes | Monitor and log system activity |

## Business Capabilities

### Financial Management (Odoo Integration)
- Invoice creation and tracking via Odoo ERP
- Payment processing with approval workflows
- Revenue reporting and reconciliation
- Accounting ledger management

### Communication Management
- Email triage, drafting, and sending
- WhatsApp client communication monitoring
- Calendar event scheduling and meeting coordination

### Marketing Automation
- LinkedIn content posting and engagement monitoring
- Facebook page management
- Instagram business posting
- X/Twitter engagement
- Cross-platform social media coordination

### Executive Reporting
- Weekly CEO briefings (generated Sunday night)
- Revenue summaries from Odoo
- KPI comparison against `Business_Goals.md`
- Bottleneck identification and proactive suggestions

### Payment Processing
- Browser automation for payment portals (Playwright/Chromium)
- Form filling and navigation
- Screenshot verification
- Multi-portal support

## Human-in-the-Loop (HITL) Rules

| Action | Approval Threshold |
|--------|-------------------|
| Payments | Over $100, or recurring over $50 |
| Public social media | Any public post |
| New contact communication | Any new recipient |
| Financial changes | Invoice sending, accounting modifications |
| Email sending | Any outgoing email |

## Error Handling

| Error Type | Recovery Strategy |
|------------|-------------------|
| Network errors | Exponential retry backoff |
| Authentication failures | Pause execution and alert |
| Logic errors | Route to review queue |
| File corruption | Quarantine file for manual review |
| MCP server down | Graceful degradation with logging |
| Process crash | Automatic restart with backoff |

**No silent failures** — all errors are logged and surfaced.

## Audit Logging

All actions logged to `Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-03-14T08:30:00.000Z",
  "action_type": "email_send",
  "target": "ACTION_email_task.md",
  "approval_status": "approved",
  "result": "success"
}
```

- Format: JSON array of log entries
- Retention: 90 days minimum
- Rotation: Daily log files

## Health Checks

### API Server
```bash
curl http://localhost:8000/health
```

### MCP Servers
```bash
curl http://localhost:8001/health    # Email
curl http://localhost:8003/health    # Odoo
curl http://localhost:8008/health    # Browser
curl http://localhost:8009/health    # Calendar
```

Expected response:
```json
{"status": "ok", "service": "<service-name>"}
```

## Troubleshooting

### System won't start

```bash
# Verify dependencies
pip install -r requirements.txt

# Check .env exists and has required variables
cat .env | grep ANTHROPIC_API_KEY

# Verify Python version
python --version  # Must be 3.10+
```

### Port conflicts

```bash
# Linux/macOS — find process using port
lsof -i :8000
kill <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Tasks not being processed

1. Verify `Needs_Action/` contains `.md` files
2. Check orchestrator is running (`run_system.py` output)
3. Review `Logs/` for error entries
4. Ensure `ANTHROPIC_API_KEY` is valid

### Approval workflow stuck

1. Check `Pending_Approval/` for files awaiting review
2. Move approved files to `Approved/` or rejected files to `Rejected/`
3. Orchestrator processes approved files within 10 seconds

### MCP server not responding

```bash
# Check if server is running
curl http://localhost:<port>/health

# Restart specific server
python -m mcp.<server_name>
```

### Frontend not connecting to backend

1. Verify API server is running: `curl http://localhost:8000/health`
2. Check `BACKEND_URL` in `golden-ui/next.config.js`
3. Ensure CORS is enabled (default: allows localhost:3000)

## Development

### Code structure

- **API Server** (`api_server.py`) — REST API for frontend dashboard
- **Orchestration** (`orchestration/`) — Core logic, directory monitoring, MCP dispatch
- **MCP servers** (`mcp/`) — Protocol implementations, each independent
- **Watchers** (`watchers/`) — External system monitors with mock/real API support
- **AI Router** (`ai_router.py`) — Claude Haiku classification with keyword fallback
- **Frontend** (`../golden-ui/`) — Next.js dashboard

### Adding a new MCP server

1. Create `mcp/your_service_mcp_server.py`
2. Implement `/health` endpoint
3. Add startup entry in `run_system.py`
4. Add execution handler in `orchestrator.py`
5. Update port table in this README

### Adding a new watcher

1. Create `watchers/your_watcher.py`
2. Implement mock mode (random event simulation)
3. Implement real API mode (check credentials via `os.getenv`)
4. Use `create_task_from_*` function to create task files in `Needs_Action/`
5. Add credentials to `.env.example`

### Running tests

```bash
python -m pytest tests/ -v
```

## Security

- Never commit `.env` to version control
- Rotate API keys regularly
- Payments over $100 always require human approval
- Audit logs retained for 90 days
- Sensitive files excluded via `.gitignore`
- Local-first architecture — data stays on your machine

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI | Anthropic Claude (Haiku for routing) |
| API Server | FastAPI, Uvicorn |
| Web Framework | FastAPI, Uvicorn, Starlette |
| HTTP | aiohttp, requests |
| Browser Automation | Playwright (Chromium) |
| Google Services | google-api-python-client, OAuth2 |
| ERP | Odoo XML-RPC |
| Bank APIs | Plaid, Stripe, Custom |
| Scheduling | Python schedule library |
| Validation | Pydantic |
| State Management | Obsidian vault (markdown files) |
| Frontend | Next.js 14, React 18, Tailwind CSS, Zustand |

## Full System Ports

| Service | Port | Purpose |
|---------|------|---------|
| API Server | 8000 | Frontend dashboard API |
| Email MCP | 8001 | Email operations |
| LinkedIn MCP | 8002 | LinkedIn posting |
| Odoo MCP | 8003 | ERP/accounting |
| Social Media MCP | 8004 | Unified social posting |
| Facebook MCP | 8005 | Facebook posting |
| Instagram MCP | 8006 | Instagram posting |
| X MCP | 8007 | X/Twitter posting |
| Browser MCP | 8008 | Payment automation |
| Calendar MCP | 8009 | Calendar events |
| Frontend | 3000 | Dashboard UI |

## License

Proprietary — All rights reserved.
