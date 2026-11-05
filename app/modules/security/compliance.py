from datetime import datetime, timezone

from app.modules.security.port_scan import scan_target_ports


def run_basic_compliance_check(ip_address: str) -> dict:
    """Run basic checks based on a small set of exposed TCP ports."""
    checked_at = datetime.now(timezone.utc).isoformat()
    scan_result = scan_target_ports(ip_address)
    if scan_result.get("status") == "Error":
        return {
            "ip_address": ip_address,
            "compliance_score": None,
            "status": "ERROR",
            "total_findings": 0,
            "findings": [],
            "error_code": scan_result.get("error_code", "PORT_SCAN_FAILED"),
            "error": scan_result.get("error", "The required port check failed."),
            "checked_at": checked_at,
        }

    open_ports = [item["port"] for item in scan_result.get("open_ports", [])]
    findings = []
    compliance_score = 100

    if 21 in open_ports:
        findings.append({
            "rule_id": "SEC-001",
            "severity": "HIGH",
            "port": 21,
            "description": "Unencrypted FTP is active. Prefer SFTP or FTPS.",
        })
        compliance_score -= 30

    if 80 in open_ports and 443 not in open_ports:
        findings.append({
            "rule_id": "SEC-002",
            "severity": "MEDIUM",
            "port": 80,
            "description": "HTTP is active without HTTPS. Enable TLS where appropriate.",
        })
        compliance_score -= 20

    if 3389 in open_ports:
        findings.append({
            "rule_id": "SEC-003",
            "severity": "MEDIUM",
            "port": 3389,
            "description": "RDP is reachable. Restrict access through a VPN or bastion host.",
        })
        compliance_score -= 15

    if 445 in open_ports:
        findings.append({
            "rule_id": "SEC-004",
            "severity": "INFO",
            "port": 445,
            "description": "SMB is active. Verify that SMBv1 is disabled.",
        })
        compliance_score -= 5

    score_status = "PASSED" if compliance_score >= 80 else "WARNING" if compliance_score >= 50 else "FAILED"
    return {
        "ip_address": ip_address,
        "compliance_score": max(0, compliance_score),
        "status": score_status,
        "total_findings": len(findings),
        "findings": findings,
        "error_code": None,
        "error": None,
        "checked_at": checked_at,
    }
