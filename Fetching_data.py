import json
import subprocess
import os
from pymodbus.client import ModbusTcpClient
import struct
import logging
import time
import csv
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Constants from original script
SCAN_SCRIPT = "modbus_network_scan_script.py"
CONNECTED_DEVICES_FILE = "connected_devices.json"
CSV_FILE = "modbus_data.csv"
START_ADDRESS = 0
TOTAL_REGISTERS = 56
ADDRESS_OFFSET = 30001
POLLING_INTERVAL = 5  # seconds
MAX_RECONNECTION_ATTEMPTS = 3
RECONNECTION_DELAY = 5  # seconds

# Parameter mapping
PARAMETERS = {
    "current": [30031, 30032],
    "voltage": [30025, 30026],
    "temperature": [30027, 30028],
    "power": [30033, 30034]
}

class ModbusDevice:
    def __init__(self, ip, port=502):
        self.ip = ip
        self.port = port
        self.client = None
        self.connected = False
        self.reconnection_attempts = 0
        self.last_reconnection_time = 0

    def connect(self):
        """Attempt to connect to the Modbus device."""
        try:
            if self.client:
                self.client.close()
            
            self.client = ModbusTcpClient(self.ip, port=self.port)
            self.connected = self.client.connect()
            
            if self.connected:
                self.reconnection_attempts = 0
                logging.info(f"Successfully connected to {self.ip}")
            return self.connected
        except Exception as e:
            logging.error(f"Error connecting to {self.ip}: {str(e)}")
            return False

    def disconnect(self):
        """Safely disconnect from the device."""
        if self.client:
            self.client.close()
        self.connected = False

    def attempt_reconnection(self):
        """Attempt to reconnect to the device with backoff."""
        current_time = time.time()
        
        # Check if enough time has passed since last reconnection attempt
        if current_time - self.last_reconnection_time < RECONNECTION_DELAY:
            return False

        self.last_reconnection_time = current_time
        self.reconnection_attempts += 1
        
        if self.reconnection_attempts <= MAX_RECONNECTION_ATTEMPTS:
            logging.info(f"Attempting reconnection to {self.ip} (Attempt {self.reconnection_attempts})")
            return self.connect()
        else:
            logging.error(f"Max reconnection attempts reached for {self.ip}")
            return False

def run_network_scan():
    """Run the network scan script as a subprocess and wait for completion."""
    try:
        logging.info("Starting network scan...")
        result = subprocess.run(['python', SCAN_SCRIPT], 
                              check=True, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            logging.info("Network scan completed successfully")
            return True
        else:
            logging.error(f"Network scan failed with error: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error running network scan: {str(e)}")
        return False

def registers_to_float(register1, register2):
    """Convert two registers to a float value."""
    combined_registers = (register1 << 16) | register2
    return struct.unpack('!f', struct.pack('!I', combined_registers))[0]

def load_connected_devices():
    """Load the list of connected devices from the JSON file."""
    if not os.path.exists(CONNECTED_DEVICES_FILE):
        logging.error(f"Connected devices file {CONNECTED_DEVICES_FILE} not found.")
        return []

    with open(CONNECTED_DEVICES_FILE, "r") as f:
        return json.load(f)

def initialize_csv(devices):
    """Initialize CSV file with headers."""
    fieldnames = ['timestamp', 'device_ip']
    fieldnames.extend(PARAMETERS.keys())
    
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    return fieldnames

def save_to_csv(data, ip, fieldnames):
    """Save the data to CSV file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row_data = {
        'timestamp': timestamp,
        'device_ip': ip
    }
    row_data.update(data['interpreted_values'])
    
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(row_data)

def fetch_modbus_registers(device):
    """Fetch data from Modbus input registers of a device."""
    if not device.connected:
        if not device.attempt_reconnection():
            return None

    try:
        logging.info(f"Reading registers {ADDRESS_OFFSET} to {ADDRESS_OFFSET + TOTAL_REGISTERS - 1} from {device.ip}...")
        
        response = device.client.read_input_registers(
            address=START_ADDRESS,
            count=TOTAL_REGISTERS
        )

        if response is None or response.isError():
            logging.error(f"Error reading registers from {device.ip}")
            device.connected = False
            return None

        all_registers = response.registers
        
        data = {
            "raw_registers": {},
            "interpreted_values": {}
        }

        for i, value in enumerate(all_registers):
            register_number = ADDRESS_OFFSET + i
            data["raw_registers"][register_number] = value

        for key, (reg1, reg2) in PARAMETERS.items():
            index1 = reg1 - ADDRESS_OFFSET
            index2 = reg2 - ADDRESS_OFFSET

            if index1 < 0 or index2 < 0 or index1 >= len(all_registers) or index2 >= len(all_registers):
                logging.warning(f"Registers {reg1} and {reg2} are out of range.")
                continue

            value = registers_to_float(all_registers[index1], all_registers[index2])
            data["interpreted_values"][key] = value

        return data
    except Exception as e:
        logging.error(f"Error fetching data from {device.ip}: {str(e)}")
        device.connected = False
        return None

def main():
    if not run_network_scan():
        logging.error("Network scan failed. Exiting...")
        return

    logging.info("Loading connected devices...")
    devices = load_connected_devices()
    if not devices:
        logging.error("No connected devices found.")
        return

    fieldnames = initialize_csv(devices)

    # Create ModbusDevice instances for each device
    modbus_devices = {}
    for device in devices:
        if device.get("protocol") == "modbus":
            ip = device.get("ip")
            modbus_device = ModbusDevice(ip)
            if modbus_device.connect():
                modbus_devices[ip] = modbus_device

    if not modbus_devices:
        logging.error("No Modbus devices connected.")
        return

    try:
        while True:
            for ip, device in modbus_devices.items():
                register_data = fetch_modbus_registers(device)
                
                if register_data:
                    save_to_csv(register_data, ip, fieldnames)
                    logging.info(f"\nData from {ip}:")
                    for key, value in register_data["interpreted_values"].items():
                        logging.info(f"{key}: {value}")
            
            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        logging.info("\nStopping data collection...")
    finally:
        for device in modbus_devices.values():
            device.disconnect()

if __name__ == "__main__":
    main()
