#!/usr/bin/env python3
"""
Main Runner for Silver Tier AI Employee System
Starts all required components: orchestrator, MCP servers, and scheduler
"""

import subprocess
import sys
import signal
import time
from threading import Thread
import os

def start_orchestrator():
    """Start the orchestrator process"""
    print("Starting Orchestrator...")
    orchestrator_process = subprocess.Popen([sys.executable, "orchestrator.py"])
    return orchestrator_process

def start_email_mcp_server():
    """Start the email MCP server process"""
    print("Starting Email MCP Server...")
    email_mcp_process = subprocess.Popen([sys.executable, "email_mcp_server.py"])
    return email_mcp_process

def start_linkedin_mcp_server():
    """Start the LinkedIn MCP server process"""
    print("Starting LinkedIn MCP Server...")
    linkedin_mcp_process = subprocess.Popen([sys.executable, "linkedin_mcp_server.py"])
    return linkedin_mcp_process

def start_scheduler():
    """Start the scheduler process"""
    print("Starting Scheduler...")
    scheduler_process = subprocess.Popen([sys.executable, "scheduler.py"])
    return scheduler_process

def main():
    """Main function to start all components"""
    print("Starting Silver Tier AI Employee System...")

    processes = []

    try:
        # Start orchestrator
        orchestrator_proc = start_orchestrator()
        processes.append(("Orchestrator", orchestrator_proc))
        time.sleep(2)  # Give it time to start

        # Start email MCP server
        email_mcp_proc = start_email_mcp_server()
        processes.append(("Email MCP Server", email_mcp_proc))
        time.sleep(2)  # Give it time to start

        # Start LinkedIn MCP server
        linkedin_mcp_proc = start_linkedin_mcp_server()
        processes.append(("LinkedIn MCP Server", linkedin_mcp_proc))
        time.sleep(2)  # Give it time to start

        # Start scheduler
        scheduler_proc = start_scheduler()
        processes.append(("Scheduler", scheduler_proc))

        print("\nAll Silver Tier components started successfully!")
        print("Components running:")
        for name, proc in processes:
            print(f"  - {name}: PID {proc.pid}")

        print("\nSystem is now operational.")
        print("Press Ctrl+C to shut down all components.")

        # Wait for all processes to finish (they shouldn't unless terminated)
        try:
            while True:
                time.sleep(1)

                # Check if any process has died unexpectedly
                for name, proc in processes:
                    if proc.poll() is not None:
                        print(f"WARNING: {name} process died unexpectedly with return code {proc.returncode}")
                        # Restart the process
                        if name == "Orchestrator":
                            proc = start_orchestrator()
                        elif name == "Email MCP Server":
                            proc = start_email_mcp_server()
                        elif name == "LinkedIn MCP Server":
                            proc = start_linkedin_mcp_server()
                        elif name == "Scheduler":
                            proc = start_scheduler()

                        processes = [(n, p if n != name else proc) for n, p in processes]

        except KeyboardInterrupt:
            print("\nReceived shutdown signal...")

    finally:
        print("Shutting down all components...")
        for name, proc in processes:
            print(f"Terminating {name} (PID: {proc.pid})...")
            proc.terminate()

        # Wait a bit for graceful shutdown
        time.sleep(2)

        # Force kill if still running
        for name, proc in processes:
            if proc.poll() is None:
                print(f"Force killing {name}...")
                proc.kill()

        print("All components shut down.")

if __name__ == "__main__":
    main()