# Network Attack Detection System

A comprehensive real-time network attack detection and prevention system built with Python, Flask, and MySQL. The system captures live network traffic, analyzes it for threats, and provides automated responses with a complete web-based dashboard.

## 🎯 Features

### Core Capabilities
- **Real-Time Packet Capture**: Captures and analyzes live network packets using Scapy
- **Threat Detection**: Multiple detection methods including:
  - Port Scanning Detection
  - Brute Force Attack Detection
  - DDoS Detection
  - Data Exfiltration Detection
  - Unauthorized Access Detection
  - Anomalous Behavior Detection

### Response System
- **Automated Responses**:
  - Block malicious IP addresses
  - Rate limiting on suspicious traffic
  - Disable compromised ports
  - Kill active connections

### Alerting & Monitoring
- **Multi-Channel Alerts**:
  - Email notifications
  - SMS alerts (placeholder)
  - Dashboard notifications
  - System logging

### Reporting & Analytics
- **Security Reports**:
  - Daily reports
  - Weekly reports
  - Monthly reports
  - Trend analysis
  - Compliance documentation

### Web Dashboard
- **Real-Time Monitoring**:
  - Live threat detection updates
  - Interactive charts and graphs
  - Incident tracking
  - Blocked IP management
  - Alert history

## 📋 System Architecture

```
Network Traffic
     ↓
Packet Capture → Data Preprocessing → Traffic Analysis
     ↓              ↓                    ↓
  [Scapy]    [Cleaning/Formatting]  [Statistics]
     ↓
Rule Engine + AI Detection
     ↓
├─ Port Scans      → Threat Identified?
├─ Brute Force        ├─ YES → Severity Check
├─ DDoS              │        ↓
├─ Exfiltration      │    Auto Response
└─ Other            │        ↓
     ↓               │    Alerts + Logging
    NO              │
     ↓              └─ Normal Traffic
  Log Traffic
     ↓
Database Storage (MySQL)
     ↓
Flask Dashboard + Reports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server
- Administrator/Root privileges (for packet capture)
- Windows, macOS, or Linux

### Installation

1. **Clone or download the project**
```bash
cd "Network attack detection system"
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup MySQL Database**
```bash
# The application will automatically create the database and tables
# Just ensure MySQL is running and credentials are correct
```

4. **Configure environment variables**
```bash
# Copy .env.example to .env
copy .env.example .env

# Edit .env with your configuration
# Key settings:
# - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD
# - CAPTURE_INTERFACE (eth0 on Linux, appropriate interface on Windows)
# - ALERT_EMAIL credentials
```

5. **Run the application**
```bash
python app.py
```

6. **Access the dashboard**
Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
Network attack detection system/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── network_capture.py          # Packet capture module
├── data_preprocessor.py        # Data cleaning & formatting
├── traffic_analyzer.py         # Traffic analysis module
├── threat_detector.py          # Threat detection engine
├── response_system.py          # Automated response system
├── alert_system.py             # Alert management
├── reporting.py                # Report generation
├── database/
│   └── db_setup.py             # MySQL database setup
├── models/                     # ML models directory
├── rules/                      # Detection rules
├── logs/                       # Application logs
├── static/
│   ├── css/
│   │   └── style.css           # Dashboard styling
│   └── js/
│       └── dashboard.js        # Dashboard JavaScript
└── templates/
    └── dashboard.html          # Web dashboard
```

## 🛠️ Configuration Guide

### MySQL Setup

The application automatically creates the following tables:
- `incidents` - Detected threats and attacks
- `network_packets` - Captured packet data
- `blocked_ips` - List of blocked IP addresses
- `alerts` - Alert history
- `responses` - Auto-response actions
- `traffic_stats` - Network statistics
- `reports` - Generated reports

### Capture Interface

**Linux:**
```python
CAPTURE_INTERFACE=eth0  # or appropriate interface
```

**Windows:**
```python
CAPTURE_INTERFACE=Ethernet  # or appropriate interface
```

**Find your interface:**
```bash
# Linux
ip link show

# Windows
ipconfig
```

### Alert Configuration

For email alerts, configure SMTP:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ALERT_EMAIL=your-email@gmail.com
```

## 📊 Dashboard Features

### Main Dashboard
- System status and health metrics
- Real-time threat statistics
- Protocol distribution charts
- Top source IPs
- Recent alerts

### Incidents Tab
- Complete incident history
- Searchable incident table
- Severity filtering
- Attack details

### Threats Tab
- Active threat list
- Threat type filtering
- Severity classification
- Confidence scores

### Blocked IPs Tab
- List of blocked IP addresses
- Block reason tracking
- One-click unblocking
- Block duration tracking

### Alerts Tab
- Alert timeline
- Alert history
- Severity-based filtering
- Channel information

