from datetime import datetime, timezone
import ipaddress
import socket

# A deliberately small set of common TCP ports; this is not a full port scan.
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    135: "RPC",
    139: "NetBIOS",
    443: "HTTPS",
    445: "SMB",
    3389: "RDP",
}


def scan_target_ports(ip_address: str, ports: dict = COMMON_PORTS, timeout_sec: float = 0.5) -> dict:
    """Check the configured TCP ports on one IP address."""
    checked_at = datetime.now(timezone.utc).isoformat()
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return {
            "ip_address": ip_address,
            "scanned_ports": 0,
            "open_ports": [],
            "status": "Error",
            "error_code": "INVALID_IP_ADDRESS",
            "error": "Provide a valid IPv4 or IPv6 address.",
            "checked_at": checked_at,
        }

    open_ports = []
    try:
        for port, service in ports.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout_sec)
                if sock.connect_ex((ip_address, port)) == 0:
                    open_ports.append({"port": port, "service": service, "status": "Open"})
    except OSError:
        return {
            "ip_address": ip_address,
            "scanned_ports": len(ports),
            "open_ports": open_ports,
            "status": "Error",
            "error_code": "PORT_SCAN_FAILED",
            "error": "The TCP port check could not be completed.",
            "checked_at": checked_at,
        }

    return {
        "ip_address": ip_address,
        "scanned_ports": len(ports),
        "open_ports": open_ports,
        "status": "Success",
        "error_code": None,
        "error": None,
        "checked_at": checked_at,
    }
