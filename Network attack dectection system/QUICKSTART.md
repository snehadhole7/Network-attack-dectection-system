# Quick Start Guide

## Installation & Running (5 minutes)

### Windows

1. **Open Command Prompt/PowerShell**
   ```bash
   cd "Network attack detection system"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings**
   - Copy `.env.example` to `.env`
   - Edit `.env`:
     - MySQL credentials (or use defaults for localhost)
     - Change `CAPTURE_INTERFACE=Ethernet` (or your network adapter)

4. **Start MySQL**
   - Make sure MySQL Server is running

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Open Dashboard**
   - Navigate to: http://localhost:5000

### Linux/macOS

1. **Open Terminal**
   ```bash
   cd "Network attack detection system"
   ```

2. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure Settings**
   ```bash
   cp .env.example .env
   nano .env
   ```
   - Update MySQL credentials if needed
   - Set `CAPTURE_INTERFACE=eth0` (or your interface)

4. **Start MySQL**
   ```bash
   # macOS with Homebrew
   brew services start mysql

   # Linux (Ubuntu/Debian)
   sudo systemctl start mysql
   ```

5. **Run the Application (requires sudo for packet capture)**
   ```bash
   sudo python3 app.py
   ```

6. **Open Dashboard**
   - Navigate to: http://localhost:5000

## First Time Setup

After starting the app:

1. **Wait for initialization** - System will create database tables automatically
2. **Check System Health** - Visit http://localhost:5000/api/health
3. **Review Dashboard** - http://localhost:5000 should load successfully
4. **Check Logs** - View `logs/app.log` for any errors

## Common Issues & Solutions

### Port Already in Use
If port 5000 is busy:
```python
# Edit app.py, change:
app.run(host='0.0.0.0', port=5001)  # Change to different port
```

### MySQL Connection Failed
```bash
# Check MySQL is running
# For Windows: Services → MySQL
# For macOS: brew services list
# For Linux: sudo systemctl status mysql

# Verify credentials in .env file
```

### No Packets Captured
```bash
# Find your network interface:
# Windows: ipconfig
# Linux: ip link show
# Update CAPTURE_INTERFACE in .env
```

### Permission Denied (Linux/macOS)
```bash
# Run with sudo for packet capture
sudo python3 app.py
```

## Testing the System

### Simulate Network Traffic
```bash
# Linux: Use ping
ping google.com

# Generate traffic for analysis
# The system will capture and analyze it
```

### Check Dashboard Data
1. Go to http://localhost:5000
2. Look at "Recent Alerts" section
3. Check "Threats" tab for detected threats
4. View "Incidents" for detailed records

## Key Features to Try

1. **Dashboard Tab** - Real-time statistics and graphs
2. **Incidents Tab** - View all detected incidents
3. **Threats Tab** - See threat classification and severity
4. **Blocked IPs Tab** - IP blocking management
5. **Alerts Tab** - Alert timeline and history
6. **Reports Tab** - Generate daily/weekly/monthly reports

## Configuration Reference

### .env File Important Settings

```env
# Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# Network (IMPORTANT)
CAPTURE_INTERFACE=eth0          # Linux
CAPTURE_INTERFACE=Ethernet      # Windows

# Threat Detection
THREAT_THRESHOLD=0.7
AUTO_RESPONSE_ENABLED=True

# Logging
LOG_LEVEL=INFO
```

## File Structure

```
├── app.py                    # Main application
├── config.py                 # Configuration
├── *.py                      # Core modules
├── database/
│   └── db_setup.py          # Database management
├── templates/
│   └── dashboard.html       # Web interface
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
├── logs/
│   └── app.log             # Application logs
├── README.md               # Full documentation
└── .env                    # Configuration (create from .env.example)
```

## Stopping the Application

- **Windows/Linux/macOS**: Press `Ctrl + C` in the terminal
- MySQL can continue running (optional)

## Next Steps

1. **Read the full README.md** for comprehensive documentation
2. **Configure email alerts** in .env for real notifications
3. **Set up automatic reports** (modify reporting.py)
4. **Customize detection rules** in threat_detector.py
5. **Deploy to production** with proper security hardening

## Support

- Check `logs/app.log` for error messages
- Review API documentation in README.md
- Verify system health: http://localhost:5000/api/health

---

**Happy monitoring! 🛡️**
