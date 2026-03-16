🥇 Gold Tier – System Architecture

Personal AI Employee – Autonomous Cross-Domain FTE

1. Overview

The Gold Tier AI Employee is a fully autonomous, cross-domain, local-first Digital FTE built under the architecture defined in:

Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026

Gold Tier extends Silver by adding:

Full Personal + Business integration

Odoo accounting system integration

Multi-MCP architecture

Social media cross-posting (LinkedIn, Facebook, Instagram, X)

Weekly autonomous CEO audit

Ralph Wiggum loop (persistent multi-step execution)

Error recovery + graceful degradation

Comprehensive audit logging

This tier transforms the assistant into a true Autonomous Employee.

2. Architectural Philosophy

Gold Tier follows five core principles:

Local-first privacy architecture

Structured reasoning via Plan.md

File-based state machine

Human-in-the-loop for sensitive actions

Persistent autonomous completion (Ralph loop)

3. System Layers Overview
Perception → Vault → Reasoning → Planning → Approval → Action → Audit → Review
4. Core Architecture Layers
4.1 Perception Layer (Watchers)

Gold Tier requires multi-domain monitoring.

Watcher Types
Watcher	Purpose
Gmail Watcher	Email triage
WhatsApp Watcher	Client communication
Finance Watcher	Bank transactions
File Watcher	Local project drops
Social Watcher	Engagement monitoring

All watchers:

Run as persistent processes

Create structured markdown files

Write into /Needs_Action/

Never perform actions directly

Watcher Output Format

Example:

---
type: email
source: gmail
priority: high
requires_financial_review: true
status: pending
---

This ensures structured reasoning input.

4.2 Knowledge & State Layer – Obsidian Vault

Gold Tier vault structure:

