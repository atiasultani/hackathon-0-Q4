#!/usr/bin/env python3
"""
Run Both Backend and Frontend Together
Starts: API Server (port 8000) + Frontend (port 3000)
"""

import subprocess
import sys
import os
import time
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "golden-ui")  # ✅ Correct folder

processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\n\nShutting down all components...")
    for name, proc in processes:
        print(f"  Stopping {name}...")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
    print("All components stopped.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60)
    print("  Gold Tier AI Employee System")
    print("  Starting Backend + Frontend")
    print("=" * 60)
    print()

    try:
        # 1️⃣ Start API Server (Backend)
        print("[1/2] Starting API Server (port 8000)...")
        api_proc = subprocess.Popen(
            [sys.executable, "-m", "api_server"],
            cwd=BACKEND_DIR,
            text=True
        )
        processes.append(("API Server", api_proc))
        time.sleep(3)
        print(f"  API Server started (PID: {api_proc.pid})")

        # 2️⃣ Start Frontend (Next.js)
        print("[2/2] Starting Frontend (port 3000)...")

        # Use npx to safely run Next.js from local node_modules
        npm_cmd = "npx"
        if os.name == "nt":  # Windows
            npm_cmd = "npx.cmd"

        frontend_proc = subprocess.Popen(
            [npm_cmd, "next", "dev", "--port", "3000"],
            cwd=FRONTEND_DIR,
            text=True
        )
        processes.append(("Frontend", frontend_proc))
        time.sleep(5)
        print(f"  Frontend started (PID: {frontend_proc.pid})")

        print("\n" + "=" * 60)
        print("  System Running!")
        print("=" * 60)
        print()
        print("  Frontend:  http://localhost:3000")
        print("  API:       http://localhost:8000")
        print("  API Docs:  http://localhost:8000/docs")
        print()
        print("  Press Ctrl+C to stop all components\n")

        # Monitor processes (simple)
        while True:
            time.sleep(1)
            for i, (name, proc) in enumerate(processes):
                if proc.poll() is not None:
                    print(f"WARNING: {name} stopped unexpectedly!")
                    print("  Please restart manually.")

    except Exception as e:
        print(f"Error: {e}")
        signal_handler(None, None)

if __name__ == "__main__":
    main()