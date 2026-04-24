"""
Real-time Updates Module
WebSocket-based real-time communication for dashboard
"""

import logging
from typing import Dict, List, Any, Callable
from datetime import datetime
from queue import Queue
import json

logger = logging.getLogger(__name__)

# Try to import flask-socketio, if not available provide fallback
try:
    from flask_socketio import SocketIO, emit, send
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    logger.warning("flask-socketio not available, falling back to polling")

class RealtimeUpdater:
    """Manage real-time updates via WebSocket"""
    
    def __init__(self):
        self.socketio = None
        self.update_queue = Queue()
        self.connected_clients = set()
        self.subscribers = {}  # Event type -> callback list
        self.polling_data = {
            'latest_threat': None,
            'latest_incident': None,
            'stats': {},
            'alerts': []
        }
    
    def initialize_socketio(self, app):
        """Initialize SocketIO with Flask app"""
        if SOCKETIO_AVAILABLE:
            self.socketio = SocketIO(app, cors_allowed_origins="*")
            self._register_socketio_handlers()
            logger.info("WebSocket support initialized")
            return True
        else:
            logger.warning("WebSocket not available, using polling fallback")
            return False
    
    def _register_socketio_handlers(self):
        """Register WebSocket event handlers"""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        def handle_connect():
            client_id = f"client_{len(self.connected_clients)}"
            self.connected_clients.add(client_id)
            logger.info(f"Client connected: {client_id}")
            emit('connection_response', {'data': 'Connected to NADS'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Client disconnected")
        
        @self.socketio.on('subscribe')
        def handle_subscribe(data):
            event_type = data.get('event_type', 'all')
            logger.info(f"Client subscribed to: {event_type}")
        
        @self.socketio.on('request_update')
        def handle_request_update(data):
            # Send immediate update
            emit('update', self.polling_data)
    
    def broadcast_threat(self, threat: Dict):
        """Broadcast threat detection to all connected clients"""
        self.polling_data['latest_threat'] = threat
        
        if self.socketio and SOCKETIO_AVAILABLE:
            try:
                self.socketio.emit('threat_detected', threat, broadcast=True)
                logger.info(f"Threat broadcast: {threat.get('type')}")
            except Exception as e:
                logger.error(f"Error broadcasting threat: {str(e)}")
        
        # Also queue for polling clients
        self.update_queue.put({'type': 'threat', 'data': threat})
    
    def broadcast_incident(self, incident: Dict):
        """Broadcast incident to all connected clients"""
        self.polling_data['latest_incident'] = incident
        
        if self.socketio and SOCKETIO_AVAILABLE:
            try:
                self.socketio.emit('incident_detected', incident, broadcast=True)
                logger.info(f"Incident broadcast: {incident.get('id')}")
            except Exception as e:
                logger.error(f"Error broadcasting incident: {str(e)}")
        
        self.update_queue.put({'type': 'incident', 'data': incident})
    
    def broadcast_alert(self, alert: Dict):
        """Broadcast alert to all connected clients"""
        if len(self.polling_data['alerts']) > 100:
            self.polling_data['alerts'] = self.polling_data['alerts'][-100:]
        
        self.polling_data['alerts'].append(alert)
        
        if self.socketio and SOCKETIO_AVAILABLE:
            try:
                self.socketio.emit('alert', alert, broadcast=True)
                logger.info(f"Alert broadcast: {alert.get('message')}")
            except Exception as e:
                logger.error(f"Error broadcasting alert: {str(e)}")
        
        self.update_queue.put({'type': 'alert', 'data': alert})
    
    def broadcast_stats(self, stats: Dict):
        """Broadcast statistics update"""
        self.polling_data['stats'] = stats
        
        if self.socketio and SOCKETIO_AVAILABLE:
            try:
                self.socketio.emit('stats_update', stats, broadcast=True)
            except Exception as e:
                logger.error(f"Error broadcasting stats: {str(e)}")
        
        self.update_queue.put({'type': 'stats', 'data': stats})
    
    def get_latest_updates(self, max_items: int = 10) -> Dict:
        """Get latest updates for polling clients"""
        updates = []
        
        while not self.update_queue.empty() and len(updates) < max_items:
            try:
                update = self.update_queue.get_nowait()
                updates.append(update)
            except:
                break
        
        return {
            'updates': updates,
            'latest_threat': self.polling_data.get('latest_threat'),
            'latest_incident': self.polling_data.get('latest_incident'),
            'stats': self.polling_data.get('stats'),
            'timestamp': datetime.now().isoformat()
        }
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscription added for: {event_type}")
    
    def notify_subscribers(self, event_type: str, data: Dict):
        """Notify all subscribers of an event"""
        callbacks = self.subscribers.get(event_type, [])
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error calling subscriber callback: {str(e)}")
    
    def get_connection_status(self) -> Dict:
        """Get WebSocket connection status"""
        return {
            'websocket_enabled': SOCKETIO_AVAILABLE and self.socketio is not None,
            'connected_clients': len(self.connected_clients),
            'queued_updates': self.update_queue.qsize(),
            'timestamp': datetime.now().isoformat()
        }
