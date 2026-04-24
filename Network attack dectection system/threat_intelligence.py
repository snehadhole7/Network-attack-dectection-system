"""
Advanced Threat Intelligence Module
Threat intelligence feeds and correlation
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ThreatIntelligence:
    """Advanced threat intelligence and correlation engine"""
    
    def __init__(self):
        self.threat_feeds = {
            'mitre': self._load_mitre_attack_framework(),
            'owasp': self._load_owasp_top10(),
            'cve': self._load_cve_database(),
            'internal': []
        }
        self.threat_correlations = []
        self.indicators_of_compromise = []
    
    def _load_mitre_attack_framework(self) -> Dict:
        """Load MITRE ATT&CK Framework tactics"""
        return {
            'reconnaissance': ['Active Scanning', 'Gather Victim Org Info'],
            'resource_development': ['Acquire Infrastructure', 'Develop Capabilities'],
            'initial_access': ['Phishing', 'Exploit Public-Facing Application'],
            'execution': ['Command and Scripting Interpreter', 'User Execution'],
            'persistence': ['Account Manipulation', 'Establish Accounts'],
            'privilege_escalation': ['Abuse Elevation Control Mechanism', 'Valid Accounts'],
            'defense_evasion': ['Obfuscated Files', 'Masquerading'],
            'credential_access': ['Brute Force', 'Credential Dumping'],
            'discovery': ['Account Discovery', 'System Network Configuration Discovery'],
            'lateral_movement': ['Lateral Tool Transfer', 'Remote Services'],
            'collection': ['Data from Local System', 'Screen Capture'],
            'command_control': ['Application Layer Protocol', 'Encrypted Channel'],
            'exfiltration': ['Exfiltration Over Web Service', 'Data Transfer Size Limits'],
            'impact': ['Data Destruction', 'Service Degradation']
        }
    
    def _load_owasp_top10(self) -> List[str]:
        """Load OWASP Top 10 Web Application Security Risks"""
        return [
            'Broken Access Control',
            'Cryptographic Failures',
            'Injection',
            'Insecure Design',
            'Security Misconfiguration',
            'Vulnerable and Outdated Components',
            'Authentication Failures',
            'Software and Data Integrity Failures',
            'Logging and Monitoring Failures',
            'Server-Side Request Forgery'
        ]
    
    def _load_cve_database(self) -> List[Dict]:
        """Load sample CVE database"""
        return [
            {
                'cve_id': 'CVE-2024-0001',
                'severity': 'CRITICAL',
                'description': 'Remote Code Execution vulnerability',
                'affected_software': ['Apache', 'Nginx'],
                'cvss_score': 9.8,
                'published': '2024-01-01'
            },
            {
                'cve_id': 'CVE-2024-0002',
                'severity': 'HIGH',
                'description': 'SQL Injection vulnerability',
                'affected_software': ['PHP', 'Node.js'],
                'cvss_score': 8.2,
                'published': '2024-01-15'
            }
        ]
    
    def correlate_threats(self, incidents: List[Dict]) -> List[Dict]:
        """Correlate multiple incidents to identify attack campaigns"""
        correlations = []
        
        # Group incidents by source IP
        ip_groups = {}
        for incident in incidents:
            source = incident.get('source_ip', 'Unknown')
            if source not in ip_groups:
                ip_groups[source] = []
            ip_groups[source].append(incident)
        
        # Detect correlation patterns
        for source_ip, incidents_list in ip_groups.items():
            if len(incidents_list) > 3:
                # Multiple incidents from same source suggest coordinated attack
                correlation = {
                    'correlation_id': f"corr_{len(self.threat_correlations)}",
                    'type': 'Multi-stage Attack',
                    'source_ip': source_ip,
                    'incident_count': len(incidents_list),
                    'threat_level': 'CRITICAL' if len(incidents_list) > 5 else 'HIGH',
                    'stages': self._identify_attack_stages(incidents_list),
                    'mitre_ttps': self._map_to_mitre(incidents_list),
                    'detected_at': datetime.now().isoformat()
                }
                correlations.append(correlation)
        
        self.threat_correlations = correlations
        logger.info(f"Identified {len(correlations)} threat correlations")
        return correlations
    
    def _identify_attack_stages(self, incidents: List[Dict]) -> List[str]:
        """Identify attack stages in incident sequence"""
        stages = []
        
        incident_types = [i.get('type', '') for i in incidents]
        
        # Reconnaissance
        if any('Scan' in t for t in incident_types):
            stages.append('Reconnaissance')
        
        # Access
        if any('Brute' in t or 'Unauthorized' in t for t in incident_types):
            stages.append('Initial Access / Credential Access')
        
        # Persistence
        if any('Persistence' in t or len(incidents) > 5 for t in incident_types):
            stages.append('Persistence')
        
        # Exfiltration
        if any('Exfiltration' in t or 'Data' in t for t in incident_types):
            stages.append('Exfiltration')
        
        return stages if stages else ['Unknown']
    
    def _map_to_mitre(self, incidents: List[Dict]) -> List[str]:
        """Map detected incidents to MITRE ATT&CK framework"""
        techniques = []
        
        for incident in incidents:
            incident_type = incident.get('type', '')
            
            if 'Port Scan' in incident_type:
                techniques.append('T1595: Active Scanning')
            elif 'Brute' in incident_type:
                techniques.append('T1110: Brute Force')
            elif 'DDoS' in incident_type:
                techniques.append('T1561: Disk Wipe')
            elif 'Unauthorized' in incident_type:
                techniques.append('T1586: Account Compromise')
            elif 'Exfiltration' in incident_type:
                techniques.append('T1041: Exfiltration Over C2 Channel')
            elif 'Malware' in incident_type:
                techniques.append('T1566: Phishing')
        
        return list(set(techniques))
    
    def add_ioc(self, ioc_type: str, value: str, confidence: float = 0.8, source: str = 'internal') -> str:
        """Add Indicator of Compromise"""
        ioc = {
            'ioc_id': f"ioc_{len(self.indicators_of_compromise)}",
            'type': ioc_type,  # IP, Domain, Hash, URL, etc.
            'value': value,
            'confidence': confidence,
            'source': source,
            'added_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.indicators_of_compromise.append(ioc)
        logger.info(f"IOC added: {ioc_type} - {value}")
        
        return ioc['ioc_id']
    
    def check_ioc(self, ioc_type: str, value: str) -> Dict:
        """Check if value matches known IOCs"""
        matches = []
        
        for ioc in self.indicators_of_compromise:
            if ioc['type'] == ioc_type and ioc['value'] == value and ioc['status'] == 'active':
                matches.append(ioc)
        
        if matches:
            return {
                'matched': True,
                'count': len(matches),
                'iocs': matches,
                'risk_level': 'CRITICAL'
            }
        
        return {
            'matched': False,
            'count': 0,
            'risk_level': 'LOW'
        }
    
    def get_threat_intelligence_summary(self) -> Dict:
        """Get summary of threat intelligence data"""
        return {
            'total_iocs': len(self.indicators_of_compromise),
            'active_iocs': sum(1 for ioc in self.indicators_of_compromise if ioc['status'] == 'active'),
            'total_correlations': len(self.threat_correlations),
            'critical_correlations': sum(1 for c in self.threat_correlations if c.get('threat_level') == 'CRITICAL'),
            'mitre_techniques': list(set([
                tech for corr in self.threat_correlations 
                for tech in corr.get('mitre_ttps', [])
            ])),
            'threat_feeds_loaded': list(self.threat_feeds.keys()),
            'last_update': datetime.now().isoformat()
        }
    
    def get_threat_landscape_report(self) -> Dict:
        """Generate threat landscape report"""
        return {
            'report_type': 'Threat Landscape',
            'generated_at': datetime.now().isoformat(),
            'top_attack_vectors': [
                {'method': 'Brute Force', 'incidents': 15, 'trend': 'increasing'},
                {'method': 'Port Scanning', 'incidents': 12, 'trend': 'stable'},
                {'method': 'Malware', 'incidents': 8, 'trend': 'increasing'},
                {'method': 'DDoS', 'incidents': 5, 'trend': 'decreasing'},
                {'method': 'Data Exfiltration', 'incidents': 3, 'trend': 'stable'}
            ],
            'emerging_threats': [
                'ML-based evasion attacks',
                'Supply chain compromises',
                'Zero-day exploits',
                'Ransomware-as-a-Service'
            ],
            'attack_patterns': self.threat_correlations[:5],
            'recommendations': [
                'Implement behavioral analytics',
                'Enhance endpoint detection',
                'Improve threat intelligence feeds',
                'Conduct red team exercises',
                'Implement zero-trust architecture'
            ]
        }
