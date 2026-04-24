"""
Traffic Analysis Module
Analyzes network traffic patterns and characteristics
"""

import logging
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)

class TrafficAnalyzer:
    """Analyze network traffic"""
    
    def __init__(self):
        self.packets = []
        self.analysis_results = {}
    
    def load_packets(self, packets: List[Dict]) -> None:
        """Load preprocessed packets"""
        self.packets = packets
    
    def analyze_traffic(self, packets: List[Dict]) -> Dict[str, Any]:
        """Perform complete traffic analysis"""
        self.load_packets(packets)
        
        analysis = {
            'total_packets': len(packets),
            'unique_sources': self._count_unique_ips('src_ip'),
            'unique_destinations': self._count_unique_ips('dst_ip'),
            'protocol_distribution': self._analyze_protocols(),
            'port_statistics': self._analyze_ports(),
            'traffic_rate': self._calculate_traffic_rate(),
            'packet_size_stats': self._analyze_packet_sizes(),
            'top_source_ips': self._get_top_ips('src_ip', 10),
            'top_dest_ips': self._get_top_ips('dst_ip', 10),
            'suspicious_ports': self._identify_suspicious_ports(),
            'traffic_anomalies': self._detect_anomalies()
        }
        
        self.analysis_results = analysis
        logger.info("Traffic analysis complete")
        return analysis
    
    def _count_unique_ips(self, ip_type: str) -> int:
        """Count unique IPs"""
        ips = set(packet.get(ip_type) for packet in self.packets if packet.get(ip_type))
        return len(ips)
    
    def _analyze_protocols(self) -> Dict[str, int]:
        """Analyze protocol distribution"""
        protocol_count = defaultdict(int)
        for packet in self.packets:
            protocol = packet.get('protocol', 'Unknown')
            protocol_count[protocol] += 1
        return dict(protocol_count)
    
    def _analyze_ports(self) -> Dict[str, Any]:
        """Analyze port statistics"""
        src_ports = defaultdict(int)
        dst_ports = defaultdict(int)
        
        for packet in self.packets:
            if packet.get('src_port'):
                src_ports[packet['src_port']] += 1
            if packet.get('dst_port'):
                dst_ports[packet['dst_port']] += 1
        
        return {
            'source_ports': dict(src_ports),
            'destination_ports': dict(dst_ports),
            'total_unique_src_ports': len(src_ports),
            'total_unique_dst_ports': len(dst_ports)
        }
    
    def _calculate_traffic_rate(self) -> Dict[str, Any]:
        """Calculate traffic rate"""
        if not self.packets:
            return {'packets_per_second': 0, 'bytes_per_second': 0}
        
        total_bytes = sum(packet.get('size', 0) for packet in self.packets)
        packet_count = len(self.packets)
        
        return {
            'total_bytes': total_bytes,
            'total_packets': packet_count,
            'packets_per_second': packet_count / max(1, len(set(p.get('timestamp') for p in self.packets)))
        }
    
    def _analyze_packet_sizes(self) -> Dict[str, float]:
        """Analyze packet size statistics"""
        if not self.packets:
            return {'min': 0, 'max': 0, 'avg': 0}
        
        sizes = [packet.get('size', 0) for packet in self.packets]
        return {
            'min': min(sizes),
            'max': max(sizes),
            'avg': sum(sizes) / len(sizes),
            'total': sum(sizes)
        }
    
    def _get_top_ips(self, ip_type: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get top IPs by frequency"""
        ip_count = defaultdict(int)
        for packet in self.packets:
            ip = packet.get(ip_type)
            if ip:
                ip_count[ip] += 1
        
        sorted_ips = sorted(ip_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_ips[:top_n]
    
    def _identify_suspicious_ports(self) -> List[int]:
        """Identify suspicious port activity"""
        suspicious = [
            23,    # Telnet
            21,    # FTP
            445,   # SMB
            139,   # NetBIOS
            135,   # RPC
            3389,  # RDP
            3306,  # MySQL
            5432,  # PostgreSQL
            27017, # MongoDB
            6379,  # Redis
        ]
        
        dst_ports = set()
        for packet in self.packets:
            if packet.get('dst_port'):
                dst_ports.add(packet['dst_port'])
        
        found_suspicious = [port for port in suspicious if port in dst_ports]
        return found_suspicious
    
    def _detect_anomalies(self) -> List[str]:
        """Detect traffic anomalies"""
        anomalies = []
        
        # Check for port scanning
        unique_dst_ports = len(set(p.get('dst_port') for p in self.packets if p.get('dst_port')))
        if unique_dst_ports > 50:
            anomalies.append('Possible port scanning detected (many unique destination ports)')
        
        # Check for unusual packet sizes
        sizes = [p.get('size', 0) for p in self.packets]
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            large_packets = sum(1 for s in sizes if s > avg_size * 10)
            if large_packets > len(sizes) * 0.1:
                anomalies.append('Unusual packet sizes detected')
        
        # Check for high traffic from single source
        src_ip_count = defaultdict(int)
        for packet in self.packets:
            if packet.get('src_ip'):
                src_ip_count[packet['src_ip']] += 1
        
        if src_ip_count and max(src_ip_count.values()) > len(self.packets) * 0.3:
            anomalies.append('High traffic concentration from single source')
        
        return anomalies
    
    def get_results(self) -> Dict[str, Any]:
        """Return analysis results"""
        return self.analysis_results
