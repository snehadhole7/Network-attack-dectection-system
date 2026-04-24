"""
Setup Script for Network Attack Detection System
Helps with initial configuration and setup
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version_info = sys.version_info
    version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    print(f"Python Version: {version}")
    
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print("❌ ERROR: Python 3.8+ required")
        return False
    
    print("✓ Python version OK")
    return True

def check_mysql():
    """Check MySQL installation"""
    print_header("Checking MySQL")
    
    try:
        import mysql.connector
        print("✓ MySQL connector installed")
        return True
    except ImportError:
        print("ℹ MySQL connector not yet installed (will be installed via pip)")
        return True

def check_dependencies():
    """Check if key packages are installed"""
    print_header("Checking Dependencies")
    
    packages = {
        'flask': 'Flask',
        'scapy': 'Scapy',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
    }
    
    missing = []
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("These will be installed when you run: pip install -r requirements.txt")
    
    return True

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        'logs',
        'models',
        'rules',
        'database',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created {directory}/")
        else:
            print(f"✓ {directory}/ already exists")

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_header("Setting Up Configuration")
    
    env_file = '.env'
    env_example = '.env.example'
    
    if os.path.exists(env_file):
        print(f"✓ {env_file} already exists")
    elif os.path.exists(env_example):
        import shutil
        shutil.copy(env_example, env_file)
        print(f"✓ Created {env_file} from template")
        print(f"\n⚠ Please edit {env_file} with your configuration:")
        print("  - MySQL credentials")
        print("  - Network interface")
        print("  - Email settings")
    else:
        print(f"⚠ {env_example} not found")

def test_imports():
    """Test if main modules can be imported"""
    print_header("Testing Module Imports")
    
    modules = [
        'config',
        'network_capture',
        'data_preprocessor',
        'traffic_analyzer',
        'threat_detector',
        'response_system',
        'alert_system',
        'reporting',
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} OK")
        except ImportError as e:
            print(f"✗ {module} - {str(e)}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def display_next_steps():
    """Display next steps for user"""
    print_header("Next Steps")
    
    print("""
1. Install Python Dependencies:
   pip install -r requirements.txt

2. Configure the System:
   Edit .env file with your settings:
   - MySQL host, user, password
   - Network interface (e.g., eth0, Ethernet)
   - SMTP settings for email alerts

3. Start MySQL:
   Ensure MySQL is running on localhost:3306

4. Run the Application:
   python app.py
   
   For Linux (packet capture requires sudo):
   sudo python app.py

5. Access the Dashboard:
   Open browser: http://localhost:5000

6. First Time Setup:
   - System will create database tables automatically
   - Check http://localhost:5000/api/health for system status
   - Review logs/app.log for any errors
    """)

def main():
    """Run setup process"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "Network Attack Detection System" + " "*17 + "║")
    print("║" + " "*20 + "Setup Wizard" + " "*26 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run checks
    if not check_python_version():
        return False
    
    check_mysql()
    check_dependencies()
    create_directories()
    create_env_file()
    
    if not test_imports():
        print("\n⚠ Some imports failed. Install dependencies first:")
        print("  pip install -r requirements.txt")
    
    display_next_steps()
    
    print("\n" + "="*60)
    print("Setup complete! Review the steps above to get started.")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)
