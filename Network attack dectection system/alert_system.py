"""
Alert System
Sends notifications about detected threats
"""

import logging
import json
from typing import List, Dict, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class AlertSystem:
    """Generate and send alerts"""
    
    def __init__(self, email_config: Dict = None):
        self.email_config = email_config or {}
        self.alerts = []
        self.alert_channels = {
            'email': self._send_email,
            'sms': self._send_sms,
            'dashboard': self._send_to_dashboard,
            'log': self._log_alert
        }
    
    def send_alert(self, threat: Dict, channels: List[str] = None) -> List[Dict]:
        """Send alert through specified channels"""
        if channels is None:
            channels = ['log', 'dashboard']
        
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'threat_type': threat.get('type', 'Unknown'),
            'severity': threat.get('severity', 'UNKNOWN'),
            'source_ip': threat.get('source_ip', 'Unknown'),
            'details': threat.get('details', ''),
            'channels': channels,
            'sent': []
        }
        
        for channel in channels:
            if channel in self.alert_channels:
                try:
                    result = self.alert_channels[channel](threat)
                    alert_record['sent'].append({
                        'channel': channel,
                        'status': 'sent',
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    alert_record['sent'].append({
                        'channel': channel,
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.error(f"Failed to send alert via {channel}: {str(e)}")
        
        self.alerts.append(alert_record)
        return alert_record['sent']
    
    def _send_email(self, threat: Dict) -> bool:
        """Send email alert"""
        try:
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            sender_email = self.email_config.get('sender_email')
            sender_password = self.email_config.get('sender_password')
            recipient_email = self.email_config.get('recipient_email')
            
            if not all([sender_email, sender_password, recipient_email]):
                logger.warning("Email credentials not configured")
                return False
            
            subject = f"[{threat.get('severity', 'MEDIUM')}] {threat.get('type', 'Unknown')} Threat Detected"
            
            body = f"""
            Network Threat Alert
            =====================
            
            Threat Type: {threat.get('type', 'Unknown')}
            Severity: {threat.get('severity', 'UNKNOWN')}
            Timestamp: {datetime.now().isoformat()}
            Source IP: {threat.get('source_ip', 'Unknown')}
            
            Details:
            {threat.get('details', 'No details available')}
            
            Please review the dashboard for more information.
            """
            
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Email alert sent to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False
    
    def _send_sms(self, threat: Dict) -> bool:
        """Send SMS alert (placeholder)"""
        # In production, integrate with Twilio or similar service
        logger.info(f"SMS alert would be sent: {threat.get('type')}")
        return True
    
    def _send_to_dashboard(self, threat: Dict) -> bool:
        """Send alert to dashboard"""
        # This would be implemented with WebSocket or similar
        logger.info(f"Alert sent to dashboard: {threat.get('type')}")
        return True
    
    def _log_alert(self, threat: Dict) -> bool:
        """Log alert to file"""
        logger.warning(
            f"THREAT ALERT - Type: {threat.get('type', 'Unknown')}, "
            f"Severity: {threat.get('severity', 'UNKNOWN')}, "
            f"Source: {threat.get('source_ip', 'Unknown')}, "
            f"Details: {threat.get('details', '')}"
        )
        return True
    
    def get_alerts(self) -> List[Dict]:
        """Get all alerts"""
        return self.alerts
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict]:
        """Get alerts by severity"""
        return [a for a in self.alerts if a['severity'] == severity]
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict]:
        """Get recent alerts within specified time window"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        recent = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time > cutoff:
                recent.append(alert)
        
        return recent
    
    def clear_alerts(self) -> None:
        """Clear alert history"""
        self.alerts.clear()
        logger.info("Alert history cleared")
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        if not self.alerts:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_type': {}
            }
        
        by_severity = {}
        by_type = {}
        
        for alert in self.alerts:
            severity = alert.get('severity', 'UNKNOWN')
            threat_type = alert.get('threat_type', 'Unknown')
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[threat_type] = by_type.get(threat_type, 0) + 1
        
        return {
            'total_alerts': len(self.alerts),
            'by_severity': by_severity,
            'by_type': by_type,
            'latest_alert': self.alerts[-1] if self.alerts else None
        }
