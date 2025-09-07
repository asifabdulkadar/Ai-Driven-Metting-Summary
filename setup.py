"""
Setup script for AI-Driven Meeting Summarizer
This script helps users set up the environment and test the system
"""
import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🤖 Checking Ollama...")
    try:
        # Check if ollama command exists
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            
            # Check if gemma:2b model is available
            if "gemma:2b" in result.stdout:
                print("✅ gemma:2b model is available")
                return True
            else:
                print("⚠️ gemma:2b model not found. Pulling model...")
                try:
                    subprocess.check_call(["ollama", "pull", "gemma:2b"])
                    print("✅ gemma:2b model pulled successfully")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to pull gemma:2b model: {e}")
                    return False
        else:
            print("❌ Ollama is not running or not installed")
            print("Please install Ollama from https://ollama.ai and start the service")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("Please install Ollama from https://ollama.ai")
        return False

def check_mongodb():
    """Check if MongoDB is accessible"""
    print("\n🍃 Checking MongoDB...")
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running on localhost:27017")
        print("Or update the MONGODB_URI in your .env file")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed")
        print("Please install FFmpeg:")
        if platform.system() == "Windows":
            print("  Download from https://ffmpeg.org/download.html")
        elif platform.system() == "Darwin":  # macOS
            print("  brew install ffmpeg")
        else:  # Linux
            print("  sudo apt install ffmpeg")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n⚙️ Setting up environment variables...")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    try:
        env_content = """MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=meeting_summarizer
OLLAMA_BASE_URL=http://localhost:11434
"""
        env_file.write_text(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_system_test():
    """Run the system test"""
    print("\n🧪 Running system test...")
    try:
        result = subprocess.run([sys.executable, "test_system.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ System test passed")
            return True
        else:
            print("❌ System test failed")
            print("Error output:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run system test: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\n📄 Creating sample data...")
    try:
        result = subprocess.run([sys.executable, "sample_data.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Sample data created successfully")
            return True
        else:
            print("❌ Failed to create sample data")
            return False
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI-Driven Meeting Summarizer - Setup Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check external dependencies
    ollama_ok = check_ollama()
    mongodb_ok = check_mongodb()
    ffmpeg_ok = check_ffmpeg()
    
    # Create sample data
    create_sample_data()
    
    # Run system test
    if ollama_ok and mongodb_ok:
        run_system_test()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Setup Summary:")
    print(f"✅ Python requirements: Installed")
    print(f"{'✅' if ollama_ok else '❌'} Ollama: {'Ready' if ollama_ok else 'Not ready'}")
    print(f"{'✅' if mongodb_ok else '❌'} MongoDB: {'Ready' if mongodb_ok else 'Not ready'}")
    print(f"{'✅' if ffmpeg_ok else '❌'} FFmpeg: {'Ready' if ffmpeg_ok else 'Not ready'}")
    
    if ollama_ok and mongodb_ok:
        print("\n🎉 Setup completed successfully!")
        print("\n💡 Next steps:")
        print("1. Run the application: streamlit run app.py")
        print("2. Open your browser to http://localhost:8501")
        print("3. Upload a meeting file and start processing!")
    else:
        print("\n⚠️ Setup completed with some issues.")
        print("Please resolve the issues above before running the application.")
    
    return ollama_ok and mongodb_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
