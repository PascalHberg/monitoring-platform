import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    3389: "RDP",
}


def _check_port(ip_address: str, port: int, service: str, timeout_sec: float) -> dict | None:
    """Returns a dict for an open port, otherwise None."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout_sec)
            sock.connect_ex((ip_address, port))
            if sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) != 0:
                return None
            return {
                "port": port,
                "service": service,
                "status": "Open",
            }
    except (OSError, socket.timeout):
        return None


def scan_target_ports(ip_address: str, ports: dict = COMMON_PORTS, timeout_sec: float = 0.5) -> dict:
    """
    Scans a target system for common TCP ports.
    Port checks are executed concurrently to avoid serial network delays.
    """
    open_ports = []
    max_workers = min(32, max(4, len(ports)))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_check_port, ip_address, port, service, timeout_sec)
            for port, service in ports.items()
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    return {
        "ip_address": ip_address,
        "scanned_ports": len(ports),
        "open_ports": open_ports,
    }
