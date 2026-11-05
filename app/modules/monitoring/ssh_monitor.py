import paramiko


def get_linux_system_metrics(ip_address: str, username: str, password: str = None, key_path: str = None, port: int = 22) -> dict:
    """
    Connects via SSH and queries CPU, RAM, and disk usage.
    Keeps the SSH session short-lived and adds explicit cleanup.
    """
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

        _, stdout_load, _ = client.exec_command("uptime", timeout=5)
        uptime_out = stdout_load.read().decode().strip()

        _, stdout_ram, _ = client.exec_command("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2}'", timeout=5)
        ram_usage = stdout_ram.read().decode().strip()

        _, stdout_disk, _ = client.exec_command("df -h / | awk 'NR==2{print $5}'", timeout=5)
        disk_usage = stdout_disk.read().decode().strip()

        return {
            "ip_address": ip_address,
            "status": "Connected",
            "metrics": {
                "uptime": uptime_out,
                "ram_usage": ram_usage,
                "disk_usage": disk_usage,
            },
        }
    except Exception as e:
        return {
            "ip_address": ip_address,
            "status": "Error",
            "error": str(e),
        }
    finally:
        client.close()
