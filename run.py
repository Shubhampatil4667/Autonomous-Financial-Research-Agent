#!/usr/bin/env python3
"""
Run script for Autonomous Financial Research Agent
"""

import subprocess
import sys
import os

def run_backend():
    """Run the FastAPI backend"""
    print("Starting FastAPI backend...")
    # Run from root using -m to ensure package imports work
    subprocess.run([sys.executable, "-m", "app.api.main"])

def run_frontend(port=8502):
    """Run the Streamlit frontend"""
    print(f"Starting Streamlit frontend on port {port}...")
    # Get the absolute path to the frontend directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    os.chdir(frontend_dir)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port)])

def run_tests():
    """Run tests"""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "../tests/"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py [backend|frontend|test]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "backend":
        run_backend()
    elif command == "frontend":
        run_frontend()
    elif command == "test":
        run_tests()
    else:
        print("Invalid command. Use: backend, frontend, or test")