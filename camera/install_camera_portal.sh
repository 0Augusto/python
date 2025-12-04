#!/bin/bash
# install_camera_portal.sh

set -e

echo "Installing IP Camera Portal Manager..."

# Install dependencies
apt update
apt install -y arp-scan python3-pip iptables-persistent net-tools
pip3 install requests netifaces

# Create directories
mkdir -p /etc/camera_portal
mkdir -p /opt/camera_portal
mkdir -p /var/log/camera_portal

# Copy the script
cp camera_portal_manager.py /opt/camera_portal/
chmod +x /opt/camera_portal/camera_portal_manager.py

# Create default configuration
cat > /etc/camera_portal/config.json << EOF
{
  "virtual_ips": {},
  "portal_api_url": "https://your-portal-api.example.com",
  "portal_api_key": "your-api-key-here",
  "virtual_ip_base": "192.168.1.200",
  "network_interface": "eth0"
}
EOF

# Create systemd service
cat > /etc/systemd/system/camera-portal.service << EOF
[Unit]
Description=IP Camera Portal Manager
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/camera_portal/camera_portal_manager.py
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable camera-portal.service

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit /etc/camera_portal/config.json with your portal details"
echo "2. Start the service: sudo systemctl start camera-portal"
echo "3. Check status: sudo systemctl status camera-portal"
echo "4. View logs: sudo journalctl -u camera-portal -f"
