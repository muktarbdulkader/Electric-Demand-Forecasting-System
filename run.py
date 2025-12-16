#!/usr/bin/env python3
"""
Ethiopian Electric Utility - Complete Startup Script
Starts both backend and frontend services
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

# Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
END = '\033[0m'

def print_header():
    """Print header"""
    print("\n" + "="*60)
    print("🇪🇹 Ethiopian Electric Utility - Demand Forecasting Platform")
    print("="*60 + "\n")

def check_python():
    """Check Python version"""
    print(f"{BLUE}Checking Python...{END}")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{RED}Python 3.8+ required. Found {version.major}.{version.minor}{END}")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True

def check_node():
    """Check Node.js version"""
    print(f"{BLUE}Checking Node.js...{END}")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"Node.js {result.stdout.strip()} ✓")
        return True
    except FileNotFoundError:
        print(f"{RED}Node.js not found. Please install Node.js 16+{END}")
        return False

def setup_backend():
    """Setup backend"""
    print(f"\n{BLUE}Setting up Backend...{END}")
    backend_dir = Path("backend")
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Get pip executable
    if platform.system() == "Windows":
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"
    
    # Install dependencies
    print("Installing backend dependencies...")
    subprocess.run([str(pip_exe), "install", "-q", "-r", "requirements.txt"], 
                   cwd=str(backend_dir), check=True)
    
    # Create .env
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        env_file.write_text("""DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
CORS_ORIGINS=["http://localhost:5173"]
""")
    
    print(f"{GREEN}✓ Backend ready{END}")
    return venv_dir

def setup_frontend():
    """Setup frontend"""
    print(f"\n{BLUE}Setting up Frontend...{END}")
    frontend_dir = Path("frontend")
    
    # Install dependencies
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install", "-q"], cwd=str(frontend_dir), check=True)
    
    # Create .env.local
    env_file = frontend_dir / ".env.local"
    if not env_file.exists():
        print("Creating .env.local file...")
        env_file.write_text("""VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Ethiopian Electric Utility
""")
    
    print(f"{GREEN}✓ Frontend ready{END}")

def start_backend(venv_dir):
    """Start backend server"""
    print(f"\n{BLUE}Starting Backend on http://localhost:8000{END}")
    
    backend_dir = Path("backend")
    
    if platform.system() == "Windows":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
    
    # Start backend
    subprocess.Popen(
        [str(python_exe), "-m", "uvicorn", "app.main:app", "--reload", 
         "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir)
    )
    
    # Wait for backend to start
    time.sleep(3)

def start_frontend():
    """Start frontend server"""
    print(f"{BLUE}Starting Frontend on http://localhost:5173{END}")
    
    frontend_dir = Path("frontend")
    subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir))

def main():
    """Main function"""
    print_header()
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not check_node():
        sys.exit(1)
    
    print(f"\n{GREEN}✓ All prerequisites installed{END}")
    
    # Setup
    venv_dir = setup_backend()
    setup_frontend()
    
    # Start services
    print(f"\n{YELLOW}Starting services...{END}")
    start_backend(venv_dir)
    start_frontend()
    
    # Print info
    print("\n" + "="*60)
    print(f"{GREEN}✓ Platform started successfully!{END}")
    print("="*60)
    print(f"\n{GREEN}Frontend:{END} http://localhost:5173")
    print(f"{GREEN}Backend:{END} http://localhost:8000")
    print(f"{GREEN}API Docs:{END} http://localhost:8000/docs")
    print("\n" + "="*60)
    print("\nPress Ctrl+C to stop all services\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Shutting down...{END}")
        sys.exit(0)

if __name__ == "__main__":
    main()
