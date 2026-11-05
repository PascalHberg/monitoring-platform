from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.connection import Base, engine, get_db
from app.database.models import Host
from app.modules.discovery.ping import check_host_availability
from app.modules.monitoring.docker_monitor import get_docker_containers
from app.modules.monitoring.ssh_monitor import get_linux_system_metrics
from app.modules.reporting.exporter import generate_hosts_csv_report
from app.modules.security.compliance import run_basic_compliance_check
from app.modules.security.port_scan import scan_target_ports
from app.security import require_api_key

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Infrastructure & Security Monitoring Platform")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/v1/hosts", dependencies=[Depends(require_api_key)])
def get_hosts(db: Session = Depends(get_db)):
    hosts = db.query(Host).all()
    return {"hosts": hosts, "generated_at": datetime.now(timezone.utc).isoformat()}


@app.post("/api/v1/scan/ping", dependencies=[Depends(require_api_key)])
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
    return {"scan_result": result, "db_host": host, "checked_at": result["checked_at"]}


@app.post("/api/v1/scan/ports", dependencies=[Depends(require_api_key)])
def scan_ports_endpoint(ip_address: str):
    result = scan_target_ports(ip_address)
    return {"port_scan_result": result, "checked_at": result["checked_at"]}


@app.post("/api/v1/monitor/linux", dependencies=[Depends(require_api_key)])
def monitor_linux_host(ip_address: str, username: str, password: str = None):
    metrics = get_linux_system_metrics(ip_address=ip_address, username=username, password=password)
    return {"ssh_metrics": metrics, "checked_at": metrics["checked_at"]}


@app.get("/api/v1/monitor/docker", dependencies=[Depends(require_api_key)])
def monitor_docker_containers(base_url: str = None):
    result = get_docker_containers(base_url=base_url)
    return {"docker_monitoring": result, "checked_at": result["checked_at"]}


@app.post("/api/v1/security/compliance", dependencies=[Depends(require_api_key)])
def check_system_compliance(ip_address: str):
    result = run_basic_compliance_check(ip_address)
    return {"compliance_result": result, "checked_at": result["checked_at"]}


@app.get("/api/v1/reporting/export/csv", dependencies=[Depends(require_api_key)])
def export_hosts_csv(db: Session = Depends(get_db)):
    csv_file = generate_hosts_csv_report(db)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return StreamingResponse(
        iter([csv_file.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=hosts_audit_report_{timestamp}.csv",
            "X-Generated-At": datetime.now(timezone.utc).isoformat(),
        },
    )