### Reports Tab
- Daily, weekly, and monthly reports
- Trend analysis
- Recommendations
- Export functionality

## 🔐 Security Features

### Detection Capabilities
1. **Port Scanning**: Detects unusual port access patterns
2. **Brute Force**: Identifies multiple failed login attempts
3. **DDoS**: Detects distributed denial of service attacks
4. **Data Exfiltration**: Monitors for large data transfers
5. **Unauthorized Access**: Detects suspicious access patterns
6. **Protocol Anomalies**: Identifies unusual protocol usage

### Response Actions
1. **IP Blocking**: Immediately block malicious IPs
2. **Rate Limiting**: Restrict traffic from suspicious sources
3. **Connection Killing**: Terminate established connections
4. **Port Disabling**: Disable compromised ports
5. **Incident Logging**: Comprehensive audit trail

## 📈 Performance Metrics

- **Packet Processing**: Processes up to 10,000+ packets per session
- **Detection Latency**: Real-time threat detection
- **Storage**: Efficient MySQL storage of incident data
- **Dashboard Refresh**: 10-second update interval
- **Concurrent Users**: Web dashboard supports multiple concurrent users

## 🔍 Threat Detection Rules

### Port Scanning
- Triggered when: >20 unique destination ports from single source
- Severity: MEDIUM
- Response: Rate limiting

### Brute Force
- Triggered when: >50 connection attempts to single port
- Severity: HIGH
- Response: IP blocking

### DDoS Attack
- Triggered when: >10,000 packets OR >1000 packets to single destination from >10 sources
- Severity: CRITICAL
- Response: IP blocking + rate limiting

### Data Exfiltration
- Triggered when: >10MB of outgoing traffic
- Severity: HIGH
- Response: IP blocking + connection killing

## 📝 Logging

Logs are stored in the `logs/` directory:
- `app.log` - Main application log
- Configurable log level (DEBUG, INFO, WARNING, ERROR)

## 🚨 Troubleshooting

### Permission Denied (Packet Capture)
```bash
# Linux: Run with sudo
sudo python app.py

# Windows: Run as Administrator
# Or use Npcap/WinPcap
```

### MySQL Connection Error
- Check MySQL service is running
- Verify credentials in .env file
- Check MYSQL_HOST is correct

### No Packets Captured
- Verify CAPTURE_INTERFACE is correct
- Check network connectivity
- Ensure proper permissions

### Dashboard Not Loading
- Check Flask server is running on port 5000
- Clear browser cache
- Check browser console for errors

## 📚 API Endpoints

### Statistics
- `GET /api/stats` - System statistics
- `GET /api/health` - System health check

### Incidents
- `GET /api/incidents` - Get recent incidents
- `GET /api/incidents/<id>` - Get incident details

### Threats
- `GET /api/threats` - Get detected threats
- `GET /api/threats?severity=HIGH` - Filter by severity

### Analysis
- `GET /api/analysis` - Get traffic analysis

### Blocked IPs
- `GET /api/blocked-ips` - List blocked IPs
- `DELETE /api/blocked-ips/<ip>` - Unblock IP

### Alerts
- `GET /api/alerts` - Get alert history
- `GET /api/alerts/stats` - Alert statistics

### Reports
- `GET /api/reports/daily` - Daily report
- `GET /api/reports/weekly` - Weekly report
- `GET /api/reports/monthly` - Monthly report

## 🔄 Workflow

1. **Initialization**: System initializes all components and database
2. **Capture**: Network packets are captured from the configured interface
3. **Preprocessing**: Raw packets are cleaned and normalized
4. **Analysis**: Traffic patterns and statistics are calculated
5. **Detection**: Threats are identified using rule-based detection
6. **Response**: Automatic responses are executed for identified threats
7. **Alerting**: Alerts are sent through configured channels
8. **Logging**: All incidents are logged to database and file system
9. **Reporting**: Regular reports are generated and made available

## 🤝 Contributing

To extend the system:

1. **Add Detection Rules**: Modify `threat_detector.py`
2. **Custom Responses**: Extend `response_system.py`
3. **New Dashboards**: Add templates to `templates/`
4. **ML Models**: Place models in `models/` directory

## 📄 License

This project is provided as-is for educational and security purposes.

## ⚠️ Disclaimer

This system should only be used on networks you own or have explicit permission to monitor. Unauthorized network monitoring may be illegal in your jurisdiction.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs in `logs/app.log`
3. Verify configuration in `.env` file
4. Check MySQL connectivity

## 🎓 Educational Use

This system is designed to help understand:
- Network security concepts
- Attack patterns and detection methods
- Real-time monitoring systems
- Web-based dashboard development
- Database design for security applications

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Production Ready
