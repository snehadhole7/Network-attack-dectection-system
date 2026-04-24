"""
Reporting Module
Generates reports and statistics about network security
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate security reports"""
    
    def __init__(self):
        self.incidents = []
        self.report_history = []
    
    def add_incident(self, incident: Dict) -> None:
        """Add an incident to the report"""
        incident['reported_at'] = datetime.now().isoformat()
        self.incidents.append(incident)
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily report"""
        today = datetime.now().date()
        today_incidents = [
            i for i in self.incidents
            if datetime.fromisoformat(i.get('timestamp', datetime.now().isoformat())).date() == today
        ]
        
        report = {
            'report_type': 'Daily Report',
            'date': today.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary(today_incidents),
            'incident_breakdown': self._breakdown_incidents(today_incidents),
            'severity_distribution': self._severity_distribution(today_incidents),
            'top_threats': self._get_top_threats(today_incidents, 5),
            'top_source_ips': self._get_top_source_ips(today_incidents, 10),
            'recommendations': self._generate_recommendations(today_incidents)
        }
        
        self.report_history.append(report)
        return report
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly report"""
        week_ago = datetime.now() - timedelta(days=7)
        week_incidents = [
            i for i in self.incidents
            if datetime.fromisoformat(i.get('timestamp', datetime.now().isoformat())) > week_ago
        ]
        
        report = {
            'report_type': 'Weekly Report',
            'period': f"{(week_ago).date()} to {datetime.now().date()}",
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary(week_incidents),
            'incident_breakdown': self._breakdown_incidents(week_incidents),
            'severity_distribution': self._severity_distribution(week_incidents),
            'top_threats': self._get_top_threats(week_incidents, 10),
            'top_source_ips': self._get_top_source_ips(week_incidents, 20),
            'trend_analysis': self._analyze_trends(week_incidents),
            'recommendations': self._generate_recommendations(week_incidents)
        }
        
        self.report_history.append(report)
        return report
    
    def generate_monthly_report(self) -> Dict[str, Any]:
        """Generate monthly report"""
        month_ago = datetime.now() - timedelta(days=30)
        month_incidents = [
            i for i in self.incidents
            if datetime.fromisoformat(i.get('timestamp', datetime.now().isoformat())) > month_ago
        ]
        
        report = {
            'report_type': 'Monthly Report',
            'period': f"Last 30 days",
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary(month_incidents),
            'incident_breakdown': self._breakdown_incidents(month_incidents),
            'severity_distribution': self._severity_distribution(month_incidents),
            'top_threats': self._get_top_threats(month_incidents, 15),
            'top_source_ips': self._get_top_source_ips(month_incidents, 30),
            'trend_analysis': self._analyze_trends(month_incidents),
            'recommendations': self._generate_recommendations(month_incidents),
            'compliance_notes': self._generate_compliance_notes(month_incidents)
        }
        
        self.report_history.append(report)
        return report
    
    def _generate_summary(self, incidents: List[Dict]) -> Dict[str, Any]:
        """Generate incident summary"""
        return {
            'total_incidents': len(incidents),
            'critical_incidents': sum(1 for i in incidents if i.get('severity') == 'CRITICAL'),
            'high_incidents': sum(1 for i in incidents if i.get('severity') == 'HIGH'),
            'medium_incidents': sum(1 for i in incidents if i.get('severity') == 'MEDIUM'),
            'low_incidents': sum(1 for i in incidents if i.get('severity') == 'LOW'),
            'blocked_ips': len(set(i.get('source_ip') for i in incidents if i.get('source_ip')))
        }
    
    def _breakdown_incidents(self, incidents: List[Dict]) -> Dict[str, int]:
        """Breakdown incidents by type"""
        breakdown = defaultdict(int)
        for incident in incidents:
            incident_type = incident.get('type', 'Unknown')
            breakdown[incident_type] += 1
        return dict(breakdown)
    
    def _severity_distribution(self, incidents: List[Dict]) -> Dict[str, int]:
        """Distribution of incidents by severity"""
        distribution = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for incident in incidents:
            severity = incident.get('severity', 'UNKNOWN')
            if severity in distribution:
                distribution[severity] += 1
        
        return distribution
    
    def _get_top_threats(self, incidents: List[Dict], limit: int = 10) -> List[tuple]:
        """Get top threat types"""
        threat_count = defaultdict(int)
        for incident in incidents:
            threat_type = incident.get('type', 'Unknown')
            threat_count[threat_type] += 1
        
        sorted_threats = sorted(threat_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_threats[:limit]
    
    def _get_top_source_ips(self, incidents: List[Dict], limit: int = 10) -> List[tuple]:
        """Get top source IPs"""
        ip_count = defaultdict(int)
        for incident in incidents:
            source_ip = incident.get('source_ip', 'Unknown')
            if source_ip and source_ip != 'Unknown':
                ip_count[source_ip] += 1
        
        sorted_ips = sorted(ip_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_ips[:limit]
    
    def _analyze_trends(self, incidents: List[Dict]) -> Dict[str, Any]:
        """Analyze incident trends"""
        if not incidents:
            return {
                'trend': 'No incidents',
                'increase_percent': 0,
                'most_common_time': 'N/A'
            }
        
        # Group by hour
        hourly_count = defaultdict(int)
        for incident in incidents:
            timestamp = datetime.fromisoformat(incident.get('timestamp', datetime.now().isoformat()))
            hour = timestamp.strftime('%H:00')
            hourly_count[hour] += 1
        
        peak_hour = max(hourly_count, key=hourly_count.get) if hourly_count else 'N/A'
        
        return {
            'trend': 'stable' if len(incidents) < 100 else 'increasing',
            'incidents_per_hour': dict(hourly_count),
            'peak_hour': peak_hour,
            'average_per_hour': len(incidents) / 24 if incidents else 0
        }
    
    def _generate_recommendations(self, incidents: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if not incidents:
            return ['Continue regular security monitoring']
        
        incident_types = set(i.get('type') for i in incidents)
        
        if 'Port Scan' in incident_types:
            recommendations.append('Implement port scanning detection and automatic IP blocking')
        
        if 'Brute Force' in incident_types:
            recommendations.append('Implement account lockout policies and multi-factor authentication')
        
        if 'DDoS' in incident_types:
            recommendations.append('Deploy DDoS protection mechanisms and traffic filtering')
        
        if 'Data Exfiltration' in incident_types:
            recommendations.append('Review and enhance data loss prevention (DLP) policies')
        
        critical_count = sum(1 for i in incidents if i.get('severity') == 'CRITICAL')
        if critical_count > 5:
            recommendations.append('Conduct comprehensive security audit immediately')
        
        if not recommendations:
            recommendations.append('Maintain current security measures and continue monitoring')
        
        return recommendations
    
    def _generate_compliance_notes(self, incidents: List[Dict]) -> List[str]:
        """Generate compliance-related notes"""
        notes = []
        
        total = len(incidents)
        critical = sum(1 for i in incidents if i.get('severity') == 'CRITICAL')
        
        if critical > 0:
            notes.append(f"Critical incidents detected: {critical}. Incident response procedures should be followed.")
        
        notes.append(f"Total security incidents this month: {total}")
        notes.append("All incidents should be documented for compliance records.")
        notes.append("Review security policies and update if necessary.")
        
        return notes
    
    def get_report_history(self) -> List[Dict]:
        """Get report history"""
        return self.report_history
    
    def export_report_as_json(self, report: Dict) -> str:
        """Export report as JSON"""
        import json
        return json.dumps(report, indent=2, default=str)
    
    def export_report_as_html(self, report: Dict) -> str:
        """Export report as HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report['report_type']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .critical {{ color: red; }}
                .high {{ color: orange; }}
                .medium {{ color: #FFB300; }}
            </style>
        </head>
        <body>
            <h1>{report['report_type']}</h1>
            <p>Generated: {report['generated_at']}</p>
            
            <h2>Summary</h2>
            <ul>
            """
        
        for key, value in report['summary'].items():
            html += f"<li>{key}: {value}</li>"
        
        html += """
            </ul>
            
            <h2>Recommendations</h2>
            <ul>
            """
        
        for rec in report['recommendations']:
            html += f"<li>{rec}</li>"
        
        html += """
            </ul>
        </body>
        </html>
        """
        return html
