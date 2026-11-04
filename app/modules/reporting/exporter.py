import csv
import io
from sqlalchemy.orm import Session
from app.database.models import Host

def generate_hosts_csv_report(db: Session) -> io.StringIO:
    """
    Liest alle geschriebenen Hosts aus der Datenbank aus 
    und generiert einen CSV-Report im Speicher.
    """
    hosts = db.query(Host).all()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # CSV-Header schreiben
    writer.writerow(["ID", "IP-Adresse", "Hostname", "OS-Typ", "Status", "Zuletzt gesehen"])
    
    # Datenzeilen schreiben
    for host in hosts:
        writer.writerow([
            host.id,
            host.ip_address,
            host.hostname,
            host.os_type,
            host.status,
            host.last_seen.strftime("%Y-%m-%d %H:%M:%S") if host.last_seen else "N/A"
        ])
        
    output.seek(0)
    return output