#!/usr/bin/env python3
"""
Startup script to run both the AI analyzer service and the frontend
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import google.generativeai
        import flask
        from dotenv import load_dotenv
        print("✅ Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please install dependencies with: pip install -r requirements_analyzer.txt")
        return False

def check_env_file():
    """Check if .env file exists with Gemini API key"""
    env_path = Path("backend/.env")
    if not env_path.exists():
        print("❌ backend/.env file not found")
        return False
    
    with open(env_path) as f:
        content = f.read()
        if "GEMINI_API_KEY" in content:
            print("✅ Gemini API key found in .env")
            return True
        else:
            print("❌ GEMINI_API_KEY not found in backend/.env")
            return False

def start_ai_service():
    """Start the AI analyzer service"""
    print("🚀 Starting AI Task Analyzer service...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    # Load .env file path
    env_path = os.path.join(os.getcwd(), 'backend', '.env')
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        # Copy loaded env vars to subprocess env
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            env['GEMINI_API_KEY'] = gemini_key
    
    try:
        process = subprocess.Popen(
            [sys.executable, 'web_task_analyzer_gemini.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait a moment for the service to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ AI service started successfully on http://localhost:5000")
            return process
        else:
            print("❌ AI service failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start AI service: {e}")
        return None

def start_frontend():
    """Start the Next.js frontend"""
    print("🚀 Starting Next.js frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("✅ Frontend starting on http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🤖 KanbanFlow AI Task Analyzer Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    processes = []
    
    try:
        # Start AI service
        ai_process = start_ai_service()
        if ai_process:
            processes.append(ai_process)
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        if not processes:
            print("❌ Failed to start any services")
            sys.exit(1)
        
        print("\n🎉 All services started successfully!")
        print("📋 AI Task Analyzer: http://localhost:5000")
        print("🌐 KanbanFlow App: http://localhost:3000")
        print("\nPress Ctrl+C to stop all services")
        
        # Wait for processes
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                for process in processes:
                    if process.poll() is not None:
                        print(f"⚠️  A service has stopped unexpectedly")
                        break
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
    
    finally:
        # Clean up processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()