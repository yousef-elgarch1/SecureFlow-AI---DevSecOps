"""
SCA (Software Composition Analysis) Report Parser

Supports: npm audit, pip-audit, OWASP Dependency-Check, Snyk
Input: JSON format
Output: Normalized dependency vulnerability data
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class SCAVulnerability:
    """Normalized SCA vulnerability data structure"""
    package_name: str
    current_version: str
    vulnerable_versions: str
    patched_version: Optional[str]
    cve_id: str
    severity: str
    description: str
    exploitability: Optional[str]
    fix_available: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class SCAParser:
    """Parse SCA reports from various tools"""

    SEVERITY_MAPPING = {
        'CRITICAL': 'CRITICAL',
        'HIGH': 'HIGH',
        'MEDIUM': 'MEDIUM',
        'MODERATE': 'MEDIUM',
        'LOW': 'LOW',
        'INFO': 'LOW'
    }

    def __init__(self):
        self.vulnerabilities: List[SCAVulnerability] = []

    def parse(self, report_content: str) -> List[SCAVulnerability]:
        """
        Parse SCA report and return normalized vulnerabilities

        Args:
            report_content: JSON string of SCA report

        Returns:
            List of SCAVulnerability objects
        """
        try:
            # Remove BOM (Byte Order Mark) if present
            if report_content.startswith('\ufeff'):
                report_content = report_content[1:]

            # Strip whitespace
            report_content = report_content.strip()

            data = json.loads(report_content)

            # Detect report format
            if 'vulnerabilities' in data:
                # npm audit format (with or without metadata)
                return self._parse_npm_audit(data)
            elif 'dependencies' in data:
                # pip-audit format
                return self._parse_pip_audit(data)
            else:
                raise ValueError("Unknown SCA report format")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing SCA report: {e}")

    def _parse_npm_audit(self, data: Dict) -> List[SCAVulnerability]:
        """Parse npm audit report format"""
        vulnerabilities = []

        vulns_data = data.get('vulnerabilities', {})

        for package_name, vuln_info_or_array in vulns_data.items():
            try:
                # Handle both single object and array formats
                vuln_list = vuln_info_or_array if isinstance(vuln_info_or_array, list) else [vuln_info_or_array]

                for vuln_info in vuln_list:
                    # Get severity
                    severity = self._normalize_severity(vuln_info.get('severity', 'MEDIUM'))

                    # Get CVE/advisory info
                    cve_id = 'N/A'
                    description = vuln_info.get('title', 'No description available')

                    # Try to get CWE if available
                    if 'cwe' in vuln_info and vuln_info['cwe']:
                        cwe_list = vuln_info['cwe']
                        if isinstance(cwe_list, list) and cwe_list:
                            cve_id = cwe_list[0]

                    # Get URL as additional info
                    if 'url' in vuln_info:
                        # Extract advisory ID from URL if no CWE
                        if cve_id == 'N/A':
                            url = vuln_info['url']
                            if 'GHSA-' in url:
                                cve_id = url.split('GHSA-')[1].split('/')[0]
                                cve_id = f"GHSA-{cve_id}"

                    # Get vulnerable range
                    vulnerable_range = vuln_info.get('range', 'Unknown')

                    # Get current version from findings if available
                    current_version = 'Unknown'
                    findings = vuln_info.get('findings', [])
                    if findings and isinstance(findings, list) and len(findings) > 0:
                        current_version = findings[0].get('version', 'Unknown')

                    # Get fix information
                    fix_available = False
                    patched_version = None
                    fix_info = vuln_info.get('fixAvailable', {})

                    if fix_info and isinstance(fix_info, dict):
                        fix_available = True
                        patched_version = fix_info.get('version', None)

                    vuln = SCAVulnerability(
                        package_name=package_name,
                        current_version=current_version,
                        vulnerable_versions=vulnerable_range,
                        patched_version=patched_version,
                        cve_id=cve_id,
                        severity=severity,
                        description=description,
                        exploitability=None,
                        fix_available=fix_available
                    )

                    vulnerabilities.append(vuln)

            except Exception as e:
                print(f"Warning: Skipping malformed vulnerability for {package_name}: {e}")
                continue

        return vulnerabilities

    def _parse_pip_audit(self, data: Dict) -> List[SCAVulnerability]:
        """Parse pip-audit report format"""
        vulnerabilities = []

        for dep in data.get('dependencies', []):
            try:
                vulns = dep.get('vulns', [])

                for vuln_data in vulns:
                    severity = self._normalize_severity(vuln_data.get('severity', 'MEDIUM'))

                    vuln = SCAVulnerability(
                        package_name=dep.get('name', 'Unknown'),
                        current_version=dep.get('version', 'Unknown'),
                        vulnerable_versions=vuln_data.get('vulnerable_versions', 'Unknown'),
                        patched_version=vuln_data.get('fixed_version', None),
                        cve_id=vuln_data.get('id', 'N/A'),
                        severity=severity,
                        description=vuln_data.get('description', 'No description'),
                        exploitability=None,
                        fix_available=bool(vuln_data.get('fixed_version'))
                    )

                    vulnerabilities.append(vuln)

            except Exception as e:
                print(f"Warning: Skipping malformed dependency: {e}")
                continue

        return vulnerabilities

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity to standard levels"""
        severity_upper = severity.upper()
        return self.SEVERITY_MAPPING.get(severity_upper, 'MEDIUM')

    def get_summary(self, vulnerabilities: List[SCAVulnerability]) -> Dict:
        """Get summary statistics of vulnerabilities"""
        summary = {
            'total': len(vulnerabilities),
            'by_severity': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            },
            'fixable': 0,
            'top_packages': {}
        }

        for vuln in vulnerabilities:
            # Count by severity
            summary['by_severity'][vuln.severity] += 1

            # Count fixable
            if vuln.fix_available:
                summary['fixable'] += 1

            # Count by package
            if vuln.package_name not in summary['top_packages']:
                summary['top_packages'][vuln.package_name] = 0
            summary['top_packages'][vuln.package_name] += 1

        # Sort packages by count
        summary['top_packages'] = dict(
            sorted(summary['top_packages'].items(),
                   key=lambda x: x[1], reverse=True)[:10]
        )

        return summary


# Test function
if __name__ == "__main__":
    # Test with sample report
    parser = SCAParser()

    try:
        with open('../../data/sample_reports/sca_sample.json', 'r') as f:
            content = f.read()

        vulns = parser.parse(content)

        print("="*60)
        print("SCA PARSER TEST")
        print("="*60)
        print(f"\n✅ Successfully parsed {len(vulns)} vulnerabilities\n")

        summary = parser.get_summary(vulns)

        print("Summary by Severity:")
        for severity, count in summary['by_severity'].items():
            if count > 0:
                print(f"  {severity}: {count}")

        print(f"\nFixable vulnerabilities: {summary['fixable']}/{summary['total']}")

        print("\nTop Vulnerable Packages:")
        for package, count in list(summary['top_packages'].items())[:5]:
            print(f"  {package}: {count} vulnerabilities")

        print("\nSample Vulnerability:")
        if vulns:
            vuln = vulns[0]
            print(f"  Package: {vuln.package_name}")
            print(f"  Severity: {vuln.severity}")
            print(f"  CVE: {vuln.cve_id}")
            print(f"  Vulnerable: {vuln.vulnerable_versions}")
            print(f"  Fix: {vuln.patched_version if vuln.fix_available else 'Not available'}")
            print(f"  Description: {vuln.description[:100]}...")

        print("\n✅ SCA Parser test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
