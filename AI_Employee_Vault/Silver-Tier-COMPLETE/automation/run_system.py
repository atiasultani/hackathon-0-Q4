#!/usr/bin/env python3
"""
Main Runner for Silver Tier AI Employee System
Starts all required components: orchestrator, MCP servers, and scheduler
"""

import subprocess
import sys
import time
import os

# Base folder where this script is located (automation folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def start_process(script_name, display_name):
    """Start a Python process with correct path"""
    script_path = os.path.join(BASE_DIR, script_name)
    print(f"Starting {display_name}...")
    return subprocess.Popen([sys.executable, script_path])

def main():
    """Main function to start all components"""
    print("Starting Silver Tier AI Employee System...")

    processes = []

    try:
        # Start orchestrator
        orchestrator_proc = start_process("orchestrator.py", "Orchestrator")
        processes.append(("Orchestrator", orchestrator_proc))
        time.sleep(2)

        # Start Email MCP server
        email_proc = start_process("email_mcp_server.py", "Email MCP Server")
        processes.append(("Email MCP Server", email_proc))
        time.sleep(2)

        # Start LinkedIn MCP server
        linkedin_proc = start_process("linkedin_mcp_server.py", "LinkedIn MCP Server")
        processes.append(("LinkedIn MCP Server", linkedin_proc))
        time.sleep(2)

        # Start Scheduler
        scheduler_proc = start_process("scheduler.py", "Scheduler")
        processes.append(("Scheduler", scheduler_proc))

        print("\nAll Silver Tier components started successfully!")
        print("Components running:")
        for name, proc in processes:
            print(f"  - {name}: PID {proc.pid}")

        print("\nSystem is now operational.")
        print("Press Ctrl+C to shut down all components.")

        # Monitor processes
        try:
            while True:
                time.sleep(1)
                for i, (name, proc) in enumerate(processes):
                    if proc.poll() is not None:
                        print(f"WARNING: {name} process died unexpectedly with return code {proc.returncode}")
                        # Restart the process
                        proc = start_process(f"{name.lower().replace(' ', '_')}.py", name)
                        processes[i] = (name, proc)

        except KeyboardInterrupt:
            print("\nReceived shutdown signal...")

    finally:
        print("Shutting down all components...")
        for name, proc in processes:
            print(f"Terminating {name} (PID: {proc.pid})...")
            proc.terminate()
        time.sleep(2)
        for name, proc in processes:
            if proc.poll() is None:
                print(f"Force killing {name}...")
                proc.kill()
        print("All components shut down.")

if __name__ == "__main__":
    main()