#!/usr/bin/env python3
"""
IP Camera Portal Manager
Detects local IP cameras, manages virtual IPs, and handles RTSP streams from AWS
"""

import os
import sys
import json
import time
import socket
import subprocess
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import netifaces
import requests

# Configuration
CONFIG_FILE = "/etc/camera_portal/config.json"
LOG_FILE = "/var/log/camera_portal.log"
PORTAL_API_URL = "https://your-portal-api.example.com"  # Replace with actual portal URL
PORTAL_API_KEY = "your-api-key-here"  # Replace with your API key

# Network configuration
VIRTUAL_IP_BASE = "192.168.1.200"  # Starting IP for virtual interfaces
VIRTUAL_NETMASK = "255.255.255.0"
VIRTUAL_INTERFACE_PREFIX = "eth0:cam"  # Will become eth0:cam0, eth0:cam1, etc.
RTSP_PORT = 554

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CameraDiscovery:
    """Handles discovery of IP cameras in local network"""
    
    @staticmethod
    def scan_local_network(interface: str = "eth0") -> List[Dict]:
        """
        Scan local network for IP cameras using arp-scan
        Returns list of detected cameras with their details
        """
        cameras = []
        
        try:
            # Run arp-scan to discover devices
            cmd = f"sudo arp-scan --localnet --interface={interface} --quiet"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # Parse arp-scan output
                for line in lines:
                    if not line.startswith(('Starting', 'Ending', 'Interface')) and line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            ip = parts[0].strip()
                            mac = parts[1].strip()
                            vendor = parts[2].strip() if len(parts) > 2 else "Unknown"
                            
                            # Check if device might be a camera (common camera vendors)
                            camera_vendors = [
                                'hikvision', 'dahua', 'axis', 'bosch', 'sony',
                                'panasonic', 'samsung', 'vivotek', 'arecont'
                            ]
                            
                            is_camera = any(vendor.lower().find(v) != -1 
                                          for v in camera_vendors)
                            
                            if is_camera:
                                # Try to detect camera model via ONVIF or HTTP
                                camera_info = CameraDiscovery._probe_camera(ip)
                                cameras.append({
                                    'ip': ip,
                                    'mac': mac,
                                    'vendor': vendor,
                                    'model': camera_info.get('model', 'Unknown'),
                                    'rtsp_url': camera_info.get('rtsp_url'),
                                    'discovered_at': datetime.now().isoformat()
                                })
            
            logger.info(f"Discovered {len(cameras)} potential cameras")
            return cameras
            
        except Exception as e:
            logger.error(f"Error scanning network: {e}")
            return []
    
    @staticmethod
    def _probe_camera(ip: str) -> Dict:
        """Probe camera for more information"""
        info = {'model': 'Unknown', 'rtsp_url': None}
        
        # Common RTSP URLs to try
        rtsp_paths = [
            '/live/main', '/live', '/stream', '/video', '/h264',
            '/cam/realmonitor', '/MediaInput/h264'
        ]
        
        # Try to get basic info via HTTP
        try:
            # Common camera web ports
            ports = [80, 8080, 8000]
            
            for port in ports:
                try:
                    response = requests.get(f"http://{ip}:{port}", timeout=2)
                    if response.status_code == 200:
                        # Parse HTML for camera info (simplified)
                        if 'camera' in response.text.lower() or 'ip' in response.text.lower():
                            info['model'] = 'Generic IP Camera'
                            break
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"HTTP probe failed for {ip}: {e}")
        
        # Try common RTSP URLs
        for path in rtsp_paths:
            rtsp_url = f"rtsp://{ip}:{RTSP_PORT}{path}"
            # Note: Actual RTSP connection test would go here
            info['rtsp_url'] = rtsp_url
            break
        
        return info

