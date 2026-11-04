import subprocess
import platform

def check_host_availability(ip_address: str, timeout_ms: int = 1000) -> dict:
    """
    Prüft die Erreichbarkeit einer IP-Adresse via ICMP Ping.
    Funktioniert plattformübergreifend auf Windows und Linux.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    timeout_val = str(timeout_ms) if platform.system().lower() == "windows" else str(max(1, timeout_ms // 1000))

    command = ["ping", param, "1", timeout_param, timeout_val, ip_address]

    try:
        # errors="ignore" verhindert UnicodeDecodeError bei deutschen Windows-Ping-Texten
        output = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            errors="ignore"
        )
        is_online = (output.returncode == 0)
        
        return {
            "ip_address": ip_address,
            "status": "Online" if is_online else "Offline",
            "returncode": output.returncode
        }
    except Exception as e:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error": str(e)
        }