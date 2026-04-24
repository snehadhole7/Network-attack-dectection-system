"""
Main Flask Application
Network Attack Detection System with Advanced Features
"""

import logging
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from config import Config
from data_preprocessor import DataPreprocessor
from traffic_analyzer import TrafficAnalyzer
from threat_detector import ThreatDetector
from response_system import ResponseSystem
from alert_system import AlertSystem
from reporting import ReportGenerator
from database.db_setup import DatabaseSetup

# Advanced Feature Modules
try:
    from ml_threat_detector import MLThreatDetector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    MLThreatDetector = None

try:
    from auth_manager import AuthManager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    AuthManager = None

try:
    from behavioral_analytics import BehavioralAnalytics
    BEHAVIORAL_AVAILABLE = True
except ImportError:
    BEHAVIORAL_AVAILABLE = False
    BehavioralAnalytics = None

try:
    from incident_response import IncidentPlaybook
    INCIDENT_RESPONSE_AVAILABLE = True
except ImportError:
    INCIDENT_RESPONSE_AVAILABLE = False
    IncidentPlaybook = None

try:
    from blockchain_audit import BlockchainAuditTrail
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    BlockchainAuditTrail = None

try:
    from compliance_reporter import ComplianceReporter
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    ComplianceReporter = None

try:
    from threat_intelligence import ThreatIntelligence
    THREAT_INTEL_AVAILABLE = True
except ImportError:
    THREAT_INTEL_AVAILABLE = False
    ThreatIntelligence = None

try:
    from realtime_updates import RealtimeUpdater
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False
    RealtimeUpdater = None

# Optional modules
try:
    from network_capture import NetworkCapture
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    NetworkCapture = None

