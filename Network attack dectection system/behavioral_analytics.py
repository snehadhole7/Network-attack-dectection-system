"""
Advanced Analytics Module
Behavioral analysis and anomaly detection
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class BehavioralAnalytics:
    """User and Entity Behavior Analytics (UEBA)"""
    
    def __init__(self):
        self.user_profiles = defaultdict(dict)
        self.entity_profiles = defaultdict(dict)
        self.baseline_data = {}
        self.anomalies = []
    
    def establish_baseline(self, packets: List[Dict], window_days: int = 7) -> Dict:
        """Establish baseline behavior"""
        baseline = {
            'avg_packet_size': 0,
            'avg_packets_per_ip': 0,
            'common_ports': [],
            'common_protocols': [],
            'peak_hours': [],
            'established_at': datetime.now().isoformat()
        }
        
        if not packets:
            return baseline
        
        sizes = [p.get('size', 0) for p in packets]
        baseline['avg_packet_size'] = statistics.mean(sizes) if sizes else 0
        
        ip_counts = defaultdict(int)
        for packet in packets:
            ip_counts[packet.get('src_ip')] += 1
        
        if ip_counts:
            baseline['avg_packets_per_ip'] = statistics.mean(ip_counts.values())
        
        # Extract common ports
        ports = [p.get('dst_port') for p in packets if p.get('dst_port')]
        if ports:
            port_counts = defaultdict(int)
            for port in ports:
                port_counts[port] += 1
            baseline['common_ports'] = sorted(
                port_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        
        # Extract common protocols
        protocols = [p.get('protocol') for p in packets]
        if protocols:
            proto_counts = defaultdict(int)
            for proto in protocols:
                proto_counts[proto] += 1
            baseline['common_protocols'] = sorted(
                proto_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
        
        self.baseline_data = baseline
        logger.info("Baseline established")
        return baseline
    
    def detect_behavioral_anomalies(self, packets: List[Dict]) -> List[Dict]:
        """Detect behavioral anomalies"""
        anomalies = []
        
        if not self.baseline_data or not packets:
            return anomalies
        
        baseline = self.baseline_data
        
        # Check for unusual packet sizes
        sizes = [p.get('size', 0) for p in packets]
        if sizes:
            avg_size = statistics.mean(sizes)
            expected_avg = baseline['avg_packet_size']
            
            if expected_avg > 0 and abs(avg_size - expected_avg) > expected_avg * 2:
                anomalies.append({
                    'type': 'Unusual Packet Sizes',
                    'severity': 'MEDIUM',
                    'description': f'Average packet size ({avg_size:.0f}) deviates significantly from baseline ({expected_avg:.0f})',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Check for unusual port access
        for packet in packets:
            dst_port = packet.get('dst_port')
            if dst_port:
                common_ports = [p[0] for p in baseline.get('common_ports', [])]
                if dst_port not in common_ports and dst_port not in [22, 80, 443, 53]:
                    anomalies.append({
                        'type': 'Unusual Port Access',
                        'severity': 'LOW',
                        'description': f'Access to uncommon port {dst_port}',
                        'timestamp': datetime.now().isoformat(),
                        'source_ip': packet.get('src_ip')
                    })
        
        # Check for protocol anomalies
        for packet in packets:
            protocol = packet.get('protocol')
            common_protocols = [p[0] for p in baseline.get('common_protocols', [])]
            if protocol not in common_protocols:
                anomalies.append({
                    'type': 'Unusual Protocol',
                    'severity': 'MEDIUM',
                    'description': f'Uncommon protocol detected: {protocol}',
                    'timestamp': datetime.now().isoformat()
                })
        
        self.anomalies = anomalies
        logger.info(f"Found {len(anomalies)} behavioral anomalies")
        return anomalies
    
    def get_traffic_profile(self, ip_address: str) -> Dict:
        """Get behavioral profile for an IP"""
        profile = {
            'ip_address': ip_address,
            'packets_sent': 0,
            'bytes_sent': 0,
            'common_destinations': [],
            'common_ports': [],
            'protocols_used': [],
            'risk_score': 0
        }
        
        return profile
    
    def calculate_risk_score(self, entity: str, behaviors: List[str]) -> float:
        """Calculate risk score based on behaviors"""
        risk_weights = {
            'port_scan': 0.8,
            'brute_force': 0.9,
            'data_exfiltration': 1.0,
            'unusual_protocol': 0.6,
            'high_traffic': 0.5
        }
        
        total_score = 0
        for behavior in behaviors:
            total_score += risk_weights.get(behavior, 0.3)
        
        # Normalize to 0-1
        return min(total_score / len(behaviors) if behaviors else 0, 1.0)
