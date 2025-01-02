import json
import time
import ipaddress
import socket
import threading
import os

# Load the configuration from the file
with open('config.json', 'r') as f:
    config = json.load(f)

# Dynamically import functions from the protocol_functions.py file
def import_protocol_function(protocol_name):
    """Dynamically import the function for the given protocol."""
    try:
        # Import the protocol functions module
        module = __import__("protocol_functions", fromlist=[protocol_name])
        # Return the corresponding function
        return getattr(module, f"check_{protocol_name}_device")
    except (ImportError, AttributeError) as e:
        print(f"Error importing function for protocol {protocol_name}: {e}")
        return None

# Scan a single IP address
def scan_ip(ip, port, timeout, result_list):
    """Scan a single IP for open Modbus port and add to results if reachable."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((str(ip), port)) == 0:
                print(f"Device found at {ip}")
                result_list.append(str(ip))
    except Exception as e:
        print(f"Error scanning {ip}: {e}")

# Scan the network for devices using threading
def scan_network(subnet, port, timeout):
    """Scan the network using threading for faster execution."""
    network = ipaddress.IPv4Network(subnet)
    threads = []
    results = []

    for ip in network.hosts():
        thread = threading.Thread(target=scan_ip, args=(ip, port, timeout, results))
        threads.append(thread)
        thread.start()
        if len(threads) >= 50:  # Limit the number of concurrent threads
            for t in threads:
                t.join()
            threads = []

    # Ensure all remaining threads complete
    for t in threads:
        t.join()

    return results

# Modbus protocol: Only Modbus will be used here
selected_protocol = "modbus"

# Import the Modbus protocol function
protocol_function = import_protocol_function(selected_protocol)

# Scan the network for devices
devices = scan_network(config["network_scan"]["subnet"], config["modbus_settings"]["port"], config["network_scan"]["scan_timeout"])

# Check each device for the Modbus protocol
if protocol_function:
    for device_ip in devices:
        print(f"\nChecking Modbus device at {device_ip}...")
        if protocol_function(device_ip, config["modbus_settings"]["port"], 
                              config["modbus_settings"]["timeout"], 
                              config["modbus_settings"]["retries"]):
            config["connected_devices"].append({"ip": device_ip, "protocol": "modbus"})

# Save connected devices to a JSON file
output_file = 'connected_devices.json'
if not os.path.exists(output_file):
    with open(output_file, 'w') as f:
        json.dump([], f)  # Create the file if it doesn't exist

with open(output_file, 'w') as f:
    json.dump(config["connected_devices"], f, indent=4)

# Output the list of connected devices
print("\nConnected devices:")
for device in config["connected_devices"]:
    print(f"IP: {device['ip']}, Protocol: {device['protocol']}")

