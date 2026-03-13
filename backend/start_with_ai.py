#!/usr/bin/env python3
"""
Startup script for KanbanFlow backend with AI capabilities
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if AI dependencies are installed"""
    try:
        import google.generativeai
        print("✅ Google Generative AI is installed")
        return True
    except ImportError:
        print("❌ Missing Google Generative AI dependency")
        print("Installing AI dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "google-generativeai", "python-dotenv"], check=True)
            print("✅ AI dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install AI dependencies")
            return False

def check_env_file():
    """Check if .env file exists with Gemini API key"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_path) as f:
        content = f.read()
        if "GEMINI_API_KEY" in content and content.split("GEMINI_API_KEY=")[1].split("\n")[0].strip():
            print("✅ Gemini API key found in .env")
            return True
        else:
            print("❌ GEMINI_API_KEY not found or empty in .env")
            return False

def main():
    """Main startup function"""
    print("🤖 KanbanFlow Backend with AI Task Analyzer")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env_file():
        print("Please add your Gemini API key to the .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("🚀 Starting KanbanFlow backend with AI capabilities...")
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()