AI_Employee_Vault/
│
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
│
├── Needs_Action/
├── Plans/
├── Active_Projects/
├── Accounting/
├── Briefings/
├── Invoices/
│
├── Pending_Approval/
├── Approved/
├── Rejected/
│
├── Logs/
├── Done/
Key Documents
File	Purpose
Company_Handbook.md	Behavior rules
Business_Goals.md	Revenue + KPI tracking
Dashboard.md	Real-time executive overview
Briefings/*	Weekly CEO briefings
Accounting/*	Transaction logs + reconciliation

Vault acts as:

Memory

State machine

Audit ledger

GUI

4.3 Reasoning Layer – Claude Code

Claude Code is the core decision engine.

Responsibilities:

Reads /Needs_Action, /Accounting, /Business_Goals

Generates /Plans/PLAN_*.md

Determines approval boundaries

Triggers MCP servers

Generates CEO briefings

Updates dashboard

Gold Tier includes:

Ralph Wiggum Persistent Loop

Claude does not exit until task completion.

Workflow:

1. Orchestrator triggers Claude
2. Claude works
3. Stop hook checks completion
4. If incomplete → reinject prompt
5. Repeat until file moved to /Done

This guarantees multi-step execution reliability.

4.4 Planning System (Plan.md Architecture)

Every major task generates a structured plan.

Example:

---
created: 2026-01-07
domain: finance
status: in_progress
---

## Objective
Generate invoice and reconcile payment

## Steps
- [x] Identify client
- [x] Calculate amount
- [ ] Create invoice in Odoo
- [ ] Send via email (approval required)
- [ ] Log in accounting
- [ ] Update dashboard

Plans are executable state documents.

4.5 Action Layer – Multi-MCP Architecture

Gold Tier requires multiple MCP servers.

Required MCP Servers
MCP	Purpose
Email MCP	Send + draft emails
Browser MCP	Payment portals
Calendar MCP	Event scheduling
Social MCP	Social posting
Odoo MCP	Accounting integration
Odoo Integration (Mandatory for Gold)

Gold Tier requires:

Integration with Odoo Community (19+)

Capabilities:

Create invoices

Draft payments

Log accounting entries

Pull revenue reports

Read ledger entries

Architecture:

Claude → Odoo MCP → Odoo JSON-RPC API → Odoo Database

Accounting becomes structured, not markdown-only.

4.6 Social Media Automation (Full Cross-Posting)

Gold Tier must support:

LinkedIn posting

Facebook posting

Instagram posting

X (Twitter) posting

Workflow:

Claude generates post

Creates approval file

Human approves

Social MCP posts

Logs action

Analytics summary written back to Vault

4.7 Human-in-the-Loop (HITL)

Mandatory for:

Payments

Public posts

New recipients

Financial changes

Invoice sending

Approval Flow:

Claude → /Pending_Approval
Human → Move to /Approved
Orchestrator → Execute MCP
Log → Move to /Done

No auto-payment allowed.

5. Weekly Autonomous CEO Briefing

Gold Tier includes:

Scheduled Business Audit

Trigger:

Every Sunday night (cron)

Process:

Claude reads:

Business_Goals.md

Accounting entries

Completed tasks

Odoo revenue data

Generates:

/Briefings/YYYY-MM-DD_Monday_Briefing.md

Includes:

Revenue summary

KPI comparison

Bottlenecks

Subscription waste detection

Proactive suggestions

This shifts AI from reactive to executive.

6. Orchestration Layer
Orchestrator.py

Central controller.

Responsibilities:

Monitor folders

Trigger Claude

Monitor approvals

Call MCP servers

Manage Ralph loop

Handle scheduling

Watchdog Process

Monitors:

Watchers

Orchestrator

MCP servers

Auto-restarts on failure.

7. Error Handling & Resilience

Gold Tier requires structured recovery.

Error Categories
Type	Handling
Network	Exponential retry
Authentication	Pause + alert
Logic	Route to review queue
Corruption	Quarantine file
System crash	Auto-restart
Graceful Degradation

Examples:

Gmail API down → queue emails

Banking API failure → never auto-retry payments

Claude offline → queue grows, processed later

System must never silently fail.

8. Security Architecture
Credential Management

Environment variables

.env excluded from git

Secrets manager for banking

Token rotation

Permission Boundaries
Category	Auto	Approval Required
Email reply (known)	Yes	New contacts
Payment	< $50 recurring	> $100
Social posts	Scheduled drafts	Public replies
Accounting entry	Draft	Posting
Audit Logging

Every action logged in:

/Logs/YYYY-MM-DD.json

Format:

{
  "timestamp": "...",
  "action_type": "payment",
  "approval_status": "approved",
  "result": "success"
}

Minimum retention: 90 days.

9. End-to-End Autonomous Invoice Flow (Gold)

WhatsApp message detected

Watcher writes file

Claude creates Plan

Invoice created in Odoo

Approval file generated

Human approves

Email MCP sends invoice

Odoo marks draft → posted

Accounting updated

Dashboard updated

Logs written

Files moved to Done

All steps persistent under Ralph loop.

10. Gold Tier Architecture Diagram
External Systems
   │
   ▼
Watchers (Multi-Domain)
   │
   ▼
Obsidian Vault (State + Memory)
   │
   ▼
Claude Code (Reasoning + Planning)
   │
   ├── Plan Generation
   ├── Approval Requests
   ├── CEO Audit
   │
   ▼
Human Approval
   │
   ▼
Multi-MCP Layer
   │
   ├── Email
   ├── Social
   ├── Browser
   ├── Calendar
   ├── Odoo
   │
   ▼
External Actions
   │
   ▼
Logs + Dashboard + Done
11. What Gold Tier Achieves

Cross-domain autonomy

Structured accounting integration

Weekly executive insights

Persistent task completion

Financial reconciliation

Multi-channel marketing automation

Robust recovery system

12. Gold Tier Deliverable Checklist

✅ All Silver features
✅ Multi-MCP servers
✅ Odoo accounting integration
✅ Facebook + Instagram + X integration
✅ Weekly CEO Briefing automation
✅ Ralph Wiggum loop
✅ Full audit logging
✅ Error recovery framework
✅ Cross-domain task orchestration

13. Architectural Strengths

Local-first privacy

Financial-grade control boundaries

Persistent multi-step completion

Executive-level insight generation

Modular expansion ready for Platinum