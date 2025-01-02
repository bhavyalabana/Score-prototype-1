import socket

def check_modbus_device(ip, port, timeout, retries):
    """Check if a Modbus device is reachable on the given IP and port."""
    try:
        for _ in range(retries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((ip, port))
                if result == 0:
                    return True
        return False
    except Exception as e:
        print(f"Error checking Modbus device at {ip}: {e}")
        return False
