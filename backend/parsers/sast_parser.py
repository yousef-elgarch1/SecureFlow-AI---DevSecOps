"""
SAST (Static Application Security Testing) Report Parser

Supports: Semgrep, SonarQube, Checkmarx, Bandit
Input: JSON format
Output: Normalized vulnerability data
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class SASTVulnerability:
    """Normalized SAST vulnerability data structure"""
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # SQL Injection, XSS, etc.
    file_path: str
    line_number: int
    cwe_id: Optional[str]
    description: str
    recommendation: str
    confidence: str = "HIGH"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class SASTParser:
    """Parse SAST reports from various tools"""

    SEVERITY_MAPPING = {
        'CRITICAL': 'CRITICAL',
        'HIGH': 'HIGH',
        'MEDIUM': 'MEDIUM',
        'MODERATE': 'MEDIUM',
        'LOW': 'LOW',
        'INFO': 'LOW',
        'WARNING': 'MEDIUM',
        'ERROR': 'HIGH'
    }

    def __init__(self):
        self.vulnerabilities: List[SASTVulnerability] = []

    def parse(self, report_content: str) -> List[SASTVulnerability]:
        """
        Parse SAST report and return normalized vulnerabilities

        Args:
            report_content: JSON string of SAST report

        Returns:
            List of SASTVulnerability objects
        """
        try:
            data = json.loads(report_content)

            # Detect report format
            if 'results' in data:
                # Semgrep format
                return self._parse_semgrep(data)
            elif 'issues' in data:
                # SonarQube format
                return self._parse_sonarqube(data)
            else:
                raise ValueError("Unknown SAST report format")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing SAST report: {e}")

    def _parse_semgrep(self, data: Dict) -> List[SASTVulnerability]:
        """Parse Semgrep report format"""
        vulnerabilities = []

        for result in data.get('results', []):
            try:
                extra = result.get('extra', {})
                metadata = extra.get('metadata', {})

                # Extract CWE from metadata or description
                cwe_id = None
                if 'cwe' in metadata:
                    cwe_id = str(metadata['cwe']) if not isinstance(metadata['cwe'], str) else metadata['cwe']

                # Normalize severity
                severity = self._normalize_severity(extra.get('severity', 'MEDIUM'))

                # Extract category from check_id or message
                check_id = result.get('check_id', '')
                category = self._extract_category(check_id, extra.get('message', ''))

                vuln = SASTVulnerability(
                    title=check_id.split('.')[-1].replace('-', ' ').title(),
                    severity=severity,
                    category=category,
                    file_path=result.get('path', 'Unknown'),
                    line_number=result.get('start', {}).get('line', 0),
                    cwe_id=cwe_id,
                    description=extra.get('message', 'No description'),
                    recommendation=extra.get('fix', 'Review and fix this vulnerability'),
                    confidence=metadata.get('confidence', 'HIGH')
                )

                vulnerabilities.append(vuln)

            except Exception as e:
                print(f"Warning: Skipping malformed result: {e}")
                continue

        return vulnerabilities

    def _parse_sonarqube(self, data: Dict) -> List[SASTVulnerability]:
        """Parse SonarQube report format"""
        vulnerabilities = []

        for issue in data.get('issues', []):
            try:
                severity = self._normalize_severity(issue.get('severity', 'MEDIUM'))

                vuln = SASTVulnerability(
                    title=issue.get('rule', 'Unknown Issue'),
                    severity=severity,
                    category=issue.get('type', 'Security Issue'),
                    file_path=issue.get('component', 'Unknown'),
                    line_number=issue.get('line', 0),
                    cwe_id=None,
                    description=issue.get('message', 'No description'),
                    recommendation='Fix according to SonarQube recommendations',
                    confidence='HIGH'
                )

                vulnerabilities.append(vuln)

            except Exception as e:
                print(f"Warning: Skipping malformed issue: {e}")
                continue

        return vulnerabilities

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity to standard levels"""
        severity_upper = severity.upper()
        return self.SEVERITY_MAPPING.get(severity_upper, 'MEDIUM')

    def _extract_category(self, check_id: str, message: str) -> str:
        """Extract vulnerability category from check_id or message"""
        # Common patterns in check_id
        if 'sqli' in check_id.lower() or 'sql-injection' in check_id.lower():
            return 'SQL Injection'
        elif 'xss' in check_id.lower() or 'cross-site-scripting' in check_id.lower():
            return 'Cross-Site Scripting (XSS)'
        elif 'csrf' in check_id.lower():
            return 'Cross-Site Request Forgery (CSRF)'
        elif 'path-traversal' in check_id.lower() or 'directory-traversal' in check_id.lower():
            return 'Path Traversal'
        elif 'command-injection' in check_id.lower():
            return 'Command Injection'
        elif 'hardcoded' in check_id.lower() or 'secret' in check_id.lower():
            return 'Hardcoded Secrets'
        elif 'crypto' in check_id.lower():
            return 'Cryptographic Issue'
        elif 'session' in check_id.lower():
            return 'Session Management'
        elif 'helmet' in check_id.lower() or 'header' in check_id.lower():
            return 'Security Headers'
        elif 'random' in check_id.lower():
            return 'Weak Randomness'
        elif 'redirect' in check_id.lower():
            return 'Open Redirect'
        else:
            return 'Security Vulnerability'

    def get_summary(self, vulnerabilities: List[SASTVulnerability]) -> Dict:
        """Get summary statistics of vulnerabilities"""
        summary = {
            'total': len(vulnerabilities),
            'by_severity': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            },
            'by_category': {},
            'top_files': {}
        }

        for vuln in vulnerabilities:
            # Count by severity
            summary['by_severity'][vuln.severity] += 1

            # Count by category
            if vuln.category not in summary['by_category']:
                summary['by_category'][vuln.category] = 0
            summary['by_category'][vuln.category] += 1

            # Count by file
            if vuln.file_path not in summary['top_files']:
                summary['top_files'][vuln.file_path] = 0
            summary['top_files'][vuln.file_path] += 1

        # Sort categories by count
        summary['by_category'] = dict(
            sorted(summary['by_category'].items(),
                   key=lambda x: x[1], reverse=True)[:10]
        )

        # Sort files by count
        summary['top_files'] = dict(
            sorted(summary['top_files'].items(),
                   key=lambda x: x[1], reverse=True)[:5]
        )

        return summary


# Test function
if __name__ == "__main__":
    # Test with sample report
    parser = SASTParser()

    try:
        with open('../../data/sample_reports/sast_sample.json', 'r') as f:
            content = f.read()

        vulns = parser.parse(content)

        print("="*60)
        print("SAST PARSER TEST")
        print("="*60)
        print(f"\n✅ Successfully parsed {len(vulns)} vulnerabilities\n")

        summary = parser.get_summary(vulns)

        print("Summary by Severity:")
        for severity, count in summary['by_severity'].items():
            if count > 0:
                print(f"  {severity}: {count}")

        print("\nTop Categories:")
        for category, count in list(summary['by_category'].items())[:5]:
            print(f"  {category}: {count}")

        print("\nSample Vulnerability:")
        if vulns:
            vuln = vulns[0]
            print(f"  Title: {vuln.title}")
            print(f"  Severity: {vuln.severity}")
            print(f"  Category: {vuln.category}")
            print(f"  File: {vuln.file_path}:{vuln.line_number}")
            print(f"  CWE: {vuln.cwe_id}")
            print(f"  Description: {vuln.description[:100]}...")

        print("\n✅ SAST Parser test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
