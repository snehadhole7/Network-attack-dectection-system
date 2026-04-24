"""
Machine Learning Module
Advanced threat detection using ML models
"""

import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MLThreatDetector:
    """Machine Learning-based threat detection"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False
        self.model_path = 'models/threat_model.pkl'
        
    def extract_features(self, packets: List[Dict]) -> np.ndarray:
        """Extract ML features from packets"""
        features = []
        
        for packet in packets:
            feature_vector = [
                packet.get('size', 0),
                packet.get('src_port', 0),
                packet.get('dst_port', 0),
                1 if packet.get('protocol') == 'TCP' else 0,
                1 if packet.get('protocol') == 'UDP' else 0,
                1 if packet.get('protocol') == 'ICMP' else 0,
            ]
            features.append(feature_vector)
        
        return np.array(features) if features else np.array([]).reshape(0, 6)
    
    def train_model(self, packets: List[Dict]) -> bool:
        """Train ML model on packet data"""
        try:
            if len(packets) < 10:
                logger.warning("Not enough packets for training")
                return False
            
            X = self.extract_features(packets)
            
            if X.shape[0] == 0:
                return False
            
            # Train anomaly detector
            X_scaled = self.scaler.fit_transform(X)
            self.isolation_forest.fit(X_scaled)
            
            # Create synthetic labels for supervised learning
            y = self.isolation_forest.predict(X_scaled)
            y = (y == -1).astype(int)  # Convert anomaly predictions to binary labels
            
            # Train classifier
            if np.sum(y) > 0:  # Only if we have positive samples
                self.random_forest.fit(X_scaled, y)
            
            self.trained = True
            logger.info("ML model trained successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def predict_threat(self, packets: List[Dict]) -> List[Dict]:
        """Predict threats using ML"""
        if not self.trained or len(packets) == 0:
            return []
        
        try:
            X = self.extract_features(packets)
            if X.shape[0] == 0:
                return []
            
            X_scaled = self.scaler.transform(X)
            
            # Anomaly detection
            anomalies = self.isolation_forest.predict(X_scaled)
            
            # Threat scoring
            threat_scores = []
            for i, packet in enumerate(packets):
                if anomalies[i] == -1:  # Anomaly detected
                    # Get probability from random forest if trained
                    if self.trained and self.random_forest.n_classes_ > 0:
                        proba = self.random_forest.predict_proba(X_scaled[i:i+1])[0]
                        threat_score = proba[1] if len(proba) > 1 else 0.5
                    else:
                        threat_score = 0.75
                    
                    threat_scores.append({
                        'timestamp': packet.get('timestamp', datetime.now().isoformat()),
                        'type': 'ML Detected Anomaly',
                        'source_ip': packet.get('src_ip', 'Unknown'),
                        'destination_ip': packet.get('dst_ip', 'Unknown'),
                        'severity': self._get_severity_from_score(threat_score),
                        'ml_score': threat_score,
                        'confidence': threat_score,
                        'details': f'Anomalous network behavior detected (ML score: {threat_score:.2f})',
                        'affected_ips': [packet.get('src_ip', 'Unknown')]
                    })
            
            return threat_scores
        
        except Exception as e:
            logger.error(f"Error predicting threats: {str(e)}")
            return []
    
    def _get_severity_from_score(self, score: float) -> str:
        """Convert ML score to severity level"""
        if score >= 0.9:
            return 'CRITICAL'
        elif score >= 0.7:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def save_model(self) -> bool:
        """Save trained model"""
        try:
            import pickle
            model_data = {
                'isolation_forest': self.isolation_forest,
                'random_forest': self.random_forest,
                'scaler': self.scaler,
                'trained': self.trained
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info("Model saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """Load trained model"""
        try:
            import pickle
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.isolation_forest = model_data['isolation_forest']
            self.random_forest = model_data['random_forest']
            self.scaler = model_data['scaler']
            self.trained = model_data['trained']
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not load model: {str(e)}")
            return False
