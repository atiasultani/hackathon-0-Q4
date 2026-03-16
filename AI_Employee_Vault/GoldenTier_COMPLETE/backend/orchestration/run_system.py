#!/usr/bin/env python3
"""
Main Runner for Silver Tier AI Employee System
Starts all required components: orchestrator, MCP servers, and scheduler
"""

import subprocess
import sys
import time
import os

# Base folder where this script is located (orchestration folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MCP folder is a sibling of orchestration
MCP_DIR = os.path.join(os.path.dirname(BASE_DIR), "mcp")


def start_process(script_path, display_name):
    """Start a Python process with correct path"""
    print(f"Starting {display_name}...")
    return subprocess.Popen([sys.executable, script_path])


def main():
    """Main function to start all components"""
    print("Starting Silver Tier AI Employee System...")

    processes = []

    try:
        # Start orchestrator
        orchestrator_proc = start_process(
            os.path.join(BASE_DIR, "orchestrator.py"), "Orchestrator"
        )
        processes.append(("Orchestrator", orchestrator_proc, os.path.join(BASE_DIR, "orchestrator.py")))
        time.sleep(2)

        # Start Email MCP server
        email_proc = start_process(
            os.path.join(MCP_DIR, "email_mcp_server.py"), "Email MCP Server"
        )
        processes.append(("Email MCP Server", email_proc, os.path.join(MCP_DIR, "email_mcp_server.py")))
        time.sleep(2)

        # Start LinkedIn MCP server
        linkedin_proc = start_process(
            os.path.join(MCP_DIR, "linkedin_mcp_server.py"), "LinkedIn MCP Server"
        )
        processes.append(("LinkedIn MCP Server", linkedin_proc, os.path.join(MCP_DIR, "linkedin_mcp_server.py")))
        time.sleep(2)

        # Start Odoo MCP server
        odoo_proc = start_process(
            os.path.join(MCP_DIR, "odoo_mcp_server.py"), "Odoo MCP Server"
        )
        processes.append(("Odoo MCP Server", odoo_proc, os.path.join(MCP_DIR, "odoo_mcp_server.py")))
        time.sleep(2)

        # Start Browser MCP server
        browser_proc = start_process(
            os.path.join(MCP_DIR, "browser_mcp_server.py"), "Browser MCP Server"
        )
        processes.append(("Browser MCP Server", browser_proc, os.path.join(MCP_DIR, "browser_mcp_server.py")))
        time.sleep(2)

        # Start Calendar MCP server
        calendar_proc = start_process(
            os.path.join(MCP_DIR, "calendar_mcp_server.py"), "Calendar MCP Server"
        )
        processes.append(("Calendar MCP Server", calendar_proc, os.path.join(MCP_DIR, "calendar_mcp_server.py")))
        time.sleep(2)

        # Start Scheduler
        scheduler_proc = start_process(
            os.path.join(BASE_DIR, "scheduler.py"), "Scheduler"
        )
        processes.append(("Scheduler", scheduler_proc, os.path.join(BASE_DIR, "scheduler.py")))

        print("\nAll Silver Tier components started successfully!")
        print("Components running:")
        for name, proc, _ in processes:
            print(f"  - {name}: PID {proc.pid}")

        print("\nSystem is now operational.")
        print("Press Ctrl+C to shut down all components.")

        # Monitor processes
        try:
            while True:
                time.sleep(1)
                for i, (name, proc, script_path) in enumerate(processes):
                    if proc.poll() is not None:
                        print(f"WARNING: {name} process died unexpectedly with return code {proc.returncode}")
                        # Restart the process using the stored script path
                        new_proc = start_process(script_path, name)
                        processes[i] = (name, new_proc, script_path)

        except KeyboardInterrupt:
            print("\nReceived shutdown signal...")

    finally:
        print("Shutting down all components...")
        for name, proc, _ in processes:
            print(f"Terminating {name} (PID: {proc.pid})...")
            proc.terminate()
        time.sleep(2)
        for name, proc, _ in processes:
            if proc.poll() is None:
                print(f"Force killing {name}...")
                proc.kill()
        print("All components shut down.")

if __name__ == "__main__":
    main()
