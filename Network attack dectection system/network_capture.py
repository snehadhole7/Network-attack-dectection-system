"""
Network Packet Capture Module
Captures live network packets and processes them
"""

import logging
from scapy.all import sniff, IP, TCP, UDP, ICMP
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class NetworkCapture:
    """Capture live network packets"""
    
    def __init__(self, interface: str = None, packet_count: int = 1000):
        self.interface = interface
        self.packet_count = packet_count
        self.packets = []
        self.running = False
        
    def packet_callback(self, packet: Any) -> None:
        """Process captured packet"""
        try:
            packet_data = {
                'timestamp': datetime.now().isoformat(),
                'size': len(packet),
                'src_ip': None,
                'dst_ip': None,
                'src_port': None,
                'dst_port': None,
                'protocol': None,
                'flags': None,
                'raw_data': packet.show(dump=True)
            }
            
            # Extract IP information
            if IP in packet:
                ip_layer = packet[IP]
                packet_data['src_ip'] = ip_layer.src
                packet_data['dst_ip'] = ip_layer.dst
                packet_data['protocol'] = ip_layer.proto
            
            # Extract TCP information
            if TCP in packet:
                tcp_layer = packet[TCP]
                packet_data['src_port'] = tcp_layer.sport
                packet_data['dst_port'] = tcp_layer.dport
                packet_data['flags'] = str(tcp_layer.flags)
            
            # Extract UDP information
            elif UDP in packet:
                udp_layer = packet[UDP]
                packet_data['src_port'] = udp_layer.sport
                packet_data['dst_port'] = udp_layer.dport
            
            self.packets.append(packet_data)
            logger.debug(f"Captured packet: {packet_data['src_ip']} -> {packet_data['dst_ip']}")
            
        except Exception as e:
            logger.error(f"Error processing packet: {str(e)}")
    
    def start_capture(self) -> List[Dict]:
        """Start capturing network packets"""
        logger.info(f"Starting packet capture on interface: {self.interface}")
        try:
            self.running = True
            sniff(
                iface=self.interface,
                prn=self.packet_callback,
                count=self.packet_count,
                store=False
            )
            self.running = False
            logger.info(f"Captured {len(self.packets)} packets")
            return self.packets
        except PermissionError:
            logger.error("Permission denied: Run with administrator/sudo privileges")
            self.running = False
            return []
        except Exception as e:
            logger.error(f"Capture error: {str(e)}")
            self.running = False
            return []
    
    def stop_capture(self) -> None:
        """Stop capturing packets"""
        self.running = False
        logger.info("Packet capture stopped")
    
    def get_packets(self) -> List[Dict]:
        """Return captured packets"""
        return self.packets
    
    def clear_packets(self) -> None:
        """Clear captured packets"""
        self.packets.clear()
