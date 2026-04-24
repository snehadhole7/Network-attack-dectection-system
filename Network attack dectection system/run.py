#!/usr/bin/env python3
"""
Startup Script for Network Attack Detection System
Initializes and starts the application with checks
"""

import os
import sys
import logging
from pathlib import Path

def main():
    """Main startup function"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Network Attack Detection System - Startup")
    logger.info("=" * 60)
    
    # Check if running from correct directory
    required_files = ['app.py', 'config.py', 'requirements.txt']
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"ERROR: {file} not found!")
            logger.error("Please run this script from the project root directory")
            return False
    
    logger.info("✓ Project structure verified")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("ERROR: Python 3.8+ required")
        return False
    
    logger.info(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if .env exists
    if not Path('.env').exists():
        if Path('.env.example').exists():
            logger.warning("⚠ .env file not found!")
            logger.warning("  Creating from .env.example template...")
            import shutil
            shutil.copy('.env.example', '.env')
            logger.info("✓ .env created (please edit with your settings)")
            logger.warning("\n⚠ IMPORTANT: Edit .env file before proceeding:")
            logger.warning("  - Set MySQL credentials")
            logger.warning("  - Set correct CAPTURE_INTERFACE")
            logger.warning("\nThen restart the application")
            return False
        else:
            logger.error("ERROR: .env.example not found!")
            return False
    
    logger.info("✓ Configuration file found")
    
    # Check required directories
    dirs_to_create = ['logs', 'models', 'rules', 'database']
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
    
    logger.info("✓ Required directories ready")
    
    # Try to import main modules
    logger.info("\nVerifying dependencies...")
    try:
        import flask
        logger.info("✓ Flask available")
    except ImportError:
        logger.error("ERROR: Flask not installed")
        logger.error("Run: pip install -r requirements.txt")
        return False
    
    try:
        import mysql.connector
        logger.info("✓ MySQL connector available")
    except ImportError:
        logger.warning("⚠ MySQL connector not installed (will install with requirements)")
    
    try:
        import scapy
        logger.info("✓ Scapy available")
    except ImportError:
        logger.warning("⚠ Scapy not installed (will install with requirements)")
    
    # Check if main app module can be imported
    try:
        from config import Config
        logger.info("✓ Configuration module loaded")
    except Exception as e:
        logger.error(f"ERROR loading config: {str(e)}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ All checks passed!")
    logger.info("=" * 60)
    logger.info("\nStarting Flask application...")
    logger.info("Dashboard will be available at: http://localhost:5000")
    logger.info("API health check: http://localhost:5000/api/health")
    logger.info("\nPress Ctrl+C to stop the server\n")
    
    # Import and run Flask app
    try:
        from app import app, initialize_system, logger as app_logger
        
        if initialize_system():
            logger.info("✓ System initialized successfully")
            logger.info("\nStarting web server...\n")
            
            # Run Flask app
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                use_reloader=False
            )
        else:
            logger.error("Failed to initialize system")
            return False
            
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        logger.error("Check logs/app.log for details")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)
