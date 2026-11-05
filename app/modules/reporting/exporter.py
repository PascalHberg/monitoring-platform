import io

import csv
from sqlalchemy.orm import Session

from app.database.models import Host


def generate_hosts_csv_report(db: Session) -> io.StringIO:
    """
    Reads all hosts from the DB and generates a CSV report in memory.
    This keeps the export simple while avoiding extra DB roundtrips.
    """
    hosts = db.query(Host).order_by(Host.last_seen.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow(["ID", "IP-Adresse", "Hostname", "OS-Typ", "Status", "Zuletzt gesehen"])

    for host in hosts:
        writer.writerow([
            host.id,
            host.ip_address,
            host.hostname,
            host.os_type,
            host.status,
            host.last_seen.strftime("%Y-%m-%d %H:%M:%S") if host.last_seen else "N/A",
        ])

    output.seek(0)
    return output
