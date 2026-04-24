"""
Data Preprocessor Module
Cleans and formats network data for analysis
"""

import logging
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Preprocess network data"""
    
    def __init__(self):
        self.raw_data = []
        self.processed_data = []
    
    def load_data(self, packets: List[Dict]) -> None:
        """Load raw packet data"""
        self.raw_data = packets
        logger.info(f"Loaded {len(packets)} packets for preprocessing")
    
    def remove_duplicates(self) -> None:
        """Remove duplicate packets"""
        unique_packets = []
        seen = set()
        
        for packet in self.raw_data:
            packet_key = (
                packet.get('src_ip'),
                packet.get('dst_ip'),
                packet.get('src_port'),
                packet.get('dst_port'),
                packet.get('protocol')
            )
            
            if packet_key not in seen:
                unique_packets.append(packet)
                seen.add(packet_key)
        
        self.raw_data = unique_packets
        logger.info(f"Removed duplicates: {len(self.processed_data)} packets remaining")
    
    def remove_noise(self) -> None:
        """Remove noisy/incomplete packets"""
        cleaned = []
        
        for packet in self.raw_data:
            # Filter out packets without IP information
            if packet.get('src_ip') and packet.get('dst_ip'):
                # Skip localhost traffic
                if not ('127.0.0.1' in [packet['src_ip'], packet['dst_ip']]):
                    cleaned.append(packet)
        
        self.raw_data = cleaned
        logger.info(f"After noise removal: {len(cleaned)} packets")
    
    def normalize_data(self) -> None:
        """Normalize and format data"""
        normalized = []
        
        for packet in self.raw_data:
            try:
                norm_packet = {
                    'timestamp': packet.get('timestamp', datetime.now().isoformat()),
                    'src_ip': packet.get('src_ip', 'Unknown'),
                    'dst_ip': packet.get('dst_ip', 'Unknown'),
                    'src_port': int(packet.get('src_port', 0)) if packet.get('src_port') else 0,
                    'dst_port': int(packet.get('dst_port', 0)) if packet.get('dst_port') else 0,
                    'protocol': self._normalize_protocol(packet.get('protocol')),
                    'size': int(packet.get('size', 0)),
                    'flags': packet.get('flags', 'None')
                }
                normalized.append(norm_packet)
            except Exception as e:
                logger.warning(f"Error normalizing packet: {str(e)}")
        
        self.processed_data = normalized
        logger.info(f"Data normalization complete: {len(normalized)} packets processed")
    
    def _normalize_protocol(self, protocol: Any) -> str:
        """Normalize protocol number to protocol name"""
        protocol_map = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            41: 'IPv6',
            50: 'ESP'
        }
        
        if isinstance(protocol, str):
            return protocol
        elif isinstance(protocol, int):
            return protocol_map.get(protocol, f'Other({protocol})')
        return 'Unknown'
    
    def process(self, packets: List[Dict]) -> List[Dict]:
        """Run complete preprocessing pipeline"""
        self.load_data(packets)
        self.remove_noise()
        self.remove_duplicates()
        self.normalize_data()
        
        logger.info(f"Processing complete: {len(self.processed_data)} packets ready for analysis")
        return self.processed_data
    
    def get_processed_data(self) -> List[Dict]:
        """Return processed data"""
        return self.processed_data
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return processed data as DataFrame"""
        return pd.DataFrame(self.processed_data)
