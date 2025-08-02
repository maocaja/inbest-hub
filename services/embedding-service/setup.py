#!/usr/bin/env python3
"""
Setup script for Embedding Service
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "chroma_db",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def setup_environment():
    """Setup environment file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from env.example")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No env.example found, please create .env manually")

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    # Test imports
    try:
        import fastapi
        import chromadb
        import sentence_transformers
        import numpy
        print("✅ All required packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test embedding generation
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        test_embedding = model.encode("test")
        print(f"✅ Embedding generation test passed (dimension: {len(test_embedding)})")
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Embedding Service...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Embedding Service setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: python main.py")
    print("3. Access the API at: http://localhost:8005")
    print("4. View docs at: http://localhost:8005/docs")

if __name__ == "__main__":
    main() 