# Setup logging
os.makedirs(Config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOG_DIR, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'nads-secret-key-change-in-production'

# Initialize components
network_capture = None
data_preprocessor = DataPreprocessor()
traffic_analyzer = TrafficAnalyzer()
threat_detector = ThreatDetector()
response_system = ResponseSystem()
alert_system = AlertSystem()
report_generator = ReportGenerator()
db = None

# Initialize advanced feature modules
ml_detector = MLThreatDetector() if ML_AVAILABLE else None
auth_manager = AuthManager(app.config['SECRET_KEY']) if AUTH_AVAILABLE else None
behavioral_analytics = BehavioralAnalytics() if BEHAVIORAL_AVAILABLE else None
incident_playbook = IncidentPlaybook() if INCIDENT_RESPONSE_AVAILABLE else None
blockchain_audit = BlockchainAuditTrail() if BLOCKCHAIN_AVAILABLE else None
compliance_reporter = ComplianceReporter() if COMPLIANCE_AVAILABLE else None
threat_intelligence = ThreatIntelligence() if THREAT_INTEL_AVAILABLE else None
realtime_updater = RealtimeUpdater() if REALTIME_AVAILABLE else None

# Initialize WebSocket support if available
if REALTIME_AVAILABLE:
    try:
        realtime_updater.initialize_socketio(app)
    except Exception as e:
        logger.warning(f"WebSocket initialization failed: {str(e)}")

# System statistics
system_stats = {
    'uptime': datetime.now().isoformat(),
    'packets_processed': 0,
    'threats_detected': 0,
    'ips_blocked': 0,
    'features_enabled': {
        'ml_detection': ML_AVAILABLE,
        'behavioral_analysis': BEHAVIORAL_AVAILABLE,
        'incident_response': INCIDENT_RESPONSE_AVAILABLE,
        'blockchain_audit': BLOCKCHAIN_AVAILABLE,
        'compliance_reporting': COMPLIANCE_AVAILABLE,
        'threat_intelligence': THREAT_INTEL_AVAILABLE,
        'realtime_updates': REALTIME_AVAILABLE,
        'network_capture': SCAPY_AVAILABLE
    }
}

# Demo data for dashboard
def generate_demo_data():
    """Generate sample data for demonstration"""
    demo_packets = [
        {'src_ip': '192.168.1.100', 'dst_ip': '8.8.8.8', 'src_port': 54321, 'dst_port': 443, 'protocol': 'TCP', 'size': 1024, 'timestamp': datetime.now().isoformat()},
        {'src_ip': '192.168.1.101', 'dst_ip': '1.1.1.1', 'src_port': 53212, 'dst_port': 80, 'protocol': 'TCP', 'size': 2048, 'timestamp': datetime.now().isoformat()},
        {'src_ip': '192.168.1.102', 'dst_ip': '8.8.4.4', 'src_port': 52111, 'dst_port': 22, 'protocol': 'TCP', 'size': 512, 'timestamp': datetime.now().isoformat()},
        {'src_ip': '203.0.113.45', 'dst_ip': '192.168.1.50', 'src_port': 12345, 'dst_port': 3306, 'protocol': 'TCP', 'size': 256, 'timestamp': datetime.now().isoformat()},
        {'src_ip': '203.0.113.46', 'dst_ip': '192.168.1.50', 'src_port': 12346, 'dst_port': 3306, 'protocol': 'TCP', 'size': 256, 'timestamp': datetime.now().isoformat()},
    ]
    
    # Process through pipeline
    data_preprocessor.process(demo_packets)
    analysis = traffic_analyzer.analyze_traffic(data_preprocessor.get_processed_data())
    threats = threat_detector.detect_threats(data_preprocessor.get_processed_data(), analysis)
    
    # Add demo threats
    demo_threats = [
        {'timestamp': datetime.now().isoformat(), 'type': 'Brute Force', 'source_ip': '203.0.113.45', 'severity': 'HIGH', 'details': 'Multiple connection attempts to MySQL', 'confidence': 0.85, 'affected_ips': ['203.0.113.45']},
        {'timestamp': datetime.now().isoformat(), 'type': 'Port Scan', 'source_ip': '192.168.1.102', 'severity': 'MEDIUM', 'details': 'Possible port scanning detected', 'confidence': 0.72, 'affected_ips': ['192.168.1.102']},
    ]
    
    for threat in demo_threats:
        threat_detector.threats.append(threat)
        alert_system.send_alert(threat)
        response_system.execute_response(threat, Config.AUTO_RESPONSE_ENABLED)
    
    system_stats['threats_detected'] = len(threat_detector.get_threats())
    system_stats['packets_processed'] = len(data_preprocessor.get_processed_data())
    system_stats['ips_blocked'] = len(response_system.get_blocked_ips())

def initialize_system():
    """Initialize all system components"""
    global db
    try:
        # Initialize database
        db = DatabaseSetup(
            Config.MYSQL_HOST,
            Config.MYSQL_USER,
            Config.MYSQL_PASSWORD,
            Config.MYSQL_DB,
            Config.MYSQL_PORT
        )
        
        if db.connect():
            db.create_database()
            db.select_database()
            db.create_tables()
            logger.info("Database initialized successfully")
        else:
            logger.warning("Running in demo mode without database")
        
        # Generate demo data
        generate_demo_data()
        
        logger.info("System initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"System initialization warning: {str(e)}")
        logger.info("Running in demo mode")
        generate_demo_data()
        return True

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'uptime': system_stats['uptime'],
        'packets_processed': system_stats['packets_processed'],
        'threats_detected': system_stats['threats_detected'],
        'ips_blocked': system_stats['ips_blocked'],
        'blocked_ips': response_system.get_blocked_ips(),
        'response_count': len(response_system.get_response_log())
    })

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get recent incidents"""
    limit = request.args.get('limit', 100, type=int)
    if db:
        incidents = db.get_recent_incidents(limit)
        return jsonify({'incidents': incidents})
    return jsonify({'incidents': threat_detector.get_threats()})

@app.route('/api/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get incident details"""
    if db:
        incidents = db.get_recent_incidents(1000)
        for incident in incidents:
            if incident.get('id') == incident_id:
                return jsonify(incident)
    return jsonify({'error': 'Incident not found'}), 404

@app.route('/api/threats', methods=['GET'])
def get_threats():
    """Get detected threats"""
    severity = request.args.get('severity', None)
    if severity:
        threats = threat_detector.get_threats_by_severity(severity)
    else:
        threats = threat_detector.get_threats()
    return jsonify({'threats': threats, 'count': len(threats)})

@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """Get traffic analysis"""
    return jsonify(traffic_analyzer.get_results())

@app.route('/api/blocked-ips', methods=['GET'])
def get_blocked_ips():
    """Get blocked IPs"""
    return jsonify({
        'blocked_ips': response_system.get_blocked_ips(),
        'count': len(response_system.get_blocked_ips())
    })

