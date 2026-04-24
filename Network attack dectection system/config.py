import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application Configuration"""
    
    # Flask Config
    DEBUG = os.getenv('FLASK_DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # MySQL Database Config
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'network_attack_detection')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Network Capture Config
    PACKET_COUNT = int(os.getenv('PACKET_COUNT', 1000))
    CAPTURE_INTERFACE = os.getenv('CAPTURE_INTERFACE', 'eth0')
    
    # Alert Config
    ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'alerts@example.com')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    
    # Threat Detection Config
    THREAT_THRESHOLD = float(os.getenv('THREAT_THRESHOLD', 0.7))
    AUTO_RESPONSE_ENABLED = os.getenv('AUTO_RESPONSE_ENABLED', 'True') == 'True'
    
    # Logging
    LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
