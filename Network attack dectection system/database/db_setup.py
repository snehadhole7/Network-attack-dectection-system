"""
Database Setup Module
Creates and manages MySQL database schema
"""

import logging
from typing import List, Dict, Any

# Make MySQL optional
try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    Error = Exception

logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Setup and manage database"""
    
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to MySQL server"""
        if not MYSQL_AVAILABLE:
            logger.warning("MySQL connector not available - running in demo mode")
            self.connection = None
            return False
        
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            logger.info("Connected to MySQL server")
            return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def create_database(self) -> bool:
        """Create database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.connection.commit()
            cursor.close()
            logger.info(f"Database '{self.database}' created/verified")
            return True
        except Error as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def select_database(self) -> bool:
        """Select the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {self.database}")
            cursor.close()
            logger.info(f"Database '{self.database}' selected")
            return True
        except Error as e:
            logger.error(f"Error selecting database: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create all necessary tables"""
        tables = {
            'incidents': """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    threat_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    source_ip VARCHAR(45) NOT NULL,
                    destination_ip VARCHAR(45),
                    source_port INT,
                    destination_port INT,
                    protocol VARCHAR(20),
                    details TEXT,
                    confidence FLOAT,
                    response_action VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_source_ip (source_ip),
                    INDEX idx_severity (severity),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_threat_type (threat_type)
                )
            """,
            'network_packets': """
                CREATE TABLE IF NOT EXISTS network_packets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    source_ip VARCHAR(45) NOT NULL,
                    destination_ip VARCHAR(45) NOT NULL,
                    source_port INT,
                    destination_port INT,
                    protocol VARCHAR(20),
                    packet_size INT,
                    flags VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_source_ip (source_ip),
                    INDEX idx_destination_ip (destination_ip),
                    INDEX idx_timestamp (timestamp)
                )
            """,
            'blocked_ips': """
                CREATE TABLE IF NOT EXISTS blocked_ips (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip_address VARCHAR(45) NOT NULL UNIQUE,
                    reason VARCHAR(255),
                    severity VARCHAR(20),
                    blocked_at DATETIME NOT NULL,
                    unblocked_at DATETIME,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_ip_address (ip_address),
                    INDEX idx_is_active (is_active)
                )
            """,
            'alerts': """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    threat_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    source_ip VARCHAR(45),
                    message TEXT,
                    channels VARCHAR(255),
                    sent_status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_severity (severity),
                    INDEX idx_created_at (created_at)
                )
            """,
            'responses': """
                CREATE TABLE IF NOT EXISTS responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    incident_id INT,
                    action VARCHAR(100) NOT NULL,
                    target VARCHAR(45),
                    status VARCHAR(20),
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (incident_id) REFERENCES incidents(id),
                    INDEX idx_action (action),
                    INDEX idx_status (status)
                )
            """,
            'traffic_stats': """
                CREATE TABLE IF NOT EXISTS traffic_stats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    total_packets INT,
                    total_bytes BIGINT,
                    unique_sources INT,
                    unique_destinations INT,
                    protocol_tcp INT DEFAULT 0,
                    protocol_udp INT DEFAULT 0,
                    protocol_icmp INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_timestamp (timestamp)
                )
            """,
            'reports': """
                CREATE TABLE IF NOT EXISTS reports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    report_type VARCHAR(50) NOT NULL,
                    report_date DATE NOT NULL,
                    report_content LONGTEXT,
                    total_incidents INT,
                    critical_incidents INT,
                    high_incidents INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_report_type (report_type),
                    INDEX idx_report_date (report_date)
                )
            """
        }
        
        try:
            cursor = self.connection.cursor()
            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                logger.info(f"Table '{table_name}' created/verified")
            self.connection.commit()
            cursor.close()
            logger.info("All tables created successfully")
            return True
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def insert_incident(self, incident: Dict[str, Any]) -> int:
        """Insert an incident into the database"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO incidents 
                (timestamp, threat_type, severity, source_ip, destination_ip, 
                 source_port, destination_port, protocol, details, confidence, response_action)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                incident.get('timestamp'),
                incident.get('type'),
                incident.get('severity'),
                incident.get('source_ip', 'Unknown'),
                incident.get('destination_ip'),
                incident.get('source_port'),
                incident.get('destination_port'),
                incident.get('protocol'),
                incident.get('details'),
                incident.get('confidence'),
                incident.get('response_action')
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            incident_id = cursor.lastrowid
            cursor.close()
            
            logger.debug(f"Incident {incident_id} inserted into database")
            return incident_id
        except Error as e:
            logger.error(f"Error inserting incident: {e}")
            return -1
    
    def insert_blocked_ip(self, ip: str, reason: str, severity: str) -> bool:
        """Insert a blocked IP"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO blocked_ips (ip_address, reason, severity, blocked_at, is_active)
                VALUES (%s, %s, %s, NOW(), TRUE)
                ON DUPLICATE KEY UPDATE is_active = TRUE
            """
            cursor.execute(query, (ip, reason, severity))
            self.connection.commit()
            cursor.close()
            logger.info(f"IP {ip} blocked in database")
            return True
        except Error as e:
            logger.error(f"Error blocking IP: {e}")
            return False
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ip_address FROM blocked_ips WHERE is_active = TRUE")
            ips = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return ips
        except Error as e:
            logger.error(f"Error getting blocked IPs: {e}")
            return []
    
    def get_recent_incidents(self, limit: int = 100) -> List[Dict]:
        """Get recent incidents"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT %s",
                (limit,)
            )
            incidents = cursor.fetchall()
            cursor.close()
            return incidents
        except Error as e:
            logger.error(f"Error getting incidents: {e}")
            return []
    
    def get_incident_count_by_severity(self) -> Dict[str, int]:
        """Get incident count by severity"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT severity, COUNT(*) as count FROM incidents GROUP BY severity"
            )
            results = dict(cursor.fetchall())
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Error getting incident counts: {e}")
            return {}
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
