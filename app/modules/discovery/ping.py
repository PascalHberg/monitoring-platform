from datetime import datetime, timezone
import ipaddress
import platform
import subprocess


def _checked_at() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_host_availability(ip_address: str, timeout_ms: int = 1000) -> dict:
    """Check one IP address with ICMP ping and return a timestamped result."""
    checked_at = _checked_at()
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error_code": "INVALID_IP_ADDRESS",
            "error": "Provide a valid IPv4 or IPv6 address.",
            "checked_at": checked_at,
        }

    is_windows = platform.system().lower() == "windows"
    param = "-n" if is_windows else "-c"
    timeout_param = "-w" if is_windows else "-W"
    timeout_val = str(timeout_ms) if is_windows else str(max(1, timeout_ms // 1000))
    command = ["ping", param, "1", timeout_param, timeout_val, ip_address]

    try:
        output = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",
            timeout=max(1, timeout_ms / 1000 + 1),
            check=False,
        )
        is_online = output.returncode == 0
        return {
            "ip_address": ip_address,
            "status": "Online" if is_online else "Offline",
            "returncode": output.returncode,
            "error_code": None if is_online else "HOST_UNREACHABLE",
            "error": None if is_online else "No ping response was received; ICMP may be blocked.",
            "checked_at": checked_at,
        }
    except subprocess.TimeoutExpired:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error_code": "PING_TIMEOUT",
            "error": "The ping process exceeded its time limit.",
            "checked_at": checked_at,
        }
    except OSError:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error_code": "PING_EXECUTION_FAILED",
            "error": "The system ping command could not be started.",
            "checked_at": checked_at,
        }
