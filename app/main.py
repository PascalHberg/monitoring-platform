from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import engine, Base, get_db
from app.database.models import Host
from app.modules.discovery.ping import check_host_availability
from app.modules.security.port_scan import scan_target_ports
from app.modules.monitoring.ssh_monitor import get_linux_system_metrics
from app.modules.monitoring.docker_monitor import get_docker_containers
from app.modules.security.compliance import run_basic_compliance_check
from fastapi.responses import StreamingResponse
from app.modules.reporting.exporter import generate_hosts_csv_report

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Infrastructure & Security Monitoring Platform")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request):
    """
    Rendert das HTML Web-Dashboard.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/v1/hosts")
def get_hosts(db: Session = Depends(get_db)):
    hosts = db.query(Host).all()
    return {"hosts": hosts}

@app.post("/api/v1/scan/ping")
def scan_single_host(ip_address: str, db: Session = Depends(get_db)):
    result = check_host_availability(ip_address)
    host = db.query(Host).filter(Host.ip_address == ip_address).first()
    if not host:
        host = Host(ip_address=ip_address, hostname=ip_address, status=result["status"])
        db.add(host)
    else:
        host.status = result["status"]
    
    db.commit()
    db.refresh(host)
    return {"scan_result": result, "db_host": host}

@app.post("/api/v1/scan/ports")
def scan_ports_endpoint(ip_address: str):
    result = scan_target_ports(ip_address)
    return {"port_scan_result": result}

@app.post("/api/v1/monitor/linux")
def monitor_linux_host(ip_address: str, username: str, password: str = None):
    metrics = get_linux_system_metrics(ip_address=ip_address, username=username, password=password)
    return {"ssh_metrics": metrics}

@app.get("/api/v1/monitor/docker")
def monitor_docker_containers(base_url: str = None):
    result = get_docker_containers(base_url=base_url)
    return {"docker_monitoring": result}

@app.post("/api/v1/security/compliance")
def check_system_compliance(ip_address: str):
    result = run_basic_compliance_check(ip_address)
    return {"compliance_result": result}

@app.get("/api/v1/reporting/export/csv")
def export_hosts_csv(db: Session = Depends(get_db)):
    """
    Generiert und liefert einen CSV-Audit-Bericht aller erfassten Hosts.
    """
    csv_file = generate_hosts_csv_report(db)
    return StreamingResponse(
        iter([csv_file.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=hosts_audit_report.csv"}
    )