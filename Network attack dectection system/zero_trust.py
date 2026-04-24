"""
Zero-Trust Security Module
Implement zero-trust architecture principles
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class TrustLevel(Enum):
    """Trust levels in zero-trust model"""
    UNKNOWN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    TRUSTED = 4

class ZeroTrustPolicy:
    """Zero-trust security policy enforcement"""
    
    def __init__(self):
        self.device_inventory = {}  # Known devices
        self.user_profiles = {}  # User behavior profiles
        self.network_segments = {}  # Network segmentation
        self.access_policies = {}  # Fine-grained policies
        self.verification_logs = []  # All verification attempts
    
    def register_device(self, device_id: str, device_info: Dict) -> bool:
        """Register device in zero-trust model"""
        self.device_inventory[device_id] = {
            'id': device_id,
            'info': device_info,
            'registered_at': datetime.now().isoformat(),
            'trust_score': 0.5,
            'last_verified': None,
            'violation_count': 0
        }
        logger.info(f"Device registered: {device_id}")
        return True
    
    def verify_device(self, device_id: str, context: Dict) -> Dict:
        """Verify device context (never trust, always verify)"""
        if device_id not in self.device_inventory:
            logger.warning(f"Verification failed: Unknown device {device_id}")
            return {
                'verified': False,
                'trust_level': TrustLevel.UNKNOWN.name,
                'reason': 'Device not registered'
            }
        
        device = self.device_inventory[device_id]
        
        # Gather verification factors
        verification_factors = []
        
        # 1. Device integrity check
        if self._check_device_integrity(device_id, context):
            verification_factors.append('integrity')
        
        # 2. Device posture check
        if self._check_device_posture(device_id, context):
            verification_factors.append('posture')
        
        # 3. Network location check
        if self._check_location(device_id, context):
            verification_factors.append('location')
        
        # 4. Time-based check
        if self._check_time_context(device_id, context):
            verification_factors.append('time')
        
        # Calculate trust score based on verification factors
        factor_count = len(verification_factors)
        trust_score = factor_count / 4.0  # Maximum 4 factors
        
        device['trust_score'] = trust_score
        device['last_verified'] = datetime.now().isoformat()
        
        # Determine trust level
        if trust_score >= 0.8:
            trust_level = TrustLevel.TRUSTED
        elif trust_score >= 0.6:
            trust_level = TrustLevel.HIGH
        elif trust_score >= 0.4:
            trust_level = TrustLevel.MEDIUM
        else:
            trust_level = TrustLevel.LOW
        
        # Log verification
        self.verification_logs.append({
            'device_id': device_id,
            'timestamp': datetime.now().isoformat(),
            'trust_level': trust_level.name,
            'factors': verification_factors,
            'context': context
        })
        
        return {
            'verified': trust_level in [TrustLevel.TRUSTED, TrustLevel.HIGH],
            'trust_level': trust_level.name,
            'trust_score': trust_score,
            'factors': verification_factors
        }
    
    def _check_device_integrity(self, device_id: str, context: Dict) -> bool:
        """Check device integrity"""
        expected_hash = context.get('expected_hash')
        actual_hash = context.get('actual_hash')
        
        if not expected_hash or not actual_hash:
            return False
        
        return expected_hash == actual_hash
    
    def _check_device_posture(self, device_id: str, context: Dict) -> bool:
        """Check device security posture"""
        checks = {
            'firewall_enabled': context.get('firewall_enabled', False),
            'antivirus_enabled': context.get('antivirus_enabled', False),
            'patches_current': context.get('patches_current', False),
            'encryption_enabled': context.get('encryption_enabled', False)
        }
        
        # All checks must pass
        return all(checks.values())
    
    def _check_location(self, device_id: str, context: Dict) -> bool:
        """Check network location"""
        ip_address = context.get('ip_address')
        network_segment = context.get('network_segment')
        
        if not ip_address or not network_segment:
            return False
        
        # Check if IP is in expected network
        return self._is_ip_in_network(ip_address, network_segment)
    
    def _check_time_context(self, device_id: str, context: Dict) -> bool:
        """Check if access is within expected time"""
        access_time = context.get('access_time')
        expected_hours = context.get('expected_hours', [9, 17])  # 9 AM - 5 PM
        
        if not access_time:
            return False
        
        try:
            hour = int(access_time.split(':')[0])
            return expected_hours[0] <= hour < expected_hours[1]
        except:
            return False
    
    def _is_ip_in_network(self, ip: str, network: str) -> bool:
        """Check if IP is in network (simplified)"""
        # Simplified check - in production, use ipaddress module
        ip_parts = ip.split('.')
        network_parts = network.split('.')
        
        for i in range(3):  # Check first 3 octets for class C
            if ip_parts[i] != network_parts[i]:
                return False
        
        return True
    
    def create_segmented_policy(self, segment_name: str, rules: List[Dict]) -> bool:
        """Create network segmentation policy"""
        self.network_segments[segment_name] = {
            'name': segment_name,
            'rules': rules,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        logger.info(f"Segmented policy created: {segment_name}")
        return True
    
    def create_access_policy(self, policy_id: str, policy: Dict) -> bool:
        """Create fine-grained access policy"""
        self.access_policies[policy_id] = {
            'id': policy_id,
            'name': policy.get('name'),
            'resources': policy.get('resources', []),
            'conditions': policy.get('conditions', {}),
            'actions': policy.get('actions', 'allow'),
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        logger.info(f"Access policy created: {policy_id}")
        return True
    
    def evaluate_access(self, user_id: str, resource: str, context: Dict) -> Dict:
        """Evaluate access request (zero-trust decision)"""
        
        # 1. Verify user identity
        user_verified = self._verify_user(user_id, context)
        if not user_verified:
            return {
                'allowed': False,
                'reason': 'User not verified',
                'decision': 'DENY'
            }
        
        # 2. Verify device
        device_verification = self.verify_device(
            context.get('device_id', 'unknown'),
            context
        )
        if not device_verification.get('verified'):
            return {
                'allowed': False,
                'reason': f"Device verification failed: {device_verification['trust_level']}",
                'decision': 'DENY'
            }
        
        # 3. Check access policy
        policy_allowed = self._check_policy(user_id, resource, context)
        if not policy_allowed:
            return {
                'allowed': False,
                'reason': 'Access policy violation',
                'decision': 'DENY'
            }
        
        # 4. Check for anomalies
        anomaly_detected = self._detect_anomaly(user_id, context)
        if anomaly_detected:
            # Allow but monitor (with MFA)
            return {
                'allowed': True,
                'reason': 'Anomaly detected - additional verification required',
                'decision': 'ALLOW_WITH_MFA',
                'require_mfa': True
            }
        
        # All checks passed
        return {
            'allowed': True,
            'reason': 'All verification checks passed',
            'decision': 'ALLOW',
            'trust_level': device_verification.get('trust_level')
        }
    
    def _verify_user(self, user_id: str, context: Dict) -> bool:
        """Verify user identity"""
        # In production, verify against IdP (identity provider)
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'id': user_id,
                'first_login': datetime.now().isoformat(),
                'login_count': 1
            }
        else:
            self.user_profiles[user_id]['login_count'] += 1
        
        return True
    
    def _check_policy(self, user_id: str, resource: str, context: Dict) -> bool:
        """Check if access matches policy"""
        # Check all active policies
        for policy_id, policy in self.access_policies.items():
            if policy['status'] != 'active':
                continue
            
            # Check if resource matches
            if resource in policy.get('resources', []):
                # Check conditions
                conditions_met = self._check_conditions(policy.get('conditions', {}), context)
                
                if conditions_met:
                    return policy.get('actions') == 'allow'
        
        # Default deny if no matching policy allows
        return False
    
    def _check_conditions(self, conditions: Dict, context: Dict) -> bool:
        """Check policy conditions"""
        for condition_key, condition_value in conditions.items():
            context_value = context.get(condition_key)
            
            if isinstance(condition_value, list):
                if context_value not in condition_value:
                    return False
            else:
                if context_value != condition_value:
                    return False
        
        return True
    
    def _detect_anomaly(self, user_id: str, context: Dict) -> bool:
        """Detect anomalous access patterns"""
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        
        # Simple anomaly detection
        anomalies = []
        
        # Check for unusual location
        if 'previous_location' in profile:
            if context.get('location') != profile['previous_location']:
                anomalies.append('location_change')
        
        # Check for unusual time
        if 'previous_hour' in profile:
            if context.get('access_time'):
                current_hour = int(context['access_time'].split(':')[0])
                if abs(current_hour - profile['previous_hour']) > 3:
                    anomalies.append('time_anomaly')
        
        # Update profile
        profile['previous_location'] = context.get('location')
        if context.get('access_time'):
            profile['previous_hour'] = int(context['access_time'].split(':')[0])
        
        return len(anomalies) > 0
    
    def get_verification_report(self, time_period: str = 'daily') -> Dict:
        """Generate verification report"""
        return {
            'report_type': f'{time_period} Verification Report',
            'generated_at': datetime.now().isoformat(),
            'total_verifications': len(self.verification_logs),
            'devices_registered': len(self.device_inventory),
            'network_segments': len(self.network_segments),
            'access_policies': len(self.access_policies),
            'trusted_devices': sum(1 for d in self.device_inventory.values() if d.get('trust_score', 0) >= 0.8),
            'violations': sum(1 for d in self.device_inventory.values() if d.get('violation_count', 0) > 0)
        }
    
    def enforce_least_privilege(self, user_id: str, role: str) -> Dict:
        """Apply least privilege principle"""
        privilege_levels = {
            'admin': ['read', 'write', 'delete', 'configure'],
            'analyst': ['read', 'write'],
            'viewer': ['read']
        }
        
        return {
            'user_id': user_id,
            'role': role,
            'permissions': privilege_levels.get(role, []),
            'enforced_at': datetime.now().isoformat()
        }
