"""
Authentication Module
JWT-based user authentication and authorization
"""

import logging
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import json
from flask import request, jsonify

logger = logging.getLogger(__name__)

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

class AuthManager:
    """Manage user authentication and JWT tokens"""
    
    def __init__(self, secret_key: str = "your-secret-key-change-in-production"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
        self.users = self._load_default_users()
        self.tokens = {}
    
    def _load_default_users(self) -> Dict[str, Dict]:
        """Load default users"""
        return {
            'admin': {
                'password_hash': self._hash_password('admin123'),
                'role': 'admin',
                'email': 'admin@nads.local'
            },
            'analyst': {
                'password_hash': self._hash_password('analyst123'),
                'role': 'analyst',
                'email': 'analyst@nads.local'
            },
            'viewer': {
                'password_hash': self._hash_password('viewer123'),
                'role': 'viewer',
                'email': 'viewer@nads.local'
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Simple password hashing (use bcrypt in production)"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> Optional[Tuple[str, Dict]]:
        """Authenticate user and return token"""
        if username not in self.users:
            logger.warning(f"Login attempt for non-existent user: {username}")
            return None
        
        user = self.users[username]
        if user['password_hash'] != self._hash_password(password):
            logger.warning(f"Failed login for user: {username}")
            return None
        
        # Generate JWT token
        if not JWT_AVAILABLE:
            # Fallback token without JWT
            token = f"token_{username}_{datetime.now().timestamp()}"
            self.tokens[token] = {
                'username': username,
                'role': user['role'],
                'created': datetime.now().isoformat()
            }
            return token, {'username': username, 'role': user['role'], 'email': user['email']}
        
        try:
            payload = {
                'username': username,
                'role': user['role'],
                'email': user['email'],
                'iat': datetime.now(),
                'exp': datetime.now() + timedelta(hours=self.token_expiry_hours)
            }
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"User logged in: {username}")
            return token, {'username': username, 'role': user['role'], 'email': user['email']}
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        if not token:
            return None
        
        # Check fallback tokens first
        if token in self.tokens:
            return self.tokens[token]
        
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def require_auth(self, f):
        """Decorator for protecting routes"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'Missing authorization token'}), 401
            
            user = self.verify_token(token)
            if not user:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user to request context
            request.user = user
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_role(self, required_role: str):
        """Decorator for role-based access control"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                
                if not token:
                    return jsonify({'error': 'Missing authorization token'}), 401
                
                user = self.verify_token(token)
                if not user:
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                # Check role
                role = user.get('role', 'viewer')
                role_hierarchy = {'admin': 3, 'analyst': 2, 'viewer': 1}
                
                if role_hierarchy.get(role, 0) < role_hierarchy.get(required_role, 0):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                request.user = user
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def add_user(self, username: str, password: str, role: str = 'viewer', email: str = '') -> bool:
        """Add new user"""
        if username in self.users:
            logger.warning(f"User already exists: {username}")
            return False
        
        self.users[username] = {
            'password_hash': self._hash_password(password),
            'role': role,
            'email': email
        }
        logger.info(f"User created: {username}")
        return True
    
    def logout(self, token: str) -> bool:
        """Logout user and invalidate token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return True
