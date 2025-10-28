"""
DAST (Dynamic Application Security Testing) Report Parser

Supports: OWASP ZAP, Burp Suite, Acunetix
Input: XML or JSON format
Output: Normalized runtime vulnerability data
"""

import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup


@dataclass
class DASTVulnerability:
    """Normalized DAST vulnerability data structure"""
    url: str
    endpoint: str
    method: str  # GET, POST, etc.
    issue_type: str  # SQL Injection, XSS, etc.
    risk_level: str
    confidence: str
    description: str
    solution: str
    cwe_id: Optional[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class DASTParser:
    """Parse DAST reports from various tools"""

    RISK_MAPPING = {
        '3': 'HIGH',
        '2': 'MEDIUM',
        '1': 'LOW',
        '0': 'INFO',
        'HIGH': 'HIGH',
        'MEDIUM': 'MEDIUM',
        'LOW': 'LOW',
        'INFO': 'LOW',
        'INFORMATIONAL': 'LOW'
    }

    def __init__(self):
        self.vulnerabilities: List[DASTVulnerability] = []

    def parse(self, report_content: str) -> List[DASTVulnerability]:
        """
        Parse DAST report and return normalized vulnerabilities

        Args:
            report_content: XML or JSON string of DAST report

        Returns:
            List of DASTVulnerability objects
        """
        try:
            # Try to detect format
            if report_content.strip().startswith('<?xml') or report_content.strip().startswith('<'):
                # XML format (OWASP ZAP)
                return self._parse_zap_xml(report_content)
            else:
                # Try JSON format
                data = json.loads(report_content)
                return self._parse_json(data)

        except json.JSONDecodeError:
            # If JSON fails, try XML
            try:
                return self._parse_zap_xml(report_content)
            except Exception as e:
                raise ValueError(f"Unable to parse as XML or JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing DAST report: {e}")

    def _parse_zap_xml(self, xml_content: str) -> List[DASTVulnerability]:
        """Parse OWASP ZAP XML report format"""
        vulnerabilities = []

        try:
            soup = BeautifulSoup(xml_content, 'xml')

            # Find all alert items
            alerts = soup.find_all('alertitem')

            for alert in alerts:
                try:
                    # Extract risk code and convert to severity
                    risk_code = alert.find('riskcode')
                    risk_level = self._normalize_risk(
                        risk_code.text if risk_code else '1'
                    )

                    # Extract CWE ID
                    cwe_elem = alert.find('cweid')
                    cwe_id = f"CWE-{cwe_elem.text}" if cwe_elem and cwe_elem.text else None

                    # Get first instance for URL/method details
                    instances = alert.find_all('instance')
                    if instances:
                        first_instance = instances[0]
                        url = first_instance.find('uri')
                        method = first_instance.find('method')

                        url_text = url.text if url else 'Unknown'
                        method_text = method.text if method else 'GET'
                    else:
                        url_text = 'Unknown'
                        method_text = 'GET'

                    # Extract other fields
                    alert_name = alert.find('alert')
                    desc = alert.find('desc')
                    solution = alert.find('solution')
                    confidence = alert.find('confidence')

                    vuln = DASTVulnerability(
                        url=url_text,
                        endpoint=self._extract_endpoint(url_text),
                        method=method_text,
                        issue_type=alert_name.text if alert_name else 'Unknown Issue',
                        risk_level=risk_level,
                        confidence=confidence.text if confidence else 'MEDIUM',
                        description=desc.text if desc else 'No description',
                        solution=solution.text if solution else 'Review and fix',
                        cwe_id=cwe_id
                    )

                    vulnerabilities.append(vuln)

                except Exception as e:
                    print(f"Warning: Skipping malformed alert: {e}")
                    continue

        except Exception as e:
            raise ValueError(f"Error parsing ZAP XML: {e}")

        return vulnerabilities

    def _parse_json(self, data: Dict) -> List[DASTVulnerability]:
        """Parse JSON format DAST reports"""
        vulnerabilities = []

        # Generic JSON parsing - adapt based on actual format
        issues = data.get('issues', data.get('findings', []))

        for issue in issues:
            try:
                risk_level = self._normalize_risk(issue.get('severity', 'MEDIUM'))

                vuln = DASTVulnerability(
                    url=issue.get('url', 'Unknown'),
                    endpoint=issue.get('endpoint', issue.get('path', '/')),
                    method=issue.get('method', 'GET'),
                    issue_type=issue.get('title', issue.get('name', 'Unknown')),
                    risk_level=risk_level,
                    confidence=issue.get('confidence', 'MEDIUM'),
                    description=issue.get('description', 'No description'),
                    solution=issue.get('solution', issue.get('remediation', 'Review and fix')),
                    cwe_id=issue.get('cwe', None)
                )

                vulnerabilities.append(vuln)

            except Exception as e:
                print(f"Warning: Skipping malformed issue: {e}")
                continue

        return vulnerabilities

    def _normalize_risk(self, risk: str) -> str:
        """Normalize risk level to standard severity"""
        risk_upper = risk.upper().strip()
        return self.RISK_MAPPING.get(risk_upper, 'MEDIUM')

    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint path from full URL"""
        try:
            if '://' in url:
                # Remove protocol and domain
                parts = url.split('://', 1)
                if len(parts) > 1:
                    path_part = parts[1]
                    if '/' in path_part:
                        path = '/' + '/'.join(path_part.split('/')[1:])
                        # Remove query params
                        if '?' in path:
                            path = path.split('?')[0]
                        return path
            return url
        except:
            return url

    def get_summary(self, vulnerabilities: List[DASTVulnerability]) -> Dict:
        """Get summary statistics of vulnerabilities"""
        summary = {
            'total': len(vulnerabilities),
            'by_risk': {
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            },
            'by_type': {},
            'top_endpoints': {}
        }

        for vuln in vulnerabilities:
            # Count by risk
            if vuln.risk_level in summary['by_risk']:
                summary['by_risk'][vuln.risk_level] += 1

            # Count by type
            if vuln.issue_type not in summary['by_type']:
                summary['by_type'][vuln.issue_type] = 0
            summary['by_type'][vuln.issue_type] += 1

            # Count by endpoint
            if vuln.endpoint not in summary['top_endpoints']:
                summary['top_endpoints'][vuln.endpoint] = 0
            summary['top_endpoints'][vuln.endpoint] += 1

        # Sort types by count
        summary['by_type'] = dict(
            sorted(summary['by_type'].items(),
                   key=lambda x: x[1], reverse=True)[:10]
        )

        # Sort endpoints by count
        summary['top_endpoints'] = dict(
            sorted(summary['top_endpoints'].items(),
                   key=lambda x: x[1], reverse=True)[:5]
        )

        return summary


# Test function
if __name__ == "__main__":
    # Test with sample report
    parser = DASTParser()

    try:
        with open('../../data/sample_reports/dast_sample.xml', 'r') as f:
            content = f.read()

        vulns = parser.parse(content)

        print("="*60)
        print("DAST PARSER TEST")
        print("="*60)
        print(f"\n✅ Successfully parsed {len(vulns)} vulnerabilities\n")

        summary = parser.get_summary(vulns)

        print("Summary by Risk Level:")
        for risk, count in summary['by_risk'].items():
            if count > 0:
                print(f"  {risk}: {count}")

        print("\nTop Issue Types:")
        for issue_type, count in list(summary['by_type'].items())[:5]:
            print(f"  {issue_type}: {count}")

        print("\nTop Vulnerable Endpoints:")
        for endpoint, count in list(summary['top_endpoints'].items())[:3]:
            print(f"  {endpoint}: {count} issues")

        print("\nSample Vulnerability:")
        if vulns:
            vuln = vulns[0]
            print(f"  Issue: {vuln.issue_type}")
            print(f"  Risk: {vuln.risk_level}")
            print(f"  URL: {vuln.url}")
            print(f"  Method: {vuln.method}")
            print(f"  CWE: {vuln.cwe_id}")
            print(f"  Description: {vuln.description[:100]}...")

        print("\n✅ DAST Parser test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
