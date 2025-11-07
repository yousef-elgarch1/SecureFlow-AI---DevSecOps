"""
Nuclei DAST Scanner - Tier 1
Fast, template-based vulnerability scanning for live URLs.

Installation:
Windows: choco install nuclei
    OR download from: https://github.com/projectdiscovery/nuclei/releases
Linux/Mac: go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
"""

import os
import subprocess
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NucleiScanner:
    """Wrapper for Nuclei DAST scanning."""

    def __init__(self):
        self.nuclei_path = self._find_nuclei()

    def _find_nuclei(self) -> Optional[str]:
        """Find Nuclei executable in system PATH."""
        # Try to find in PATH
        nuclei_path = shutil.which("nuclei")
        if nuclei_path:
            logger.info(f"Found Nuclei at: {nuclei_path}")
            return nuclei_path

        # Try common Windows locations
        common_paths = [
            r"C:\ProgramData\chocolatey\bin\nuclei.exe",
            r"C:\Program Files\nuclei\nuclei.exe",
            os.path.expanduser(r"~\go\bin\nuclei.exe"),
        ]

        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found Nuclei at: {path}")
                return path

        logger.warning("Nuclei not found in PATH or common locations")
        return None

    def scan(
        self,
        target_url: str,
        severity: List[str] = None,
        tags: List[str] = None,
        templates: List[str] = None,
        timeout: int = 300
    ) -> Dict:
        """
        Scan a live URL with Nuclei.

        Args:
            target_url: Target URL to scan (e.g., https://example.com)
            severity: List of severities to scan for (critical, high, medium, low, info)
            tags: List of tags to filter templates (e.g., owasp, cve, xss)
            templates: List of specific template paths
            timeout: Scan timeout in seconds (default: 300)

        Returns:
            Dictionary with scan results in our format
        """
        if not self.nuclei_path:
            raise Exception(
                "Nuclei not installed. "
                "Install with: choco install nuclei (Windows) or "
                "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
            )

        try:
            logger.info(f"Starting Nuclei scan on {target_url}...")

            # Default to important severities if not specified
            if severity is None:
                severity = ["critical", "high", "medium"]

            # Build command
            cmd = [
                self.nuclei_path,
                "-u", target_url,
                "-jsonl",  # JSON Lines output
                "-silent",  # Only show findings
                "-severity", ",".join(severity),
            ]

            # Add tags if specified
            if tags:
                cmd.extend(["-tags", ",".join(tags)])

            # Add specific templates if specified
            if templates:
                for template in templates:
                    cmd.extend(["-t", template])

            # Update templates before scanning
            logger.info("Updating Nuclei templates...")
            subprocess.run(
                [self.nuclei_path, "-update-templates"],
                capture_output=True,
                timeout=60
            )

            logger.info(f"Running Nuclei command: {' '.join(cmd)}")

            # Run Nuclei scan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )

            logger.info(f"Nuclei return code: {result.returncode}")
            logger.info(f"Nuclei stderr: {result.stderr[:500] if result.stderr else 'None'}")

            # Parse JSONL output (one JSON object per line)
            vulnerabilities = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if not line.strip():
                        continue
                    try:
                        finding = json.loads(line)

                        # Map Nuclei output to our format
                        vuln = {
                            "title": finding.get("info", {}).get("name", "Unknown vulnerability"),
                            "severity": finding.get("info", {}).get("severity", "MEDIUM").upper(),
                            "description": finding.get("info", {}).get("description", "No description"),
                            "url": finding.get("matched-at", target_url),
                            "template_id": finding.get("template-id", ""),
                            "matcher_name": finding.get("matcher-name", ""),
                            "extracted_results": finding.get("extracted-results", []),
                            "curl_command": finding.get("curl-command", ""),
                            "tags": finding.get("info", {}).get("tags", []),
                            "cwe": finding.get("info", {}).get("classification", {}).get("cwe-id", []),
                            "cve": finding.get("info", {}).get("classification", {}).get("cve-id", []),
                            "recommendation": finding.get("info", {}).get("remediation", "Review and fix the vulnerability"),
                            "reference": finding.get("info", {}).get("reference", []),
                        }
                        vulnerabilities.append(vuln)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse Nuclei output line: {line[:100]} - {e}")
                        continue

            logger.info(f"Nuclei found {len(vulnerabilities)} vulnerabilities")

            return {
                "tool": "Nuclei",
                "scan_type": "DAST",
                "target": target_url,
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": vulnerabilities,
                "summary": {
                    "total": len(vulnerabilities),
                    "critical": len([v for v in vulnerabilities if v["severity"] == "CRITICAL"]),
                    "high": len([v for v in vulnerabilities if v["severity"] == "HIGH"]),
                    "medium": len([v for v in vulnerabilities if v["severity"] == "MEDIUM"]),
                    "low": len([v for v in vulnerabilities if v["severity"] == "LOW"]),
                }
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Nuclei scan timeout (>{timeout}s)")
            return {
                "tool": "Nuclei",
                "scan_type": "DAST",
                "target": target_url,
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                "error": f"Scan timeout (>{timeout}s)"
            }
        except Exception as e:
            logger.error(f"Nuclei scan error: {e}", exc_info=True)
            return {
                "tool": "Nuclei",
                "scan_type": "DAST",
                "target": target_url,
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                "error": str(e)
            }


def scan_url_with_nuclei(
    target_url: str,
    severity: List[str] = None,
    tags: List[str] = None
) -> Dict:
    """
    Convenience function to scan a URL with Nuclei.

    Args:
        target_url: URL to scan
        severity: Severity levels to scan for
        tags: Template tags to use

    Returns:
        Scan results dictionary
    """
    scanner = NucleiScanner()
    return scanner.scan(target_url, severity=severity, tags=tags)
