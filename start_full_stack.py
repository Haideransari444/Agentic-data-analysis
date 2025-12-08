#!/usr/bin/env python3
"""
Startup script to run both FastAPI backend and Next.js frontend
"""
import subprocess
import sys
import os
import time

def main():
    print("=" * 80)
    print("🚀 AI Data Analysis Platform - Full Stack Startup")
    print("=" * 80)
    
    # Check if we're in the right directory
    if not os.path.exists("api_server.py"):
        print("❌ Error: api_server.py not found. Please run from project root.")
        sys.exit(1)
    
    if not os.path.exists("ai-data-dashboard"):
        print("❌ Error: ai-data-dashboard folder not found.")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("\n📊 Starting FastAPI Backend (port 8000)...")
        backend = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(("Backend", backend))
        
        # Wait for backend to start
        time.sleep(3)
        
        # Start Next.js frontend
        print("\n💻 Starting Next.js Frontend (port 3000)...")
        print("   (This may take a moment to compile...)")
        
        frontend = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="ai-data-dashboard",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            shell=True
        )
        processes.append(("Frontend", frontend))
        
        print("\n" + "=" * 80)
        print("✅ Both services starting up...")
        print("=" * 80)
        print("📊 Backend API:  http://localhost:8000")
        print("📖 API Docs:     http://localhost:8000/docs")
        print("💻 Frontend:     http://localhost:3000")
        print("=" * 80)
        print("\n⌨️  Press Ctrl+C to stop all services")
        print("=" * 80)
        
        # Monitor processes
        while True:
            for name, proc in processes:
                # Check if process is still running
                if proc.poll() is not None:
                    print(f"\n❌ {name} process exited unexpectedly")
                    raise KeyboardInterrupt
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        for name, proc in processes:
            print(f"   Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("✅ All services stopped")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for name, proc in processes:
            proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