@app.route('/api/blocked-ips/<ip>', methods=['DELETE'])
def unblock_ip(ip):
    """Unblock an IP"""
    result = response_system.unblock_ip(ip)
    return jsonify(result)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts"""
    limit = request.args.get('limit', 50, type=int)
    alerts = alert_system.get_alerts()[-limit:]
    return jsonify({'alerts': alerts, 'count': len(alerts)})

@app.route('/api/alerts/stats', methods=['GET'])
def get_alert_stats():
    """Get alert statistics"""
    return jsonify(alert_system.get_alert_stats())

@app.route('/api/reports/daily', methods=['GET'])
def get_daily_report():
    """Get daily report"""
    report = report_generator.generate_daily_report()
    return jsonify(report)

@app.route('/api/reports/weekly', methods=['GET'])
def get_weekly_report():
    """Get weekly report"""
    report = report_generator.generate_weekly_report()
    return jsonify(report)

@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    """Get monthly report"""
    report = report_generator.generate_monthly_report()
    return jsonify(report)

@app.route('/api/reports/export/<format_type>', methods=['POST'])
def export_report(format_type):
    """Export report in specified format"""
    report_type = request.json.get('report_type', 'daily')
    
    if report_type == 'daily':
        report = report_generator.generate_daily_report()
    elif report_type == 'weekly':
        report = report_generator.generate_weekly_report()
    else:
        report = report_generator.generate_monthly_report()
    
    if format_type == 'json':
        content = report_generator.export_report_as_json(report)
        return jsonify({'content': content})
    elif format_type == 'html':
        content = report_generator.export_report_as_html(report)
        return content, 200, {'Content-Type': 'text/html'}
    
    return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    return jsonify({
        'stats': system_stats,
        'threats_by_type': traffic_analyzer.get_results().get('protocol_distribution', {}),
        'top_source_ips': traffic_analyzer.get_results().get('top_source_ips', []),
        'suspicious_ports': traffic_analyzer.get_results().get('suspicious_ports', []),
        'blocked_ips_count': len(response_system.get_blocked_ips()),
        'alert_stats': alert_system.get_alert_stats(),
        'recent_alerts': alert_system.get_recent_alerts(60)[:10],
        'response_count': len(response_system.get_response_log())
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_status = 'disconnected'
    if db and db.connection:
        try:
            if hasattr(db.connection, 'is_connected'):
                db_status = 'connected' if db.connection.is_connected() else 'disconnected'
            else:
                db_status = 'connected'
        except:
            db_status = 'error'
    
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'version': '2.0.0',
        'features': system_stats['features_enabled']
    })

# ===== AUTHENTICATION ENDPOINTS =====
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    if not AUTH_AVAILABLE:
        return jsonify({'error': 'Authentication not available'}), 503
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    result = auth_manager.login(username, password)
    if result:
        token, user_info = result
        return jsonify({
            'token': token,
            'user': user_info,
            'message': 'Login successful'
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    if not AUTH_AVAILABLE:
        return jsonify({'error': 'Authentication not available'}), 503
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_manager.logout(token)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/user', methods=['GET'])
def get_current_user():
    """Get current user info"""
    if not AUTH_AVAILABLE:
        return jsonify({'error': 'Authentication not available'}), 503
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = auth_manager.verify_token(token)
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(user), 200

# ===== MACHINE LEARNING ENDPOINTS =====
@app.route('/api/ml/train', methods=['POST'])
def train_ml_model():
    """Train ML threat detection model"""
    if not ML_AVAILABLE:
        return jsonify({'error': 'ML module not available'}), 503
    
    packets = data_preprocessor.get_processed_data()
    success = ml_detector.train_model(packets)
    
    if success:
        ml_detector.save_model()
        return jsonify({'message': 'Model trained successfully'}), 200
    
    return jsonify({'error': 'Failed to train model'}), 400

@app.route('/api/ml/predict', methods=['POST'])
def predict_threats():
    """Predict threats using ML model"""
    if not ML_AVAILABLE:
        return jsonify({'error': 'ML module not available'}), 503
    
    packets = request.json.get('packets', data_preprocessor.get_processed_data())
    
    if ml_detector.trained:
        predictions = ml_detector.predict_threat(packets)
        return jsonify({'predictions': predictions}), 200
    
    return jsonify({'error': 'Model not trained'}), 400

@app.route('/api/ml/status', methods=['GET'])
def get_ml_status():
    """Get ML model status"""
    if not ML_AVAILABLE:
        return jsonify({'error': 'ML module not available'}), 503
    
    return jsonify({
        'trained': ml_detector.trained,
        'model_path': ml_detector.model_path
    }), 200

# ===== BEHAVIORAL ANALYTICS ENDPOINTS =====
@app.route('/api/behavioral/baseline', methods=['POST'])
def establish_baseline():
    """Establish behavioral baseline"""
    if not BEHAVIORAL_AVAILABLE:
        return jsonify({'error': 'Behavioral analytics not available'}), 503
    
    packets = data_preprocessor.get_processed_data()
    baseline = behavioral_analytics.establish_baseline(packets)
    
    return jsonify({
        'message': 'Baseline established',
        'baseline': baseline
    }), 200

@app.route('/api/behavioral/anomalies', methods=['GET'])
def detect_anomalies():
    """Detect behavioral anomalies"""
    if not BEHAVIORAL_AVAILABLE:
        return jsonify({'error': 'Behavioral analytics not available'}), 503
    
    packets = data_preprocessor.get_processed_data()
    anomalies = behavioral_analytics.detect_behavioral_anomalies(packets)
    
    return jsonify({
        'anomalies': anomalies,
        'count': len(anomalies)
    }), 200

@app.route('/api/behavioral/profile/<ip>', methods=['GET'])
def get_behavioral_profile(ip):
    """Get behavioral profile for an IP"""
    if not BEHAVIORAL_AVAILABLE:
        return jsonify({'error': 'Behavioral analytics not available'}), 503
    
    profile = behavioral_analytics.get_traffic_profile(ip)
    return jsonify(profile), 200

# ===== INCIDENT RESPONSE ENDPOINTS =====
@app.route('/api/incidents/playbook/<threat_type>', methods=['POST'])
def execute_playbook(threat_type):
    """Execute incident response playbook"""
    if not INCIDENT_RESPONSE_AVAILABLE:
        return jsonify({'error': 'Incident response not available'}), 503
    
    threat_data = request.json
    actions = incident_playbook.execute_playbook(threat_type, threat_data)
    
    return jsonify({
        'playbook': threat_type,
        'actions': actions,
        'status': 'executed'
    }), 200

@app.route('/api/incidents/playbooks', methods=['GET'])
def get_playbooks():
    """Get available playbooks"""
    if not INCIDENT_RESPONSE_AVAILABLE:
        return jsonify({'error': 'Incident response not available'}), 503
    
    return jsonify({
        'playbooks': list(incident_playbook.playbooks.keys()),
        'count': len(incident_playbook.playbooks)
    }), 200

@app.route('/api/incidents/history', methods=['GET'])
def get_playbook_history():
    """Get playbook execution history"""
    if not INCIDENT_RESPONSE_AVAILABLE:
        return jsonify({'error': 'Incident response not available'}), 503
    
    limit = request.args.get('limit', 50, type=int)
    history = incident_playbook.get_execution_history(limit)
    
    return jsonify({
        'history': history,
        'count': len(history)
    }), 200

# ===== BLOCKCHAIN AUDIT ENDPOINTS =====
@app.route('/api/audit/add', methods=['POST'])
def add_audit_event():
    """Add audit event to blockchain"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({'error': 'Blockchain audit not available'}), 503
    
    data = request.json
    event_type = data.get('event_type')
    details = data.get('details', {})
    severity = data.get('severity', 'INFO')
    
    tx_id = blockchain_audit.add_transaction(event_type, details, severity)
    
    return jsonify({
        'tx_id': tx_id,
        'message': 'Audit event added'
    }), 201

