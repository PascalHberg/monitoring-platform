# Infrastructure & Security Monitoring Platform

Eine selbst entwickelte, modulare Monitoring- und Compliance-Plattform zur automatisierten Überwachung von IT-Infrastrukturen (Linux, Windows, Container, Netzwerkgeräte) und zur Erstellung von Sicherheitsberichten.

## Systemarchitektur & Module

Die Anwendung ist als **modularer Monolith** strukturiert:

- **Network Discovery (`app/modules/discovery/`):** ICMP-Ping-Checks zur Erreichbarkeitsprüfung im Subnetz.
- **Security & Compliance (`app/modules/security/`):** Socket-basiertes Port-Scanning und automatisierte Härtungsprüfungen (angelehnt an CIS Benchmarks / BSI-Grundschutz).
- **Infrastructure Monitoring (`app/modules/monitoring/`):** 
  - Linux System-Metrics (CPU, RAM, Disk) via `Paramiko` (SSH).
  - Container-Monitoring über das Docker SDK.
- **Reporting (`app/modules/reporting/`):** Export-Modul zur automatisierten Erstellung von CSV-Audit-Berichten.
- **Database (`app/database/`):** SQLAlchemy ORM mit SQLite-Persistenz für inventarisierte Hosts.
- **Frontend (`app/templates/`):** Single-Page Dashboard auf Basis von HTML5, CSS3 und JavaScript (Fetch API).

## Tech-Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn
- **ORM & Datenbank:** SQLAlchemy, SQLite
- **Netzwerk & Security:** `subprocess` (Ping), `socket` (Port-Scan), `paramiko` (SSH), `docker` SDK
- **Containerisierung:** Docker, Docker Compose

## Schnellanleitung (Docker Deployment)

1. Repository klonen:
   ```bash
   git clone [https://github.com/PascalHberg/monitoring-platform.git](https://github.com/PascalHberg/monitoring-platform.git)
   cd monitoring-platform
