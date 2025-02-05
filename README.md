# Modbus Data Collection and ThingsBoard Integration System

A comprehensive system for scanning Modbus networks, collecting device data, and forwarding it to ThingsBoard IoT platform. The system automatically discovers Modbus devices on the network, establishes connections, collects real-time data, and forwards it to ThingsBoard for visualization and analysis.

## Features

- Automatic network scanning and Modbus device discovery
- Real-time data collection from multiple Modbus devices
- Automatic device registration and management in ThingsBoard
- Configurable polling intervals and connection parameters
- CSV data logging for local storage
- Robust error handling and automatic reconnection
- Real-time monitoring through ThingsBoard dashboards

## Architecture

The system consists of several Python scripts working together:

1. `modbus_network_scan_script.py`: Scans the network for Modbus devices
2. `protocol_functions.py`: Contains protocol-specific connection testing functions
3. `Fetching_data.py`: Manages Modbus connections and data collection
4. `Data_to_thingsboard.py`: Handles data forwarding to ThingsBoard
5. `config.json`: Central configuration file

## Prerequisites

- Python 3.7 or higher
- ThingsBoard Community Edition or Professional Edition
- Network access to Modbus devices

## Required Python Packages

```bash
pip install pymodbus
pip install requests
pip install watchdog
```

## Configuration

### 1. Edit config.json

```json
{
    "modbus_settings": {
        "port": 502,
        "timeout": 1,
        "retries": 1
    },
    "network_scan": {
        "subnet": "192.168.1.0/25",
        "scan_timeout": 0.5
    },
    "protocols": [
        "modbus",
        "opc",
        "mqtt"
    ],
    "connected_devices": []
}
```

### 2. Configure ThingsBoard Settings

In `Data_to_thingsboard.py`, update the following constants:

```python
THINGSBOARD_HOST = "http://localhost:8080"  # Your ThingsBoard host
admin_username = "tenant@thingsboard.org"    # Your admin username
admin_password = "tenant"                    # Your admin password
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd modbus-thingsboard-integration
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your network settings in `config.json`

4. Set up ThingsBoard:
   - Install and start ThingsBoard
   - Create an administrator account
   - Update ThingsBoard credentials in the code

5. Start the system:
   ```bash
   python Data_to_thingsboard.py
   ```

## How It Works

1. **Network Discovery**:
   - The system scans the configured subnet for Modbus devices
   - Discovered devices are saved to `connected_devices.json`

2. **Data Collection**:
   - Establishes connections to discovered Modbus devices
   - Collects data from specified registers
   - Stores data in a local CSV file
   - Parameters collected:
     - Current
     - Voltage
     - Temperature
     - Power

3. **ThingsBoard Integration**:
   - Automatically creates devices in ThingsBoard
   - Generates and manages access tokens
   - Forwards data as telemetry
   - Maintains persistent device mapping

## Monitoring and Logging

- Main log file: `thingsboard_forwarder.log`
- CSV data file: `modbus_data.csv`
- Device tokens: `device_tokens.json`

## Error Handling

The system includes robust error handling for:
- Network connectivity issues
- Device communication failures
- ThingsBoard connection problems
- Automatic reconnection with configurable retries
- Data persistence during outages

## Customization

### Modbus Register Mapping

Modify the `PARAMETERS` dictionary in `Fetching_data.py`:

```python
PARAMETERS = {
    "current": [30031, 30032],
    "voltage": [30025, 30026],
    "temperature": [30027, 30028],
    "power": [30033, 30034]
}
```

### Polling Interval

Adjust `POLLING_INTERVAL` in `Fetching_data.py` (default: 5 seconds)

### Reconnection Settings

Modify in `Fetching_data.py`:
```python
MAX_RECONNECTION_ATTEMPTS = 3
RECONNECTION_DELAY = 5  # seconds
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Troubleshooting

1. **No devices found**:
   - Check network connectivity
   - Verify Modbus port (default: 502)
   - Confirm subnet configuration

2. **ThingsBoard connection issues**:
   - Verify ThingsBoard host address
   - Check credentials
   - Confirm ThingsBoard is running

3. **Data not updating**:
   - Check device connectivity
   - Verify register addresses
   - Review log files for errors


## Author

BHAVYA LABANA
RnD Engineer
PHDCOMM PVT LTD