@app.route('/api/audit/mine', methods=['POST'])
def mine_audit_block():
    """Mine new audit block"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({'error': 'Blockchain audit not available'}), 503
    
    block = blockchain_audit.mine_block()
    
    if block:
        return jsonify({
            'block': block,
            'message': 'Block mined successfully'
        }), 201
    
    return jsonify({'error': 'No pending transactions'}), 400

@app.route('/api/audit/logs', methods=['GET'])
def get_audit_logs():
    """Get audit logs"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({'error': 'Blockchain audit not available'}), 503
    
    event_type = request.args.get('event_type', None)
    severity = request.args.get('severity', None)
    
    logs = blockchain_audit.get_audit_log(event_type, severity)
    
    return jsonify({
        'logs': logs,
        'count': len(logs)
    }), 200

@app.route('/api/audit/chain-stats', methods=['GET'])
def get_blockchain_stats():
    """Get blockchain statistics"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({'error': 'Blockchain audit not available'}), 503
    
    stats = blockchain_audit.get_chain_statistics()
    return jsonify(stats), 200

@app.route('/api/audit/validate', methods=['GET'])
def validate_blockchain():
    """Validate blockchain integrity"""
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({'error': 'Blockchain audit not available'}), 503
    
    is_valid = blockchain_audit.is_chain_valid()
    
    return jsonify({
        'valid': is_valid,
        'status': 'VALID' if is_valid else 'INVALID'
    }), 200

# ===== COMPLIANCE ENDPOINTS =====
@app.route('/api/compliance/<framework>', methods=['GET'])
def get_compliance_report(framework):
    """Get compliance report for framework"""
    if not COMPLIANCE_AVAILABLE:
        return jsonify({'error': 'Compliance reporting not available'}), 503
    
    incidents = threat_detector.get_threats()
    report = compliance_reporter.generate_compliance_report(framework, incidents)
    
    if report:
        return jsonify(report), 200
    
    return jsonify({'error': f'Unknown framework: {framework}'}), 400

@app.route('/api/compliance/frameworks', methods=['GET'])
def get_available_frameworks():
    """Get available compliance frameworks"""
    if not COMPLIANCE_AVAILABLE:
        return jsonify({'error': 'Compliance reporting not available'}), 503
    
    return jsonify({
        'frameworks': list(compliance_reporter.compliance_frameworks.keys()),
        'count': len(compliance_reporter.compliance_frameworks)
    }), 200

# ===== THREAT INTELLIGENCE ENDPOINTS =====
@app.route('/api/threat-intel/summary', methods=['GET'])
def get_threat_intel_summary():
    """Get threat intelligence summary"""
    if not THREAT_INTEL_AVAILABLE:
        return jsonify({'error': 'Threat intelligence not available'}), 503
    
    summary = threat_intelligence.get_threat_intelligence_summary()
    return jsonify(summary), 200

@app.route('/api/threat-intel/correlate', methods=['POST'])
def correlate_threats():
    """Correlate threats to identify attack campaigns"""
    if not THREAT_INTEL_AVAILABLE:
        return jsonify({'error': 'Threat intelligence not available'}), 503
    
    incidents = threat_detector.get_threats()
    correlations = threat_intelligence.correlate_threats(incidents)
    
    return jsonify({
        'correlations': correlations,
        'count': len(correlations)
    }), 200

@app.route('/api/threat-intel/ioc/add', methods=['POST'])
def add_ioc():
    """Add Indicator of Compromise"""
    if not THREAT_INTEL_AVAILABLE:
        return jsonify({'error': 'Threat intelligence not available'}), 503
    
    data = request.json
    ioc_type = data.get('type')
    value = data.get('value')
    confidence = data.get('confidence', 0.8)
    
    ioc_id = threat_intelligence.add_ioc(ioc_type, value, confidence)
    
    return jsonify({
        'ioc_id': ioc_id,
        'message': 'IOC added'
    }), 201

@app.route('/api/threat-intel/ioc/check', methods=['POST'])
def check_ioc():
    """Check if value matches known IOCs"""
    if not THREAT_INTEL_AVAILABLE:
        return jsonify({'error': 'Threat intelligence not available'}), 503
    
    data = request.json
    ioc_type = data.get('type')
    value = data.get('value')
    
    result = threat_intelligence.check_ioc(ioc_type, value)
    
    return jsonify(result), 200

@app.route('/api/threat-intel/landscape', methods=['GET'])
def get_threat_landscape():
    """Get threat landscape report"""
    if not THREAT_INTEL_AVAILABLE:
        return jsonify({'error': 'Threat intelligence not available'}), 503
    
    report = threat_intelligence.get_threat_landscape_report()
    return jsonify(report), 200

# ===== REAL-TIME UPDATES ENDPOINTS =====
@app.route('/api/realtime/status', methods=['GET'])
def get_realtime_status():
    """Get real-time connection status"""
    if not REALTIME_AVAILABLE:
        return jsonify({'websocket_enabled': False}), 200
    
    status = realtime_updater.get_connection_status()
    return jsonify(status), 200

@app.route('/api/realtime/updates', methods=['GET'])
def get_latest_updates():
    """Get latest updates for polling clients"""
    if not REALTIME_AVAILABLE:
        return jsonify({'error': 'Real-time updates not available'}), 503
    
    max_items = request.args.get('max', 10, type=int)
    updates = realtime_updater.get_latest_updates(max_items)
    
    return jsonify(updates), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Network Attack Detection System...")
    
    if initialize_system():
        logger.info("System ready, starting Flask server...")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=Config.DEBUG
        )
    else:
        logger.error("Failed to initialize system")