class NetworkManager:
    """Manages virtual IP addresses and network configuration"""
    
    def __init__(self):
        self.virtual_ips = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.virtual_ips = config.get('virtual_ips', {})
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            config = {
                'virtual_ips': self.virtual_ips,
                'last_updated': datetime.now().isoformat()
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def create_virtual_ip(self, camera_id: str, base_interface: str = "eth0") -> Optional[str]:
        """
        Create a virtual IP address for a camera
        Returns the created IP address or None if failed
        """
        try:
            # Generate next available IP
            ip_parts = list(map(int, VIRTUAL_IP_BASE.split('.')))
            existing_count = len(self.virtual_ips)
            ip_parts[3] += existing_count  # Increment last octet
            
            virtual_ip = ".".join(map(str, ip_parts))
            interface_name = f"{VIRTUAL_INTERFACE_PREFIX}{existing_count}"
            
            # Create virtual interface
            cmd_add_ip = f"sudo ip addr add {virtual_ip}/{VIRTUAL_NETMASK} dev {base_interface} label {interface_name}"
            cmd_up = f"sudo ip link set {interface_name} up"
            
            # Execute commands
            for cmd in [cmd_add_ip, cmd_up]:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to execute: {cmd}\nError: {result.stderr}")
                    return None
            
            # Store configuration
            self.virtual_ips[camera_id] = {
                'virtual_ip': virtual_ip,
                'interface': interface_name,
                'base_interface': base_interface,
                'created_at': datetime.now().isoformat(),
                'camera_id': camera_id
            }
            
            self.save_config()
            logger.info(f"Created virtual IP {virtual_ip} for camera {camera_id}")
            
            return virtual_ip
            
        except Exception as e:
            logger.error(f"Error creating virtual IP: {e}")
            return None
    
    def remove_virtual_ip(self, camera_id: str):
        """Remove virtual IP address"""
        try:
            if camera_id in self.virtual_ips:
                config = self.virtual_ips[camera_id]
                virtual_ip = config['virtual_ip']
                interface = config['interface']
                
                # Remove IP address
                cmd = f"sudo ip addr del {virtual_ip}/32 dev {config['base_interface']} label {interface}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    del self.virtual_ips[camera_id]
                    self.save_config()
                    logger.info(f"Removed virtual IP {virtual_ip} for camera {camera_id}")
                else:
                    logger.error(f"Failed to remove IP: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"Error removing virtual IP: {e}")
    
    def setup_port_forwarding(self, virtual_ip: str, camera_ip: str, 
                            rtsp_port: int = RTSP_PORT) -> bool:
        """
        Setup port forwarding from virtual IP to camera IP
        Returns True if successful
        """
        try:
            # Setup iptables rules for port forwarding
            rules = [
                # Forward RTSP traffic
                f"sudo iptables -t nat -A PREROUTING -d {virtual_ip} -p tcp --dport {rtsp_port} "
                f"-j DNAT --to-destination {camera_ip}:{rtsp_port}",
                
                # Masquerade return traffic
                f"sudo iptables -t nat -A POSTROUTING -s {camera_ip} -j MASQUERADE",
                
                # Allow forwarding
                f"sudo iptables -A FORWARD -d {camera_ip} -p tcp --dport {rtsp_port} -j ACCEPT",
                f"sudo iptables -A FORWARD -s {camera_ip} -p tcp --sport {rtsp_port} -j ACCEPT"
            ]
            
            for rule in rules:
                result = subprocess.run(rule, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"Rule may already exist or failed: {result.stderr}")
            
            logger.info(f"Set up port forwarding: {virtual_ip}:{rtsp_port} -> {camera_ip}:{rtsp_port}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up port forwarding: {e}")
            return False

class PortalClient:
    """Handles communication with the web portal"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def register_cameras(self, cameras: List[Dict]) -> bool:
        """Register discovered cameras with portal"""
        try:
            endpoint = f"{self.api_url}/api/cameras/register"
            payload = {
                'machine_id': self._get_machine_id(),
                'cameras': cameras,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Registered {len(cameras)} cameras with portal")
                return True
            else:
                logger.error(f"Failed to register cameras: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering cameras: {e}")
            return False
    
    def get_activated_cameras(self) -> List[Dict]:
        """Get list of activated cameras from portal"""
        try:
            endpoint = f"{self.api_url}/api/cameras/activated"
            params = {'machine_id': self._get_machine_id()}
            
            response = requests.get(endpoint, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('activated_cameras', [])
            else:
                logger.error(f"Failed to get activated cameras: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting activated cameras: {e}")
            return []
    
    def _get_machine_id(self) -> str:
        """Get unique machine identifier"""
        try:
            # Use machine-id or hostname
            with open('/etc/machine-id', 'r') as f:
                return f.read().strip()
        except:
            return socket.gethostname()

class CameraManager:
    """Main camera management class"""
    
    def __init__(self):
        self.discovery = CameraDiscovery()
        self.network = NetworkManager()
        self.portal = PortalClient(PORTAL_API_URL, PORTAL_API_KEY)
        self.running = False
    
    def start(self):
        """Start the camera management service"""
        self.running = True
        logger.info("Starting Camera Manager Service")
        
        # Initial camera discovery
        cameras = self.discovery.scan_local_network()
        if cameras:
            self.portal.register_cameras(cameras)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the camera management service"""
        self.running = False
        logger.info("Stopping Camera Manager Service")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Check for activated cameras from portal
                activated = self.portal.get_activated_cameras()
                
                for camera in activated:
                    camera_id = camera.get('camera_id')
                    original_ip = camera.get('original_ip')
                    
                    if camera_id and original_ip:
                        # Check if virtual IP already exists
                        if camera_id not in self.network.virtual_ips:
                            # Create virtual IP
                            virtual_ip = self.network.create_virtual_ip(camera_id)
                            
                            if virtual_ip:
                                # Setup port forwarding
                                success = self.network.setup_port_forwarding(
                                    virtual_ip, original_ip
                                )
                                
                                if success:
                                    logger.info(f"Camera {camera_id} activated and ready at {virtual_ip}")
                                else:
                                    logger.error(f"Failed to setup port forwarding for {camera_id}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)

def setup_systemd_service():
    """Create systemd service file for automatic startup"""
    service_content = """[Unit]
Description=IP Camera Portal Manager
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /opt/camera_portal/camera_portal_manager.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Create script directory
        os.makedirs("/opt/camera_portal", exist_ok=True)
        
        # Install script
        script_path = "/opt/camera_portal/camera_portal_manager.py"
        with open(__file__, 'r') as src:
            with open(script_path, 'w') as dst:
                dst.write(src.read())
        
        os.chmod(script_path, 0o755)
        
        # Create systemd service
        service_path = "/etc/systemd/system/camera-portal.service"
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        # Enable service
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "camera-portal.service"], check=True)
        
        print(f"Service installed. Start with: sudo systemctl start camera-portal")
        print(f"View logs with: sudo journalctl -u camera-portal -f")
        
    except Exception as e:
        print(f"Error setting up service: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        setup_systemd_service()
        return
    
    # Check if running as root
    if os.geteuid() != 0:
        print("This script must be run as root")
        sys.exit(1)
    
    # Enable IP forwarding
    with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
        f.write('1')
    
    # Start camera manager
    manager = CameraManager()
    
    try:
        manager.start()
    except KeyboardInterrupt:
        manager.stop()
        print("\nService stopped")

if __name__ == "__main__":
    main()
