"""
Blockchain Audit Trail Module
Immutable audit logging using blockchain principles
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import hashlib
import json

logger = logging.getLogger(__name__)

class BlockchainAuditTrail:
    """Blockchain-based immutable audit trail"""
    
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = {
            'index': 0,
            'timestamp': datetime.now().isoformat(),
            'transactions': [],
            'previous_hash': '0',
            'hash': self._calculate_hash({'index': 0, 'timestamp': datetime.now().isoformat(), 'transactions': [], 'previous_hash': '0'}),
            'nonce': 0
        }
        self.chain.append(genesis_block)
        logger.info("Genesis block created")
    
    def add_transaction(self, event_type: str, details: Dict, severity: str = 'INFO') -> str:
        """Add a transaction (audit event) to pending pool"""
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details,
            'severity': severity,
            'tx_id': self._generate_tx_id(event_type, details)
        }
        
        self.pending_transactions.append(transaction)
        logger.info(f"Transaction added: {event_type}")
        
        return transaction['tx_id']
    
    def _generate_tx_id(self, event_type: str, details: Dict) -> str:
        """Generate unique transaction ID"""
        data = f"{event_type}{datetime.now().isoformat()}{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def mine_block(self) -> Dict:
        """Mine a new block with pending transactions"""
        if not self.pending_transactions:
            logger.warning("No pending transactions to mine")
            return {}
        
        previous_block = self.chain[-1]
        new_block = {
            'index': len(self.chain),
            'timestamp': datetime.now().isoformat(),
            'transactions': self.pending_transactions[:],
            'previous_hash': previous_block['hash'],
            'hash': '',
            'nonce': 0
        }
        
        # Proof of work (simplified)
        new_block['hash'] = self._calculate_hash(new_block)
        
        self.chain.append(new_block)
        self.pending_transactions = []
        
        logger.info(f"Block {new_block['index']} mined with {len(new_block['transactions'])} transactions")
        
        return new_block
    
    def _calculate_hash(self, block: Dict) -> str:
        """Calculate hash of a block"""
        block_copy = block.copy()
        block_copy.pop('hash', None)
        block_copy.pop('nonce', None)
        
        block_string = json.dumps(block_copy, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash
            if current_block['hash'] != self._calculate_hash(current_block):
                logger.error(f"Invalid hash at block {i}")
                return False
            
            # Verify previous hash
            if current_block['previous_hash'] != previous_block['hash']:
                logger.error(f"Invalid previous hash at block {i}")
                return False
        
        logger.info("Blockchain is valid")
        return True
    
    def get_audit_log(self, event_type: str = None, severity: str = None) -> List[Dict]:
        """Retrieve audit log with optional filtering"""
        audit_log = []
        
        for block in self.chain:
            for transaction in block.get('transactions', []):
                # Apply filters
                if event_type and transaction['type'] != event_type:
                    continue
                if severity and transaction['severity'] != severity:
                    continue
                
                audit_log.append({
                    'block_index': block['index'],
                    'block_hash': block['hash'],
                    'timestamp': transaction['timestamp'],
                    'type': transaction['type'],
                    'severity': transaction['severity'],
                    'details': transaction['details'],
                    'tx_id': transaction['tx_id']
                })
        
        return audit_log
    
    def get_chain_statistics(self) -> Dict:
        """Get blockchain statistics"""
        total_transactions = sum(len(block.get('transactions', [])) for block in self.chain)
        
        severity_counts = {}
        for block in self.chain:
            for tx in block.get('transactions', []):
                severity = tx.get('severity', 'INFO')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'chain_valid': self.is_chain_valid(),
            'severity_distribution': severity_counts,
            'creation_time': self.chain[0]['timestamp'] if self.chain else None
        }
    
    def export_audit_trail(self, format: str = 'json') -> str:
        """Export audit trail in specified format"""
        if format == 'json':
            return json.dumps({
                'chain': self.chain,
                'pending_transactions': self.pending_transactions,
                'statistics': self.get_chain_statistics()
            }, indent=2, default=str)
        
        elif format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Block', 'Timestamp', 'Type', 'Severity', 'Transaction ID'])
            
            for log_entry in self.get_audit_log():
                writer.writerow([
                    log_entry['block_index'],
                    log_entry['timestamp'],
                    log_entry['type'],
                    log_entry['severity'],
                    log_entry['tx_id']
                ])
            
            return output.getvalue()
        
        return ''
