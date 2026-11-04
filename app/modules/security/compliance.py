from app.modules.security.port_scan import scan_target_ports

def run_basic_compliance_check(ip_address: str) -> dict:
    """
    Führt Basis-Härtungs- und Compliance-Prüfungen auf Basis offener Dienste durch.
    """
    # Scanne relevante administrative und unsichere Ports
    scan_result = scan_target_ports(ip_address)
    open_ports = [item["port"] for item in scan_result.get("open_ports", [])]
    
    findings = []
    compliance_score = 100

    # Regel 1: Unsichere Klartext-Protokolle (FTP / HTTP)
    if 21 in open_ports:
        findings.append({
            "rule_id": "SEC-001",
            "severity": "HIGH",
            "description": "Unverschlüsseltes FTP-Protokoll (Port 21) aktiv. Empfehlung: SFTP/FTPS nutzen."
        })
        compliance_score -= 30

    if 80 in open_ports and 443 not in open_ports:
        findings.append({
            "rule_id": "SEC-002",
            "severity": "MEDIUM",
            "description": "HTTP (Port 80) aktiv ohne HTTPS (Port 443). Empfehlung: TLS-Verschlüsselung aktivieren."
        })
        compliance_score -= 20

    # Regel 2: Exponierte Management-Schnittstellen (SSH / RDP / SMB)
    if 3389 in open_ports:
        findings.append({
            "rule_id": "SEC-003",
            "severity": "MEDIUM",
            "description": "RDP (Port 3389) direkt erreichbar. Empfehlung: Zugriff über VPN oder Bastion-Host einschränken."
        })
        compliance_score -= 15

    if 445 in open_ports:
        findings.append({
            "rule_id": "SEC-004",
            "severity": "INFO",
            "description": "SMB-Freigabe (Port 445) aktiv. Stellen Sie sicher, dass SMBv1 deaktiviert ist."
        })
        compliance_score -= 5

    # Status auswerten
    score_status = "PASSED" if compliance_score >= 80 else "WARNING" if compliance_score >= 50 else "FAILED"

    return {
        "ip_address": ip_address,
        "compliance_score": max(0, compliance_score),
        "status": score_status,
        "total_findings": len(findings),
        "findings": findings
    }