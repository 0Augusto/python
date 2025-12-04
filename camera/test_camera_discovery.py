#!/usr/bin/env python3
# test_camera_discovery.py

import subprocess
import json

def test_network_scan():
    """Test network scanning"""
    print("Testing network scan...")
    
    # Test arp-scan
    try:
        result = subprocess.run(
            "sudo arp-scan --localnet --interface=eth0 --quiet",
            shell=True,
            capture_output=True,
            text=True
        )
        
        print(f"Scan output (first 10 lines):")
        for line in result.stdout.split('\n')[:10]:
            if line.strip():
                print(f"  {line}")
                
    except Exception as e:
        print(f"Error: {e}")

def test_virtual_ip():
    """Test virtual IP creation"""
    print("\nTesting virtual IP creation...")
    
    test_ip = "192.168.1.250"
    
    # Add test IP
    subprocess.run(f"sudo ip addr add {test_ip}/24 dev eth0 label eth0:test", shell=True)
    
    # Verify
    result = subprocess.run("ip addr show eth0:test", shell=True, capture_output=True, text=True)
    
    if test_ip in result.stdout:
        print(f"✓ Virtual IP {test_ip} created successfully")
    else:
        print("✗ Failed to create virtual IP")
    
    # Cleanup
    subprocess.run(f"sudo ip addr del {test_ip}/24 dev eth0 label eth0:test", shell=True)

if __name__ == "__main__":
    print("IP Camera Portal Manager - Test Script")
    print("=" * 50)
    
    test_network_scan()
    test_virtual_ip()
    
    print("\nTest complete!")
