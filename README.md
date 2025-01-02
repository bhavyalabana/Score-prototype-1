# Score-prototype-1
# Modbus Network Integration

## Overview
This project provides a modular framework for:
- Scanning a network for Modbus-compatible devices.
- Fetching data from Modbus registers.
- Sending the data to ThingsBoard for visualization and control.

The setup supports additional protocols such as OPC and MQTT, making it extensible for future use cases.

---

## Features
- **Network Scanning**: Identifies Modbus devices on a specified subnet.
- **Data Fetching**: Reads specified registers (`current`, `voltage`, `temperature`, `power`) and stores the data locally in a CSV file.
- **ThingsBoard Integration**: Dynamically creates or updates devices in ThingsBoard and sends telemetry data.
- **Protocol Modularity**: Additional protocols can be supported by adding functions in the `protocol_functions.py` file.

---

## Repository Structure
```plaintext
📂 scripts
    ├── modbus_network_scan_script.py  # Scans the network for Modbus devices
    ├── Fetching_data.py               # Fetches data from Modbus devices
    ├── Data_to_thingsboard.py         # Forwards data to ThingsBoard
    ├── protocol_functions.py          # Contains protocol-specific functions
📂 config
    ├── config.json                    # Configuration for scanning and fetching
📂 data
    ├── connected_devices.json         # Stores discovered devices
    ├── modbus_data.csv                # Stores fetched data
📂 logs
    ├── thingsboard_forwarder.log      # Logging for ThingsBoard integration
README.md                              # Documentation for the project
requirements.txt                       # Python dependencies
LICENSE                                # Project license
```

---

## Prerequisites
- Python 3.8 or higher
- ThingsBoard Community Edition installed
- Modbus-compatible devices on the network

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Modbus-Network-Integration.git
   cd Modbus-Network-Integration
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings**
   - Update `config/config.json` with your network and Modbus settings.

4. **Run the Scripts**
   - **Network Scan**: Identify Modbus devices on the subnet.
     ```bash
     python scripts/modbus_network_scan_script.py
     ```
   - **Fetch Data**: Collect data from connected devices.
     ```bash
     python scripts/Fetching_data.py
     ```
   - **Send to ThingsBoard**: Forward data to ThingsBoard.
     ```bash
     python scripts/Data_to_thingsboard.py
     ```

---

## Configuration File (`config/config.json`)
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

---

## Extending the Framework
- **Adding a Protocol**:
  1. Define a function in `protocol_functions.py` to check device compatibility.
  2. Include the protocol in the `config.json` under the `protocols` list.

- **Custom Data Fetching**:
  - Modify `Fetching_data.py` to include additional parameters or logic.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contributions
Contributions are welcome! Please open an issue or submit a pull request to improve the project.

---

## Acknowledgments
- [ThingsBoard Community Edition](https://thingsboard.io/)
- [Pymodbus Library](https://github.com/riptideio/pymodbus)

