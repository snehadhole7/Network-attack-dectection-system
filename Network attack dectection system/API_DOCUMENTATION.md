# Network Attack Detection System - API Documentation

## Overview
Comprehensive API for the Network Attack Detection System with advanced features including ML-based threat detection, behavioral analytics, incident response automation, blockchain audit trails, compliance reporting, and threat intelligence.

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

### Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Analyst**: username: `analyst`, password: `analyst123`
- **Viewer**: username: `viewer`, password: `viewer123`

---

## Core Endpoints

### Authentication
- **POST** `/api/auth/login` - User login
- **POST** `/api/auth/logout` - User logout
- **GET** `/api/auth/user` - Get current user info

### System Health
- **GET** `/api/health` - System health check with feature status
- **GET** `/api/stats` - System statistics

### Incidents & Threats
- **GET** `/api/incidents` - Get recent incidents
- **GET** `/api/incidents/<id>` - Get specific incident
- **GET** `/api/threats` - Get detected threats
- **GET** `/api/analysis` - Get traffic analysis

### Response Management
- **GET** `/api/blocked-ips` - Get blocked IP addresses
- **DELETE** `/api/blocked-ips/<ip>` - Unblock an IP

### Alerts & Reporting
- **GET** `/api/alerts` - Get alerts
- **GET** `/api/alerts/stats` - Get alert statistics
- **GET** `/api/reports/daily` - Get daily report
- **GET** `/api/reports/weekly` - Get weekly report
- **GET** `/api/reports/monthly` - Get monthly report
- **POST** `/api/reports/export/<format>` - Export report (json/html)

### Dashboard
- **GET** `/api/dashboard-data` - Get comprehensive dashboard data

---

## Advanced Features

### Machine Learning Detection
- **POST** `/api/ml/train` - Train ML threat detection model
- **POST** `/api/ml/predict` - Predict threats using ML
- **GET** `/api/ml/status` - Get ML model status

### Behavioral Analytics
- **POST** `/api/behavioral/baseline` - Establish behavioral baseline
- **GET** `/api/behavioral/anomalies` - Detect behavioral anomalies
- **GET** `/api/behavioral/profile/<ip>` - Get behavioral profile for IP

### Incident Response Automation
- **POST** `/api/incidents/playbook/<type>` - Execute incident response playbook
- **GET** `/api/incidents/playbooks` - Get available playbooks
- **GET** `/api/incidents/history` - Get playbook execution history

### Blockchain Audit Trail
- **POST** `/api/audit/add` - Add audit event
- **POST** `/api/audit/mine` - Mine new audit block
- **GET** `/api/audit/logs` - Get audit logs
- **GET** `/api/audit/chain-stats` - Get blockchain statistics
- **GET** `/api/audit/validate` - Validate blockchain integrity

### Compliance Reporting
- **GET** `/api/compliance/<framework>` - Get compliance report
  - Supported frameworks: `gdpr`, `hipaa`, `pci_dss`, `iso27001`, `nist`, `cis`
- **GET** `/api/compliance/frameworks` - Get available frameworks

### Threat Intelligence
- **GET** `/api/threat-intel/summary` - Get threat intelligence summary
- **POST** `/api/threat-intel/correlate` - Correlate threats
- **POST** `/api/threat-intel/ioc/add` - Add Indicator of Compromise
- **POST** `/api/threat-intel/ioc/check` - Check IOC
- **GET** `/api/threat-intel/landscape` - Get threat landscape report

### Real-Time Updates
- **GET** `/api/realtime/status` - Get WebSocket connection status
- **GET** `/api/realtime/updates` - Get latest updates (polling fallback)

---

## Request/Response Examples

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "admin",
    "role": "admin",
    "email": "admin@nads.local"
  },
  "message": "Login successful"
}
```

### Train ML Model
```bash
POST /api/ml/train
Authorization: Bearer <token>

Response:
{
  "message": "Model trained successfully"
}
```

### Execute Incident Playbook
```bash
POST /api/incidents/playbook/brute_force
Authorization: Bearer <token>
Content-Type: application/json

{
  "source_ip": "192.168.1.100",
  "target_port": 22
}

Response:
{
  "playbook": "brute_force",
  "actions": [
    {
      "action": "block_ip",
      "target": "192.168.1.100",
      "priority": "critical",
      "duration": "1h",
      "description": "Immediately block brute force source"
    },
    ...
  ],
  "status": "executed"
}
```

### Generate Compliance Report
```bash
GET /api/compliance/gdpr
Authorization: Bearer <token>

Response:
{
  "framework": "GDPR",
  "generated_at": "2024-04-24T10:30:00",
  "compliance_checks": {
    "data_protection": {
      "status": "COMPLIANT",
      "findings": "Found 0 potential data breaches",
      "requirement": "Article 32: Security of Processing"
    },
    ...
  },
  "recommendations": [...]
}
```

### Add Indicator of Compromise
```bash
POST /api/threat-intel/ioc/add
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "IP",
  "value": "192.168.1.100",
  "confidence": 0.95
}

Response:
{
  "ioc_id": "ioc_0",
  "message": "IOC added"
}
```

---

## Feature Availability
The system gracefully handles missing dependencies. Check `/api/health` to see which features are enabled:

```json
{
  "features_enabled": {
    "ml_detection": true,
    "behavioral_analysis": true,
    "incident_response": true,
    "blockchain_audit": true,
    "compliance_reporting": true,
    "threat_intelligence": true,
    "realtime_updates": true,
    "network_capture": true
  }
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

### 503 Service Unavailable
```json
{
  "error": "Feature not available"
}
```

---

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Traditional Deployment
```bash
python app.py
```

### Access Dashboard
- URL: `http://localhost:5000`
- Default credentials included in `.env`

---

## Performance Considerations

1. **ML Model Training**: May take time on large datasets
2. **Blockchain Audit**: Mine blocks periodically to prevent queue overflow
3. **WebSocket**: Reduces server load compared to 10-second polling
4. **Behavioral Analytics**: Baseline should be established on clean data

---

## Support & Documentation

For detailed implementation, see:
- `IMPLEMENTATION_SUMMARY.md` - Architecture overview
- `QUICKSTART.md` - Quick start guide
- `README.md` - Project documentation
