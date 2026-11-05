import platform
import subprocess


def check_host_availability(ip_address: str, timeout_ms: int = 1000) -> dict:
    """
    Checks whether an IP is reachable via ICMP ping.
    Uses a single OS detection and a real timeout to avoid hanging calls.
    """
    is_windows = platform.system().lower() == "windows"
    param = "-n" if is_windows else "-c"
    timeout_param = "-w" if is_windows else "-W"

    if is_windows:
        timeout_val = str(max(1, timeout_ms))
    else:
        timeout_val = str(max(1, timeout_ms // 1000))

    command = ["ping", param, "1", timeout_param, timeout_val, ip_address]

    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",
            timeout=max(1, timeout_ms / 1000),
            check=False,
        )
        return {
            "ip_address": ip_address,
            "status": "Online" if completed.returncode == 0 else "Offline",
            "returncode": completed.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "ip_address": ip_address,
            "status": "Offline",
            "returncode": 1,
        }
    except Exception as e:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error": str(e),
        }
