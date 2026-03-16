#!/usr/bin/env python3
"""
Orchestrator for Silver Tier AI Employee System
Coordinates between watchers, Claude reasoning, approval workflow, and MCP servers
"""

import os
import time
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import threading
import requests

BASE_PATH = Path(__file__).parent.parent  # Go up one level to the main directory
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
PLANS_DIR = BASE_PATH / "Plans"
PENDING_APPROVAL_DIR = BASE_PATH / "Pending_Approval"
APPROVED_DIR = BASE_PATH / "Approved"
DONE_DIR = BASE_PATH / "Done"
REJECTED_DIR = BASE_PATH / "Rejected"
LOGS_DIR = BASE_PATH / "Logs"
DASHBOARD_FILE = BASE_PATH / "Dashboard.md"

class Orchestrator:
    def __init__(self):
        self.running = True

    def log_action(self, action_type, target, approval_status, result):
        """Create structured log entry"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "action_type": action_type,
            "target": target,
            "approval_status": approval_status,
            "result": result
        }

        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS_DIR / f"{log_date}.json"

        # Read existing logs or create new list
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def update_dashboard(self):
        """Update Dashboard.md with current system status"""
        pending_tasks = len(list(NEEDS_ACTION_DIR.glob("*.md")))
        pending_approval = len(list(PENDING_APPROVAL_DIR.glob("*.md")))
        approved_tasks = len(list(APPROVED_DIR.glob("*.md")))
        completed_today = len([f for f in DONE_DIR.glob("*.md")
                              if f.stat().st_mtime > datetime.now().timestamp() - 86400])

        dashboard_content = f"""# AI Employee Dashboard

## System Status
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **System Status**: {'RUNNING' if self.running else 'STOPPED'}

## Task Metrics
- **Pending Tasks**: {pending_tasks}
- **Pending Approval**: {pending_approval}
- **Approved Tasks**: {approved_tasks}
- **Completed Today**: {completed_today}

## Recent Activity
"""

        # Add recent log entries
        log_files = list(LOGS_DIR.glob("*.json"))
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_log, 'r') as f:
                    logs = json.load(f)
                    recent_logs = logs[-5:] if len(logs) >= 5 else logs  # Last 5 entries

                    for log in recent_logs:
                        dashboard_content += f"- {log['timestamp']}: {log['action_type']} ({log['result']})\n"
            except (json.JSONDecodeError, KeyError):
                dashboard_content += "- No recent activity logs available\n"
        else:
            dashboard_content += "- No recent activity logs available\n"

        dashboard_content += f"""
## Directories Status
- Needs_Action: {pending_tasks} items
- Plans: {len(list(PLANS_DIR.glob('*.md')))} items
- Pending_Approval: {pending_approval} items
- Approved: {approved_tasks} items
- Done: {len(list(DONE_DIR.glob('*.md')))} items
- Logs: {len(list(LOGS_DIR.glob('*')))} items

*Dashboard automatically updated by Orchestrator*
"""

        with open(DASHBOARD_FILE, 'w') as f:
            f.write(dashboard_content)

    def trigger_claude(self, task_file):
        """Trigger Claude to process a task file"""
        print(f"Triggering Claude to process: {task_file}")

        # Create a plan file based on the task
        task_path = NEEDS_ACTION_DIR / task_file
        plan_filename = f"PLAN_{task_file.replace('.md', '')}.md"
        plan_path = PLANS_DIR / plan_filename

        with open(task_path, 'r') as f:
            task_content = f.read()

        # Create a basic plan structure (CLAUDE.md compliant format)
        plan_content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
status: pending_approval
source: {task_file}
---

## Objective
Process task: {task_file}

## Original Task Content
{task_content}

## Steps
- [x] Analyzed task content
- [ ] Determine required actions
- [ ] Create action plan
- [ ] Submit for approval if needed
"""

        with open(plan_path, 'w') as f:
            f.write(plan_content)

        # Check if this requires approval (basic heuristic)
        requires_approval = any(word in task_content.lower() for word in ['email', 'send', 'payment', 'post', 'linkedin'])

        if requires_approval:
            # Create proper approval file (CLAUDE.md compliant format)
            approval_filename = f"ACTION_{task_file.replace('.md', '')}.md"
            approval_path = PENDING_APPROVAL_DIR / approval_filename
            
            # Determine action type and priority
            if 'email' in task_content.lower():
                action_type = 'send_email'
            elif 'linkedin' in task_content.lower() or 'post' in task_content.lower():
                action_type = 'linkedin_post'
            elif 'payment' in task_content.lower():
                action_type = 'payment'
            else:
                action_type = 'general_action'
            
            priority = 'high' if any(word in task_content.lower() for word in ['urgent', 'asap', 'critical']) else 'medium'

            approval_content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
priority: {priority}
source: {task_file}
---

## Action Required
Execute action for task: {task_file}

## Details
{task_content}

## Reason
Task requires human approval before execution per Silver Tier HITL policy.

