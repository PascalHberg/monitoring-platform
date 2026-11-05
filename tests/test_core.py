import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.security import require_api_key
from app.modules.discovery.ping import check_host_availability
from app.modules.security.compliance import run_basic_compliance_check
from app.modules.security.port_scan import scan_target_ports


class ApiSecurityTests(unittest.TestCase):
    @patch.dict(os.environ, {"API_TOKEN": "test-secret"})
    def test_missing_or_wrong_key_is_rejected(self):
        for supplied in (None, "wrong"):
            with self.subTest(supplied=supplied), self.assertRaises(HTTPException) as raised:
                require_api_key(supplied)
            self.assertEqual(raised.exception.status_code, 401)
            self.assertEqual(raised.exception.detail["code"], "INVALID_API_TOKEN")

    @patch.dict(os.environ, {"API_TOKEN": "test-secret"})
    def test_correct_key_is_accepted(self):
        self.assertIsNone(require_api_key("test-secret"))

    @patch.dict(os.environ, {}, clear=True)
    def test_unconfigured_key_fails_closed(self):
        with self.assertRaises(HTTPException) as raised:
            require_api_key("anything")
        self.assertEqual(raised.exception.status_code, 503)
        self.assertEqual(raised.exception.detail["code"], "API_AUTH_NOT_CONFIGURED")


class MonitoringFunctionTests(unittest.TestCase):
    @patch("app.modules.discovery.ping.subprocess.run")
    def test_ping_success_has_timestamp_and_status(self, run):
        run.return_value.returncode = 0
        result = check_host_availability("127.0.0.1")
        self.assertEqual(result["status"], "Online")
        self.assertIsNotNone(result["checked_at"])
        run.assert_called_once()

    def test_ping_rejects_invalid_ip_with_clear_reason(self):
        result = check_host_availability("not-an-ip")
        self.assertEqual(result["error_code"], "INVALID_IP_ADDRESS")
        self.assertIn("valid IPv4 or IPv6", result["error"])
        self.assertIsNotNone(result["checked_at"])

    def test_port_scan_rejects_invalid_ip(self):
        result = scan_target_ports("bad-address")
        self.assertEqual(result["error_code"], "INVALID_IP_ADDRESS")
        self.assertEqual(result["open_ports"], [])

    @patch("app.modules.security.compliance.scan_target_ports")
    def test_compliance_reports_findings_and_timestamp(self, scan):
        scan.return_value = {
            "status": "Success",
            "open_ports": [{"port": 21, "service": "FTP", "status": "Open"}],
        }
        result = run_basic_compliance_check("192.0.2.1")
        self.assertEqual(result["status"], "WARNING")
        self.assertEqual(result["findings"][0]["rule_id"], "SEC-001")
        self.assertEqual(result["findings"][0]["port"], 21)
        self.assertIsNotNone(result["checked_at"])

    @patch("app.modules.security.compliance.scan_target_ports")
    def test_compliance_exposes_port_scan_failure(self, scan):
        scan.return_value = {
            "status": "Error",
            "error_code": "PORT_SCAN_FAILED",
            "error": "The TCP port check could not be completed.",
        }
        result = run_basic_compliance_check("192.0.2.1")
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "PORT_SCAN_FAILED")
        self.assertIsNotNone(result["checked_at"])


if __name__ == "__main__":
    unittest.main()
