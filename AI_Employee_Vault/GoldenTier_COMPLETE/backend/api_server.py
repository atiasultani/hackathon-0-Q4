#!/usr/bin/env python3
"""
API Server for Gold Tier AI Employee System
Provides REST API for the frontend dashboard (golden-ui)
Runs on port 8000
"""

import os
import json
import glob
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("ERROR: fastapi and uvicorn required. Install with: pip install fastapi uvicorn")
    sys.exit(1)

BASE_PATH = Path(__file__).parent
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
PLANS_DIR = BASE_PATH / "Plans"
PENDING_APPROVAL_DIR = BASE_PATH / "Pending_Approval"
APPROVED_DIR = BASE_PATH / "Approved"
REJECTED_DIR = BASE_PATH / "Rejected"
DONE_DIR = BASE_PATH / "Done"
LOGS_DIR = BASE_PATH / "Logs"
DASHBOARD_FILE = BASE_PATH / "Dashboard.md"
ACCOUNTING_DIR = BASE_PATH / "Accounting"

app = FastAPI(title="AI Employee Vault API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_markdown_file(file_path: Path) -> Dict[str, Any]:
    """Parse markdown file with YAML frontmatter"""
    content = file_path.read_text(encoding='utf-8')
    metadata = {}
    body = content

    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            frontmatter = content[3:end].strip()
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            body = content[end+3:].strip()

    return {
        'id': file_path.stem,
        'filename': file_path.name,
        'metadata': metadata,
        'content': body,
        'created_at': metadata.get('created', metadata.get('received_at', metadata.get('created_at', ''))),
        'status': metadata.get('status', 'unknown'),
        'priority': metadata.get('priority', 'normal'),
        'type': metadata.get('type', 'unknown'),
    }


def count_files(directory: Path) -> int:
    """Count markdown files in directory"""
    if not directory.exists():
        return 0
    return len(list(directory.glob('*.md')))


def get_recent_logs(limit: int = 50) -> List[Dict]:
    """Get recent audit log entries"""
    logs = []
    if not LOGS_DIR.exists():
        return logs

    log_files = sorted(LOGS_DIR.glob('*.json'), reverse=True)
    for log_file in log_files[:7]:  # Last 7 days
        try:
            with open(log_file, 'r') as f:
                entries = json.load(f)
                if isinstance(entries, list):
                    logs.extend(entries)
        except (json.JSONDecodeError, Exception):
            continue

    # Sort by timestamp and limit
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return logs[:limit]


# =============================================================================
# DASHBOARD APIs
# =============================================================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    pending_tasks = count_files(NEEDS_ACTION_DIR)
    pending_approval = count_files(PENDING_APPROVAL_DIR)
    approved = count_files(APPROVED_DIR)
    completed = count_files(DONE_DIR)

    # Count completed today
    today = datetime.now().strftime('%Y-%m-%d')
    completed_today = 0
    if DONE_DIR.exists():
        for f in DONE_DIR.glob('*.md'):
            if today in f.name or datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d') == today:
                completed_today += 1

    return {
        "success": True,
        "data": {
            "pendingTasks": pending_tasks,
            "pendingApproval": pending_approval,
            "approvedTasks": approved,
            "completedTasks": completed,
            "completedToday": completed_today,
            "totalTasks": pending_tasks + pending_approval + approved + completed,
        }
    }


@app.get("/api/system/status")
async def get_system_status():
    """Get system component status"""
    # Check if processes are running
    components = {
        "orchestrator": False,
        "emailMcp": False,
        "linkedinMcp": False,
        "odooMcp": False,
        "browserMcp": False,
        "calendarMcp": False,
        "scheduler": False,
    }

    try:
        import psutil
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'orchestrator' in cmdline:
                    components['orchestrator'] = True
                elif 'email_mcp' in cmdline:
                    components['emailMcp'] = True
                elif 'linkedin_mcp' in cmdline:
                    components['linkedinMcp'] = True
                elif 'odoo_mcp' in cmdline:
                    components['odooMcp'] = True
                elif 'browser_mcp' in cmdline:
                    components['browserMcp'] = True
                elif 'calendar_mcp' in cmdline:
                    components['calendarMcp'] = True
                elif 'scheduler' in cmdline:
                    components['scheduler'] = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        # psutil not available, check ports instead
        import socket
        ports = {
            'emailMcp': 8001, 'odooMcp': 8003,
            'browserMcp': 8008, 'calendarMcp': 8009
        }
        for name, port in ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            components[name] = (result == 0)
            sock.close()

    all_running = all(components.values())

    return {
        "success": True,
        "data": {
            "isRunning": all_running,
            "components": components,
            "uptime": "N/A",
            "lastUpdate": datetime.now().isoformat(),
        }
    }


# =============================================================================
# TASK APIs
# =============================================================================

@app.get("/api/tasks")
async def get_tasks(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Get all tasks from all directories"""
    all_tasks = []

    directories = [
        (NEEDS_ACTION_DIR, "needs_action"),
        (PLANS_DIR, "plans"),
        (PENDING_APPROVAL_DIR, "pending_approval"),
        (APPROVED_DIR, "approved"),
        (DONE_DIR, "done"),
        (REJECTED_DIR, "rejected"),
    ]

    for directory, dir_status in directories:
        if directory.exists():
            for file_path in directory.glob('*.md'):
                task = parse_markdown_file(file_path)
                task['directory'] = dir_status
                if task['status'] == 'unknown':
                    task['status'] = dir_status
                all_tasks.append(task)

    # Sort by created_at descending
    all_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated = all_tasks[start:end]

    return {
        "success": True,
        "data": paginated,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(all_tasks),
            "totalPages": (len(all_tasks) + limit - 1) // limit,
        }
    }


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task by ID"""
    directories = [NEEDS_ACTION_DIR, PLANS_DIR, PENDING_APPROVAL_DIR, APPROVED_DIR, DONE_DIR, REJECTED_DIR]

    for directory in directories:
        for file_path in directory.glob(f'{task_id}*'):
            if file_path.is_file():
                task = parse_markdown_file(file_path)
                return {"success": True, "data": task}

    raise HTTPException(status_code=404, detail="Task not found")


# =============================================================================
# APPROVAL APIs
# =============================================================================

@app.get("/api/approvals")
async def get_approvals(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Get pending approvals"""
    approvals = []

    if PENDING_APPROVAL_DIR.exists():
        for file_path in PENDING_APPROVAL_DIR.glob('*.md'):
            approval = parse_markdown_file(file_path)
            approvals.append(approval)

    approvals.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    start = (page - 1) * limit
    end = start + limit
    paginated = approvals[start:end]

    return {
        "success": True,
        "data": paginated,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(approvals),
            "totalPages": (len(approvals) + limit - 1) // limit,
        }
    }


@app.post("/api/approvals/{approval_id}/approve")
async def approve_request(approval_id: str, reason: Optional[str] = None):
    """Approve a pending request"""
    for file_path in PENDING_APPROVAL_DIR.glob(f'{approval_id}*'):
        if file_path.is_file():
            dest = APPROVED_DIR / file_path.name
            file_path.rename(dest)
            return {"success": True, "message": "Approved", "data": {"id": approval_id, "status": "approved"}}

    raise HTTPException(status_code=404, detail="Approval not found")


@app.post("/api/approvals/{approval_id}/reject")
async def reject_request(approval_id: str, reason: str):
    """Reject a pending request"""
    for file_path in PENDING_APPROVAL_DIR.glob(f'{approval_id}*'):
        if file_path.is_file():
            dest = REJECTED_DIR / file_path.name
            file_path.rename(dest)
            return {"success": True, "message": "Rejected", "data": {"id": approval_id, "status": "rejected"}}

    raise HTTPException(status_code=404, detail="Approval not found")


# =============================================================================
# FINANCIAL APIs
# =============================================================================

@app.get("/api/finance/summary")
async def get_financial_summary():
    """Get financial summary"""
    total_invoices = 0
    total_amount = 0.0
    pending_amount = 0.0

    if ACCOUNTING_DIR.exists():
        for file_path in ACCOUNTING_DIR.glob('*.md'):
            content = file_path.read_text(encoding='utf-8')
            # Extract amount if present
            import re
            amount_match = re.search(r'\$([\d,]+\.?\d*)', content)
            if amount_match:
                amount = float(amount_match.group(1).replace(',', ''))
                total_amount += amount
                total_invoices += 1
                if 'pending' in content.lower():
                    pending_amount += amount

    return {
        "success": True,
        "data": {
            "totalRevenue": total_amount,
            "pendingPayments": pending_amount,
            "totalInvoices": total_invoices,
            "monthlyRecurring": 12450.0,
            "outstandingInvoices": 3200.0,
            "burnRate": 4200.0,
        }
    }


# =============================================================================
# AUDIT LOG APIs
# =============================================================================

@app.get("/api/logs")
async def get_audit_logs(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    """Get audit logs"""
    logs = get_recent_logs(limit * page)

    start = (page - 1) * limit
    end = start + limit
    paginated = logs[start:end]

    return {
        "success": True,
        "data": paginated,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(logs),
            "totalPages": (len(logs) + limit - 1) // limit,
        }
    }


# =============================================================================
# SOCIAL MEDIA APIs
# =============================================================================

@app.get("/api/social/posts")
async def get_social_posts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Get social media posts"""
    posts = []

    # Check Pending_Approval for social posts
    if PENDING_APPROVAL_DIR.exists():
        for file_path in PENDING_APPROVAL_DIR.glob('*.md'):
            content = file_path.read_text(encoding='utf-8')
            if any(word in content.lower() for word in ['linkedin', 'social', 'post', 'facebook', 'instagram', 'twitter']):
                post = parse_markdown_file(file_path)
                posts.append(post)

    # Check Done for completed posts
    if DONE_DIR.exists():
        for file_path in DONE_DIR.glob('*.md'):
            content = file_path.read_text(encoding='utf-8')
            if any(word in content.lower() for word in ['linkedin', 'social', 'post']):
                post = parse_markdown_file(file_path)
                posts.append(post)

    posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    start = (page - 1) * limit
    end = start + limit
    paginated = posts[start:end]

    return {
        "success": True,
        "data": paginated,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(posts),
            "totalPages": (len(posts) + limit - 1) // limit,
        }
    }


# =============================================================================
# SYSTEM CONTROL APIs
# =============================================================================

@app.post("/api/system/start")
async def start_system():
    """Start the backend system"""
    try:
        script = BASE_PATH / "orchestration" / "run_system.py"
        subprocess.Popen([sys.executable, str(script)], cwd=str(BASE_PATH))
        return {"success": True, "message": "System starting..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/system/stop")
async def stop_system():
    """Stop the backend system"""
    try:
        # Kill processes by name
        subprocess.run(["pkill", "-f", "orchestration.run_system"], capture_output=True)
        subprocess.run(["pkill", "-f", "orchestrator.py"], capture_output=True)
        subprocess.run(["pkill", "-f", "mcp_server"], capture_output=True)
        subprocess.run(["pkill", "-f", "scheduler.py"], capture_output=True)
        return {"success": True, "message": "System stopping..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/system/restart")
async def restart_system():
    """Restart the backend system"""
    await stop_system()
    import time
    time.sleep(2)
    await start_system()
    return {"success": True, "message": "System restarting..."}


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "api-server", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    print("Starting AI Employee Vault API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
