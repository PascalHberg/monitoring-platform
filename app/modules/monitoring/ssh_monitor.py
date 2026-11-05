from datetime import datetime, timezone

import paramiko


def get_linux_system_metrics(ip_address: str, username: str, password: str = None, key_path: str = None, port: int = 22) -> dict:
    """Connect over SSH and collect basic Linux metrics."""
    checked_at = datetime.now(timezone.utc).isoformat()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=ip_address,
            port=port,
            username=username,
            password=password,
            key_filename=key_path,
            timeout=5,
        )
        _, stdout_load, _ = client.exec_command("uptime")
        uptime_out = stdout_load.read().decode().strip()
        _, stdout_ram, _ = client.exec_command("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2}'")
        ram_usage = stdout_ram.read().decode().strip()
        _, stdout_disk, _ = client.exec_command("df -h / | awk 'NR==2{print $5}'")
        disk_usage = stdout_disk.read().decode().strip()
        return {
            "ip_address": ip_address,
            "status": "Connected",
            "metrics": {"uptime": uptime_out, "ram_usage": ram_usage, "disk_usage": disk_usage},
            "error_code": None,
            "error": None,
            "checked_at": checked_at,
        }
    except paramiko.AuthenticationException:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error_code": "SSH_AUTHENTICATION_FAILED",
            "error": "SSH authentication failed; check the username and credentials.",
            "checked_at": checked_at,
        }
    except (paramiko.SSHException, OSError, TimeoutError):
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error_code": "SSH_CONNECTION_FAILED",
            "error": "Could not establish or use the SSH connection.",
            "checked_at": checked_at,
        }
    finally:
        client.close()
