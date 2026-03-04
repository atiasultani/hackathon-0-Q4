🥈 Silver Tier – System Architecture

Personal AI Employee – Functional Assistant

1. Overview

The Silver Tier AI Employee is a local-first, semi-autonomous functional assistant built using:

Claude Code as the reasoning engine

Obsidian Vault as memory + dashboard

Python Watchers as perception layer

MCP Servers as action layer

Human-in-the-Loop (HITL) for sensitive operations

This tier upgrades Bronze by adding:

Multiple Watchers

LinkedIn auto-posting

Plan.md reasoning loop

One working MCP server

Approval workflow

Basic scheduling

2. High-Level Architecture

The system follows:

Perception → Reasoning → Approval → Action → Logging → Completion
3. Core Components (Silver Tier Scope)
3.1 🧠 Reasoning Layer – Claude Code

Technology: Claude Code CLI
Role: Central decision engine

Responsibilities:

Reads /Needs_Action

Interprets content

Generates /Plans/PLAN_*.md

Writes approval files when required

Updates Dashboard

Moves completed tasks to /Done

Claude operates in:

Read → Think → Plan → Write → Request Approval

All intelligence is implemented as Agent Skills.

3.2 🗂 Memory & Interface – Obsidian Vault

Technology: Obsidian (local markdown vault)

Required Folder Structure (Silver)
AI_Employee_Vault/
│
├── Dashboard.md
├── Company_Handbook.md
│
├── Needs_Action/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Done/
├── Logs/
File Roles
File/Folder	Purpose
Dashboard.md	Real-time status summary
Company_Handbook.md	AI behavior rules
Needs_Action	Incoming tasks from Watchers
Plans	Claude-created execution plans
Pending_Approval	Sensitive action requests
Approved	Human-approved actions
Done	Completed tasks
Logs	Audit trail
4. Perception Layer – Watchers (Minimum Two)

Silver requires 2+ watchers.

4.1 Gmail Watcher (Python + Gmail API)

Detects:

Unread important emails

Creates:

/Needs_Action/EMAIL_<id>.md

Metadata format:

type: email
from: sender@email.com
subject: Example
priority: high
status: pending
4.2 WhatsApp Watcher (Playwright-based)

Detects:

Keywords like "invoice", "urgent", "payment"

Creates:

/Needs_Action/WHATSAPP_<client>.md
4.3 Optional: LinkedIn Watcher / Social Trigger

Can detect:

Post scheduling triggers

Engagement signals

5. Reasoning Output – Plan.md Workflow

When Claude processes /Needs_Action, it creates:

/Plans/PLAN_<task>.md

Example structure:

---
created: 2026-01-07
status: pending_approval
---

## Objective
Reply to client email

## Steps
- [x] Analyze email
- [ ] Draft reply
- [ ] Send (Requires Approval)

This introduces structured execution and traceability.

6. Action Layer – MCP Server (Minimum One Required)

Silver Tier requires at least one working MCP server.

Recommended:

Email MCP Server

Capabilities:

Draft email

Send email

Search emails

Claude triggers MCP only after approval.

Example flow:

Pending_Approval/EMAIL_client.md
↓ (Human moves file)
Approved/EMAIL_client.md
↓
Orchestrator calls MCP
↓
Email sent
↓
Log written
↓
Files moved to Done
7. Human-in-the-Loop (HITL) Architecture

Sensitive actions never auto-execute.

Instead Claude creates:

/Pending_Approval/ACTION_name.md

Example:

type: approval_request
action: send_email
to: client@email.com
amount: 500
status: pending

Human must:

Move file → /Approved/

Only then action executes.

8. LinkedIn Auto-Posting (Silver Feature)

Silver requires:

Automatically post on LinkedIn about business to generate sales

Implementation:

Claude generates post draft

Post saved to:

/Pending_Approval/LINKEDIN_POST_*.md

After approval → MCP triggers posting

This ensures:

No uncontrolled public posts

Marketing automation with oversight

9. Orchestration Layer
9.1 Orchestrator.py

Master control process.

Responsibilities:

Trigger Claude when new files appear

Monitor /Approved

Call MCP servers

Move completed tasks

Update Dashboard

9.2 Scheduling

Silver requires basic scheduling via:

cron (Mac/Linux)

Task Scheduler (Windows)

Example scheduled jobs:

Task	Frequency
Morning summary	Daily 8:00 AM
LinkedIn post	Weekly
Inbox sweep	Every 10 mins
10. Logging & Audit

Every action produces structured logs:

/Logs/YYYY-MM-DD.json

Format:

{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "target": "client@email.com",
  "approval_status": "approved",
  "result": "success"
}

Logs are mandatory for:

Transparency

Debugging

Security review

11. Execution Flow (End-to-End Silver)
Example: Client Requests Invoice

WhatsApp Watcher detects keyword

File created in /Needs_Action

Orchestrator triggers Claude

Claude:

Reads file

Creates Plan.md

Generates invoice

Creates approval file

Human approves

MCP sends email

Logs written

Files moved to /Done

Dashboard updated

12. Security Boundaries (Silver Scope)

No credentials inside vault

.env used for secrets

DRY_RUN mode for testing

Approval required for:

Payments

New contacts

Public posts

13. Silver Tier Architecture Diagram
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
14. What Silver Tier Does NOT Include

Odoo integration

Multi-MCP servers

Ralph Wiggum loop

Full cross-domain integration

24/7 cloud deployment

Accounting system

Weekly CEO audit automation

Those belong to Gold and Platinum.

15. Silver Tier Deliverable Checklist

✅ Obsidian Vault
✅ 2+ Watchers
✅ Claude reasoning loop with Plan.md
✅ LinkedIn auto-post (with approval)
✅ 1 MCP server working
✅ HITL approval workflow
✅ Scheduling via cron/Task Scheduler
✅ Logging system

16. Architectural Strengths (Silver Level)

Local-first privacy

Structured reasoning via Plan.md

Controlled autonomy

File-based state machine

Transparent approval mechanism

Modular watcher system