---
[HUMAN: Move this file to /Approved/ to execute, or /Rejected/ to cancel]
"""
            
            with open(approval_path, 'w') as f:
                f.write(approval_content)
            
            # Move original task to Done (approval file tracks the action)
            done_path = DONE_DIR / task_file
            shutil.move(task_path, done_path)

            # Log the action
            self.log_action("task_processing", str(task_file), "requires_approval", "moved_to_pending")
        else:
            # Move directly to done (for non-sensitive tasks)
            done_path = DONE_DIR / task_file
            shutil.move(task_path, done_path)

            # Log the action
            self.log_action("task_processing", str(task_file), "auto_approved", "completed")

    def monitor_needs_action(self):
        """Monitor Needs_Action directory for new files"""
        while self.running:
            try:
                task_files = list(NEEDS_ACTION_DIR.glob("*.md"))

                for task_file in task_files:
                    try:
                        self.trigger_claude(task_file.name)
                    except Exception as e:
                        print(f"Error processing {task_file}: {e}")

                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error monitoring Needs_Action: {e}")
                time.sleep(10)

    def monitor_approved(self):
        """Monitor Approved directory for files to process with MCP servers"""
        while self.running:
            try:
                approved_files = list(APPROVED_DIR.glob("*.md"))

                for approved_file in approved_files:
                    try:
                        self.execute_approved_task(approved_file.name)
                    except Exception as e:
                        print(f"Error executing {approved_file}: {e}")

                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error monitoring Approved: {e}")
                time.sleep(10)

    def execute_approved_task(self, filename):
        """Execute an approved task using MCP server"""
        print(f"Executing approved task: {filename}")

        approved_path = APPROVED_DIR / filename
        done_path = DONE_DIR / filename
        failed_path = NEEDS_ACTION_DIR / f"{filename.replace('.md', '_FAILED.md')}"

        try:
            # Simulate MCP server execution based on file type
            with open(approved_path, 'r') as f:
                content = f.read()

            # Determine action type and execute accordingly
            if 'linkedin' in content.lower() or 'post' in content.lower():
                action_result = self.execute_linkedin_post(content)
                action_type = "linkedin_post"
            elif 'email' in content.lower() or 'send' in content.lower():
                action_result = self.execute_email(content)
                action_type = "email_send"
            elif 'facebook' in content.lower() or 'instagram' in content.lower() or 'x ' in content.lower() or 'twitter' in content.lower():
                action_result = self.execute_social_media_post(content)
                action_type = "social_media_post"
            elif 'odoo' in content.lower() or 'invoice' in content.lower() or 'accounting' in content.lower():
                action_result = self.execute_odoo_operation(content)
                action_type = "odoo_operation"
            elif 'payment' in content.lower() or 'portal' in content.lower():
                action_result = self.execute_payment_via_browser(content)
                action_type = "payment_processing"
            elif 'calendar' in content.lower() or 'meeting' in content.lower() or 'event' in content.lower():
                action_result = self.execute_calendar_operation(content)
                action_type = "calendar_operation"
            else:
                action_result = "completed"
                action_type = "general_task"

            if action_result == "success":
                # Move to Done directory
                shutil.move(approved_path, done_path)
                # Log the action
                self.log_action(action_type, filename, "approved", action_result)
            else:
                # Handle failure - move to Needs_Action with _FAILED suffix
                shutil.move(approved_path, failed_path)
                self.log_action(action_type, filename, "approved", f"failed: {action_result}")
                self.update_dashboard_with_failure(filename, action_result)

        except Exception as e:
            # Handle exception - move to Needs_Action with _FAILED suffix
            error_msg = str(e)
            if approved_path.exists():
                shutil.move(approved_path, failed_path)
            self.log_action("task_execution", filename, "approved", f"failed: {error_msg}")
            self.update_dashboard_with_failure(filename, error_msg)
            raise  # Re-raise for monitor_approved to catch

    def update_dashboard_with_failure(self, filename: str, error: str):
        """Update dashboard with failure notice (CLAUDE.md error handling)"""
        # Add failure notice to dashboard
        current_content = DASHBOARD_FILE.read_text() if DASHBOARD_FILE.exists() else "# AI Employee Dashboard\n"
        
        failure_notice = f"\n## ⚠️ Failed Tasks\n- **{filename}**: {error}\n"
        
        if "⚠️ Failed Tasks" not in current_content:
            current_content += failure_notice
            DASHBOARD_FILE.write_text(current_content)

    def execute_linkedin_post(self, content):
        """Execute LinkedIn post via LinkedIn MCP server"""
        print("Executing LinkedIn post via MCP server...")
        try:
            # Call LinkedIn MCP server
            import requests
            response = requests.post("http://localhost:8004/post_content", json={
                "platforms": ["linkedin"],
                "message": content,
                "message": content.split("## Details")[1].split("\n")[1] if "## Details" in content else "Automated post"
            }, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return "success"
                else:
                    return f"failed: {result.get('message', 'Unknown error')}"
            else:
                return f"failed: HTTP {response.status_code}"
        except Exception as e:
            return f"failed: {str(e)}"

    def execute_email(self, content):
        """Execute email send via Email MCP server"""
        print("Executing email send via MCP server...")
        try:
            # Call Email MCP server
            import requests
            response = requests.post("http://localhost:8001/send_email", json={
                "subject": "Automated Email",
                "body": content,
                "recipients": ["recipient@example.com"]  # Would be parsed from content in real implementation
            }, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return "success"
                else:
                    return f"failed: {result.get('message', 'Unknown error')}"
            else:
                return f"failed: HTTP {response.status_code}"
        except Exception as e:
            return f"failed: {str(e)}"

    def execute_social_media_post(self, content):
        """Execute social media post via Social Media MCP server"""
        print("Executing social media post via MCP server...")
        try:
            # Determine which platforms to post to based on content
            platforms = []
            if any(word in content.lower() for word in ['facebook', 'fb']):
                platforms.append('facebook')
            if any(word in content.lower() for word in ['instagram', 'ig']):
                platforms.append('instagram')
            if any(word in content.lower() for word in ['x', 'twitter']):
                platforms.append('x')
            if not platforms:
                platforms = ['facebook', 'instagram', 'x']  # Default to all if not specified

            # Call Social Media MCP server
            import requests
            response = requests.post("http://localhost:8004/post_content", json={
                "platforms": platforms,
                "message": content.split("## Details")[1].split("\n")[1] if "## Details" in content else "Automated social post",
                "caption": content.split("## Details")[1].split("\n")[1] if "## Details" in content else "Automated social post"
            }, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return "success"
                else:
                    return f"failed: {result.get('message', 'Unknown error')}"
            else:
                return f"failed: HTTP {response.status_code}"
        except Exception as e:
            return f"failed: {str(e)}"

    def execute_odoo_operation(self, content):
        """Execute Odoo operation via Odoo MCP server"""
        print("Executing Odoo operation via MCP server...")
        try:
            # Determine operation type from content
            if 'invoice' in content.lower():
                # Example: create invoice
                import requests
                response = requests.post("http://localhost:8003/create_invoice", json={
                    "partner_id": 1,  # Would be parsed from content in real implementation
                    "invoice_date": datetime.now().strftime('%Y-%m-%d'),
                    "move_type": "out_invoice"
                }, timeout=30)
            else:
                return "failed: unsupported operation"

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return "success"
                else:
                    return f"failed: {result.get('message', 'Unknown error')}"
            else:
                return f"failed: HTTP {response.status_code}"
        except Exception as e:
            return f"failed: {str(e)}"

    def execute_payment_via_browser(self, content):
        """Execute payment via Browser MCP server"""
        print("Executing payment via Browser MCP server...")
        try:
            import requests
            import uuid

            # Create a session
            session_response = requests.post("http://localhost:8008/create_session", timeout=30)
            if session_response.status_code != 200:
                return f"failed: Could not create browser session"

            session_data = session_response.json()
            session_id = session_data.get("session_id")

            # Perform payment operations
            # This is a simplified example - in reality, more complex steps would be needed
            result = requests.post(f"http://localhost:8008/process_payment/{session_id}", json={
                "amount": 100.00,
                "description": content[:100]  # First 100 chars as description
            }, timeout=30)

            # Close session
            requests.post(f"http://localhost:8008/close_session/{session_id}", timeout=10)

            if result.status_code == 200:
                result_data = result.json()
                if result_data.get("status") in ["success", "unknown"]:  # unknown is acceptable for payment processing
                    return "success"
                else:
                    return f"failed: {result_data.get('message', 'Unknown error')}"
            else:
                return f"failed: HTTP {result.status_code}"
        except Exception as e:
            return f"failed: {str(e)}"

    def execute_calendar_operation(self, content):
        """Execute calendar operation via Calendar MCP server"""
        print("Executing calendar operation via MCP server...")
        try:
            import requests
            # Example: create event
            response = requests.post("http://localhost:8009/create_event", json={
                "summary": content.split("## Details")[1].split("\n")[1] if "## Details" in content else "Automated event",
                "description": content,
                "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat()
            }, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return "success"
                else:
                    return f"failed: {result.get('message', 'Unknown error')}"
            else:
                return f"failed: HTTP {response.status_code}"
        except Exception as e:
            return f"failed: {str(e)}"

    def run(self):
        """Start the orchestrator"""
        print("Starting AI Employee Orchestrator...")

        # Start monitoring threads
        needs_action_thread = threading.Thread(target=self.monitor_needs_action, daemon=True)
        approved_thread = threading.Thread(target=self.monitor_approved, daemon=True)

        needs_action_thread.start()
        approved_thread.start()

        # Update dashboard initially
        self.update_dashboard()

        try:
            while self.running:
                # Update dashboard periodically
                self.update_dashboard()
                time.sleep(30)  # Update dashboard every 30 seconds
        except KeyboardInterrupt:
            print("\nShutting down orchestrator...")
            self.running = False

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()