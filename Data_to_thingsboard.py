import subprocess
import time
import json
import csv
import requests
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('thingsboard_forwarder.log')
    ]
)

# ThingsBoard configuration
THINGSBOARD_HOST = "http://localhost:8080"  # Replace with your ThingsBoard host
DEVICE_TOKENS = {}  # Will store device tokens as {ip: access_token}
TOKEN_FILE = "device_tokens.json"  # File to store tokens persistently

# File paths
CSV_FILE = "modbus_data.csv"
FETCHING_SCRIPT = "Fetching_data.py"
LAST_PROCESSED_LINE = 0

def load_device_tokens():
    """Load device tokens from file if it exists."""
    global DEVICE_TOKENS
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                DEVICE_TOKENS = json.load(f)
                logging.info(f"Loaded {len(DEVICE_TOKENS)} device tokens from file")
    except Exception as e:
        logging.error(f"Error loading device tokens: {str(e)}")

def save_device_tokens():
    """Save device tokens to file."""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(DEVICE_TOKENS, f)
            logging.info("Saved device tokens to file")
    except Exception as e:
        logging.error(f"Error saving device tokens: {str(e)}")

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(CSV_FILE):
            process_new_data()

def get_or_create_device(device_ip):
    """Get or create a device in ThingsBoard and return its access token."""
    if device_ip in DEVICE_TOKENS:
        return DEVICE_TOKENS[device_ip]

    # ThingsBoard API credentials
    admin_username = "tenant@thingsboard.org"  # Replace with your admin username
    admin_password = "tenant"  # Replace with your admin password

    # Get JWT token
    auth_url = f"{THINGSBOARD_HOST}/api/auth/login"
    auth_data = {"username": admin_username, "password": admin_password}
    
    try:
        auth_response = requests.post(auth_url, json=auth_data)
        jwt_token = auth_response.json()['token']

        # Create device if it doesn't exist
        headers = {
            'Content-Type': 'application/json',
            'X-Authorization': f'Bearer {jwt_token}'
        }

        # Check if device exists
        device_name = f"modbus_device_{device_ip.replace('.', '_')}"
        devices_url = f"{THINGSBOARD_HOST}/api/tenant/devices?deviceName={device_name}"
        devices_response = requests.get(devices_url, headers=headers)

        if devices_response.status_code == 200 and devices_response.json()['data']:
            device_id = devices_response.json()['data'][0]['id']['id']
        else:
            # Create new device
            device_data = {
                "name": device_name,
                "type": "modbus_device"
            }
            create_response = requests.post(
                f"{THINGSBOARD_HOST}/api/device",
                headers=headers,
                json=device_data
            )
            device_id = create_response.json()['id']['id']

        # Get device credentials
        creds_url = f"{THINGSBOARD_HOST}/api/device/{device_id}/credentials"
        creds_response = requests.get(creds_url, headers=headers)
        access_token = creds_response.json()['credentialsId']

        DEVICE_TOKENS[device_ip] = access_token
        save_device_tokens()  # Save tokens whenever a new one is created
        return access_token

    except Exception as e:
        logging.error(f"Error getting/creating device: {str(e)}")
        return None

def process_new_data():
    """Process new lines from the CSV file and send to ThingsBoard."""
    global LAST_PROCESSED_LINE
    
    try:
        with open(CSV_FILE, 'r') as f:
            csv_reader = csv.DictReader(f)
            rows = list(csv_reader)
            
            # Process only new rows
            for row in rows[LAST_PROCESSED_LINE:]:
                device_ip = row['device_ip']
                access_token = get_or_create_device(device_ip)
                
                if not access_token:
                    logging.error(f"Could not get access token for device {device_ip}")
                    continue

                # Prepare telemetry data
                telemetry = {
                    'ts': int(time.time() * 1000),
                    'values': {
                        'current': float(row['current']),
                        'voltage': float(row['voltage']),
                        'temperature': float(row['temperature']),
                        'power': float(row['power'])
                    }
                }

                # Send data to ThingsBoard
                tb_url = f"{THINGSBOARD_HOST}/api/v1/{access_token}/telemetry"
                response = requests.post(tb_url, json=telemetry)
                
                if response.status_code == 200:
                    logging.info(f"Successfully sent data to ThingsBoard for device {device_ip}")
                else:
                    logging.error(f"Failed to send data to ThingsBoard for device {device_ip}: {response.status_code}")

            LAST_PROCESSED_LINE = len(rows)

    except Exception as e:
        logging.error(f"Error processing CSV data: {str(e)}")

def main():
    # Load existing device tokens
    load_device_tokens()

    # Start the Fetching_data.py script as a subprocess
    try:
        fetching_process = subprocess.Popen(['python', FETCHING_SCRIPT])
        logging.info("Started Fetching_data.py successfully")

        # Set up file monitoring
        event_handler = CSVHandler()
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=False)
        observer.start()
        logging.info("Started CSV file monitoring")

        # Main loop
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            observer.stop()
            fetching_process.terminate()
            logging.info("Stopping the application...")

        observer.join()
        fetching_process.wait()

    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()