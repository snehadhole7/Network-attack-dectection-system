"""
Auto Response System
Automatically responds to detected threats
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseAction:
    """Actions that can be taken in response to threats"""
    
    BLOCK_IP = 'block_ip'
    RATE_LIMIT = 'rate_limit'
    DISABLE_PORT = 'disable_port'
    ISOLATE_HOST = 'isolate_host'
    KILL_CONNECTION = 'kill_connection'
    LOG_INCIDENT = 'log_incident'
    ALERT = 'alert'

class ResponseSystem:
    """Execute automated responses to threats"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.rate_limited_ips = {}
        self.disabled_ports = set()
        self.response_log = []
        self.enabled = True
    
    def execute_response(self, threat: Dict, auto_response_enabled: bool = True) -> List[Dict]:
        """Execute appropriate response for a threat"""
        if not auto_response_enabled or not self.enabled:
            return [{'action': ResponseAction.LOG_INCIDENT, 'status': 'logged'}]
        
        responses = []
        threat_type = threat.get('type', '')
        severity = threat.get('severity', '')
        source_ip = threat.get('source_ip', '')
        
        # Determine response based on threat type and severity
        if threat_type == 'Port Scan':
            responses.append(self._rate_limit_ip(source_ip))
            responses.append(self._log_incident(threat))
        
        elif threat_type == 'Brute Force':
            responses.append(self._block_ip(source_ip))
            responses.append(self._alert(threat))
            responses.append(self._log_incident(threat))
        
        elif threat_type == 'DDoS':
            responses.append(self._block_ip(source_ip))
            responses.append(self._rate_limit_ip(source_ip))
            responses.append(self._alert(threat, critical=True))
            responses.append(self._log_incident(threat))
        
        elif threat_type == 'Data Exfiltration':
            responses.append(self._block_ip(source_ip))
            responses.append(self._kill_connection(source_ip))
            responses.append(self._alert(threat))
            responses.append(self._log_incident(threat))
        
        elif threat_type == 'Unauthorized Access':
            responses.append(self._rate_limit_ip(source_ip))
            responses.append(self._alert(threat))
            responses.append(self._log_incident(threat))
        
        else:
            responses.append(self._log_incident(threat))
        
        return responses
    
    def _block_ip(self, ip: str) -> Dict[str, Any]:
        """Block an IP address"""
        self.blocked_ips.add(ip)
        response = {
            'action': ResponseAction.BLOCK_IP,
            'target': ip,
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'details': f'IP {ip} has been blocked'
        }
        self.response_log.append(response)
        logger.warning(f"Blocked IP: {ip}")
        return response
    
    def _rate_limit_ip(self, ip: str, limit: int = 100) -> Dict[str, Any]:
        """Rate limit an IP address"""
        self.rate_limited_ips[ip] = {
            'limit': limit,
            'timestamp': datetime.now().isoformat()
        }
        response = {
            'action': ResponseAction.RATE_LIMIT,
            'target': ip,
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'details': f'IP {ip} rate limited to {limit} packets/sec'
        }
        self.response_log.append(response)
        logger.info(f"Rate limited IP: {ip}")
        return response
    
    def _disable_port(self, port: int) -> Dict[str, Any]:
        """Disable a port"""
        self.disabled_ports.add(port)
        response = {
            'action': ResponseAction.DISABLE_PORT,
            'target': port,
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'details': f'Port {port} has been disabled'
        }
        self.response_log.append(response)
        logger.warning(f"Disabled port: {port}")
        return response
    
    def _kill_connection(self, ip: str) -> Dict[str, Any]:
        """Terminate connections from an IP"""
        response = {
            'action': ResponseAction.KILL_CONNECTION,
            'target': ip,
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'details': f'All connections from {ip} have been terminated'
        }
        self.response_log.append(response)
        logger.warning(f"Killed connections from: {ip}")
        return response
    
    def _alert(self, threat: Dict, critical: bool = False) -> Dict[str, Any]:
        """Generate an alert"""
        response = {
            'action': ResponseAction.ALERT,
            'threat_type': threat.get('type', 'Unknown'),
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'severity': 'CRITICAL' if critical else threat.get('severity', 'MEDIUM'),
            'details': threat.get('details', 'Unknown threat')
        }
        self.response_log.append(response)
        level = logging.CRITICAL if critical else logging.WARNING
        logger.log(level, f"Alert: {threat.get('type')} - {threat.get('details')}")
        return response
    
    def _log_incident(self, threat: Dict) -> Dict[str, Any]:
        """Log an incident"""
        response = {
            'action': ResponseAction.LOG_INCIDENT,
            'threat_type': threat.get('type', 'Unknown'),
            'status': 'logged',
            'timestamp': datetime.now().isoformat(),
            'severity': threat.get('severity', 'UNKNOWN'),
            'source_ip': threat.get('source_ip', 'Unknown'),
            'details': threat.get('details', '')
        }
        self.response_log.append(response)
        return response
    
    def unblock_ip(self, ip: str) -> Dict[str, Any]:
        """Unblock an IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"Unblocked IP: {ip}")
            return {
                'action': ResponseAction.BLOCK_IP,
                'target': ip,
                'status': 'removed',
                'timestamp': datetime.now().isoformat()
            }
        return {'status': 'not_found', 'ip': ip}
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        return list(self.blocked_ips)
    
    def get_rate_limited_ips(self) -> Dict[str, Any]:
        """Get rate limited IPs"""
        return self.rate_limited_ips
    
    def get_response_log(self) -> List[Dict]:
        """Get response log"""
        return self.response_log
    
    def clear_log(self) -> None:
        """Clear response log"""
        self.response_log.clear()
        logger.info("Response log cleared")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def get_ip_rate_limit(self, ip: str) -> int:
        """Get rate limit for IP"""
        if ip in self.rate_limited_ips:
            return self.rate_limited_ips[ip]['limit']
        return -1  # Not rate limited
