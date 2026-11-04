import socket

# Standard-Liste wichtiger Ports für Infrastruktur & Security
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    135: "RPC",
    139: "NetBIOS",
    443: "HTTPS",
    445: "SMB",
    3389: "RDP"
}

def scan_target_ports(ip_address: str, ports: dict = COMMON_PORTS, timeout_sec: float = 0.5) -> dict:
    """
    Scannt ein Zielsystem auf definierte TCP-Ports.
    """
    open_ports = []
    
    for port, service in ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout_sec)
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                open_ports.append({
                    "port": port,
                    "service": service,
                    "status": "Open"
                })
                
    return {
        "ip_address": ip_address,
        "scanned_ports": len(ports),
        "open_ports": open_ports
    }