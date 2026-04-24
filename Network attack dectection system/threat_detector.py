"""
Threat Detection Module
Detects attacks using rule-based and AI methods
"""

import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ThreatType(Enum):
    """Types of threats"""
    PORT_SCAN = 'Port Scan'
    BRUTE_FORCE = 'Brute Force'
    DDOS = 'DDoS'
    DATA_EXFILTRATION = 'Data Exfiltration'
    UNAUTHORIZED_ACCESS = 'Unauthorized Access'
    MALWARE_COMMUNICATION = 'Malware Communication'
    SUSPICIOUS_PROTOCOL = 'Suspicious Protocol'
    ANOMALOUS_BEHAVIOR = 'Anomalous Behavior'

class ThreatDetector:
    """Detect threats in network traffic"""
    
    def __init__(self):
        self.packets = []
        self.threats = []
        self.traffic_history = defaultdict(list)
        self.threat_threshold = 0.7
    
    def load_packets(self, packets: List[Dict]) -> None:
        """Load packets for threat detection"""
        self.packets = packets
    
    def detect_threats(self, packets: List[Dict], analysis: Dict) -> List[Dict]:
        """Perform threat detection"""
        self.load_packets(packets)
        self.threats = []
        
        # Run various detection methods
        self._detect_port_scans(analysis)
        self._detect_brute_force(analysis)
        self._detect_ddos(analysis)
        self._detect_data_exfiltration(analysis)
        self._detect_unauthorized_access()
        self._detect_suspicious_protocols()
        self._detect_anomalous_behavior(analysis)
        
        logger.info(f"Threat detection complete: {len(self.threats)} threats found")
        return self.threats
    
    def _detect_port_scans(self, analysis: Dict) -> None:
        """Detect port scanning activity"""
        suspicious_ports = analysis.get('suspicious_ports', [])
        
        # High number of unique destination ports from single source
        src_port_traffic = defaultdict(lambda: {'unique_dst_ports': set(), 'count': 0})
        for packet in self.packets:
            src_ip = packet.get('src_ip')
            dst_port = packet.get('dst_port')
            if src_ip and dst_port:
                src_port_traffic[src_ip]['unique_dst_ports'].add(dst_port)
                src_port_traffic[src_ip]['count'] += 1
        
        for src_ip, traffic_data in src_port_traffic.items():
            unique_ports = len(traffic_data['unique_dst_ports'])
            if unique_ports > 20:
                threat = {
                    'timestamp': datetime.now().isoformat(),
                    'type': ThreatType.PORT_SCAN.value,
                    'source_ip': src_ip,
                    'severity': ThreatSeverity.MEDIUM.name,
                    'confidence': min(1.0, unique_ports / 100),
                    'details': f'Possible port scan: {unique_ports} unique ports targeted',
                    'affected_ips': [src_ip]
                }
                self.threats.append(threat)
                logger.warning(f"Port scan detected from {src_ip}: {unique_ports} ports")
    
    def _detect_brute_force(self, analysis: Dict) -> None:
        """Detect brute force attacks"""
        # High number of connections to same destination port
        port_access = defaultdict(lambda: defaultdict(int))
        
        for packet in self.packets:
            src_ip = packet.get('src_ip')
            dst_ip = packet.get('dst_ip')
            dst_port = packet.get('dst_port')
            
            if dst_port in [22, 3389, 445, 3306, 5432]:  # Common brute force targets
                key = f"{dst_ip}:{dst_port}"
                port_access[src_ip][key] += 1
        
        for src_ip, targets in port_access.items():
            for target, count in targets.items():
                if count > 50:
                    threat = {
                        'timestamp': datetime.now().isoformat(),
                        'type': ThreatType.BRUTE_FORCE.value,
                        'source_ip': src_ip,
                        'severity': ThreatSeverity.HIGH.name,
                        'confidence': min(1.0, count / 500),
                        'details': f'Possible brute force: {count} attempts to {target}',
                        'affected_ips': [src_ip]
                    }
                    self.threats.append(threat)
                    logger.warning(f"Brute force detected from {src_ip} to {target}")
    
    def _detect_ddos(self, analysis: Dict) -> None:
        """Detect DDoS attacks"""
        traffic_rate = analysis.get('traffic_rate', {})
        total_packets = traffic_rate.get('total_packets', 0)
        
        # Check for abnormally high packet count
        if total_packets > 10000:
            # Analyze if multiple sources targeting same destination
            dst_traffic = defaultdict(int)
            src_count = defaultdict(set)
            
            for packet in self.packets:
                dst_ip = packet.get('dst_ip')
                src_ip = packet.get('src_ip')
                if dst_ip:
                    dst_traffic[dst_ip] += 1
                    if src_ip:
                        src_count[dst_ip].add(src_ip)
            
            for dst_ip, count in dst_traffic.items():
                sources = len(src_count.get(dst_ip, set()))
                if count > 1000 and sources > 10:
                    threat = {
                        'timestamp': datetime.now().isoformat(),
                        'type': ThreatType.DDOS.value,
                        'target_ip': dst_ip,
                        'severity': ThreatSeverity.CRITICAL.name,
                        'confidence': 0.95,
                        'details': f'Possible DDoS: {count} packets from {sources} sources',
                        'affected_ips': [dst_ip]
                    }
                    self.threats.append(threat)
                    logger.critical(f"DDoS detected targeting {dst_ip}")
    
    def _detect_data_exfiltration(self, analysis: Dict) -> None:
        """Detect data exfiltration attempts"""
        packet_size_stats = analysis.get('packet_size_stats', {})
        avg_size = packet_size_stats.get('avg', 0)
        
        # Look for unusually large outgoing traffic
        src_outgoing = defaultdict(int)
        for packet in self.packets:
            src_ip = packet.get('src_ip')
            size = packet.get('size', 0)
            if src_ip:
                src_outgoing[src_ip] += size
        
        for src_ip, total_size in src_outgoing.items():
            if total_size > 10 * 1024 * 1024:  # 10MB threshold
                threat = {
                    'timestamp': datetime.now().isoformat(),
                    'type': ThreatType.DATA_EXFILTRATION.value,
                    'source_ip': src_ip,
                    'severity': ThreatSeverity.HIGH.name,
                    'confidence': 0.8,
                    'details': f'Possible data exfiltration: {total_size / 1024 / 1024:.2f} MB transferred',
                    'affected_ips': [src_ip]
                }
                self.threats.append(threat)
                logger.warning(f"Data exfiltration detected from {src_ip}")
    
    def _detect_unauthorized_access(self) -> None:
        """Detect unauthorized access attempts"""
        # Check for access to restricted ports without proper protocol
        restricted_ports = {
            22: 'SSH',
            3389: 'RDP',
            445: 'SMB',
            3306: 'MySQL',
            5432: 'PostgreSQL'
        }
        
        port_protocol = defaultdict(lambda: defaultdict(int))
        for packet in self.packets:
            dst_port = packet.get('dst_port')
            protocol = packet.get('protocol')
            src_ip = packet.get('src_ip')
            
            if dst_port in restricted_ports:
                port_protocol[dst_port][protocol] += 1
        
        for port, protocols in port_protocol.items():
            if len(protocols) > 1 or protocols.get('ICMP', 0) > 0:
                threat = {
                    'timestamp': datetime.now().isoformat(),
                    'type': ThreatType.UNAUTHORIZED_ACCESS.value,
                    'target_port': port,
                    'severity': ThreatSeverity.MEDIUM.name,
                    'confidence': 0.7,
                    'details': f'Unusual protocol on restricted port {port}',
                    'affected_ips': []
                }
                self.threats.append(threat)
                logger.warning(f"Unauthorized access attempt on port {port}")
    
    def _detect_suspicious_protocols(self) -> None:
        """Detect suspicious protocol usage"""
        # Check for unusual protocol usage
        protocol_usage = defaultdict(int)
        for packet in self.packets:
            protocol = packet.get('protocol', 'Unknown')
            protocol_usage[protocol] += 1
        
        suspicious = ['ICMP']  # ICMP can be used for tunneling
        for protocol in suspicious:
            if protocol_usage.get(protocol, 0) > 100:
                threat = {
                    'timestamp': datetime.now().isoformat(),
                    'type': ThreatType.SUSPICIOUS_PROTOCOL.value,
                    'protocol': protocol,
                    'severity': ThreatSeverity.LOW.name,
                    'confidence': 0.6,
                    'details': f'Suspicious {protocol} usage detected',
                    'affected_ips': []
                }
                self.threats.append(threat)
                logger.info(f"Suspicious protocol usage: {protocol}")
    
    def _detect_anomalous_behavior(self, analysis: Dict) -> None:
        """Detect anomalous network behavior"""
        anomalies = analysis.get('traffic_anomalies', [])
        
        for anomaly in anomalies:
            threat = {
                'timestamp': datetime.now().isoformat(),
                'type': ThreatType.ANOMALOUS_BEHAVIOR.value,
                'severity': ThreatSeverity.MEDIUM.name,
                'confidence': 0.65,
                'details': anomaly,
                'affected_ips': []
            }
            self.threats.append(threat)
            logger.warning(f"Anomaly detected: {anomaly}")
    
    def get_threats(self) -> List[Dict]:
        """Return detected threats"""
        return self.threats
    
    def get_threats_by_severity(self, severity: str) -> List[Dict]:
        """Get threats filtered by severity"""
        return [t for t in self.threats if t['severity'] == severity]
