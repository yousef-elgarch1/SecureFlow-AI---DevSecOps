"""
Compliance Coverage Analyzer
Analyzes which NIST CSF and ISO 27001 controls are covered by generated policies
"""

from typing import Dict, List, Set
import re


class ComplianceCoverageAnalyzer:
    """
    Analyzes compliance control coverage in generated policies
    """

    def __init__(self):
        # NIST CSF Framework Controls (23 categories across 5 functions)
        self.nist_csf_controls = {
            # Identify (ID)
            "ID.AM": ["ID.AM-1", "ID.AM-2", "ID.AM-3", "ID.AM-4", "ID.AM-5", "ID.AM-6"],
            "ID.BE": ["ID.BE-1", "ID.BE-2", "ID.BE-3", "ID.BE-4", "ID.BE-5"],
            "ID.GV": ["ID.GV-1", "ID.GV-2", "ID.GV-3", "ID.GV-4"],
            "ID.RA": ["ID.RA-1", "ID.RA-2", "ID.RA-3", "ID.RA-4", "ID.RA-5", "ID.RA-6"],
            "ID.RM": ["ID.RM-1", "ID.RM-2", "ID.RM-3"],
            "ID.SC": ["ID.SC-1", "ID.SC-2", "ID.SC-3", "ID.SC-4", "ID.SC-5"],

            # Protect (PR)
            "PR.AC": ["PR.AC-1", "PR.AC-2", "PR.AC-3", "PR.AC-4", "PR.AC-5", "PR.AC-6", "PR.AC-7"],
            "PR.AT": ["PR.AT-1", "PR.AT-2", "PR.AT-3", "PR.AT-4", "PR.AT-5"],
            "PR.DS": ["PR.DS-1", "PR.DS-2", "PR.DS-3", "PR.DS-4", "PR.DS-5", "PR.DS-6", "PR.DS-7", "PR.DS-8"],
            "PR.IP": ["PR.IP-1", "PR.IP-2", "PR.IP-3", "PR.IP-4", "PR.IP-5", "PR.IP-6", "PR.IP-7", "PR.IP-8", "PR.IP-9", "PR.IP-10", "PR.IP-11", "PR.IP-12"],
            "PR.MA": ["PR.MA-1", "PR.MA-2"],
            "PR.PT": ["PR.PT-1", "PR.PT-2", "PR.PT-3", "PR.PT-4", "PR.PT-5"],

            # Detect (DE)
            "DE.AE": ["DE.AE-1", "DE.AE-2", "DE.AE-3", "DE.AE-4", "DE.AE-5"],
            "DE.CM": ["DE.CM-1", "DE.CM-2", "DE.CM-3", "DE.CM-4", "DE.CM-5", "DE.CM-6", "DE.CM-7", "DE.CM-8"],
            "DE.DP": ["DE.DP-1", "DE.DP-2", "DE.DP-3", "DE.DP-4", "DE.DP-5"],

            # Respond (RS)
            "RS.RP": ["RS.RP-1"],
            "RS.CO": ["RS.CO-1", "RS.CO-2", "RS.CO-3", "RS.CO-4", "RS.CO-5"],
            "RS.AN": ["RS.AN-1", "RS.AN-2", "RS.AN-3", "RS.AN-4", "RS.AN-5"],
            "RS.MI": ["RS.MI-1", "RS.MI-2", "RS.MI-3"],
            "RS.IM": ["RS.IM-1", "RS.IM-2"],

            # Recover (RC)
            "RC.RP": ["RC.RP-1"],
            "RC.IM": ["RC.IM-1", "RC.IM-2"],
            "RC.CO": ["RC.CO-1", "RC.CO-2", "RC.CO-3"]
        }

        # ISO 27001:2013 Annex A Controls (14 domains, 35 control objectives, 114 controls)
        self.iso_27001_controls = {
            "A.5": ["A.5.1.1", "A.5.1.2"],  # Information security policies
            "A.6": ["A.6.1.1", "A.6.1.2", "A.6.1.3", "A.6.1.4", "A.6.1.5", "A.6.2.1", "A.6.2.2"],  # Organization
            "A.7": ["A.7.1.1", "A.7.1.2", "A.7.2.1", "A.7.2.2", "A.7.2.3", "A.7.3.1"],  # Human resources
            "A.8": ["A.8.1.1", "A.8.1.2", "A.8.1.3", "A.8.1.4", "A.8.2.1", "A.8.2.2", "A.8.2.3", "A.8.3.1", "A.8.3.2", "A.8.3.3"],  # Asset management
            "A.9": ["A.9.1.1", "A.9.1.2", "A.9.2.1", "A.9.2.2", "A.9.2.3", "A.9.2.4", "A.9.2.5", "A.9.2.6", "A.9.3.1", "A.9.4.1", "A.9.4.2", "A.9.4.3", "A.9.4.4", "A.9.4.5"],  # Access control
            "A.10": ["A.10.1.1", "A.10.1.2"],  # Cryptography
            "A.11": ["A.11.1.1", "A.11.1.2", "A.11.1.3", "A.11.1.4", "A.11.1.5", "A.11.1.6", "A.11.2.1", "A.11.2.2", "A.11.2.3", "A.11.2.4", "A.11.2.5", "A.11.2.6", "A.11.2.7", "A.11.2.8", "A.11.2.9"],  # Physical security
            "A.12": ["A.12.1.1", "A.12.1.2", "A.12.1.3", "A.12.1.4", "A.12.2.1", "A.12.3.1", "A.12.4.1", "A.12.4.2", "A.12.4.3", "A.12.4.4", "A.12.5.1", "A.12.6.1", "A.12.6.2", "A.12.7.1"],  # Operations security
            "A.13": ["A.13.1.1", "A.13.1.2", "A.13.1.3", "A.13.2.1", "A.13.2.2", "A.13.2.3", "A.13.2.4"],  # Communications security
            "A.14": ["A.14.1.1", "A.14.1.2", "A.14.1.3", "A.14.2.1", "A.14.2.2", "A.14.2.3", "A.14.2.4", "A.14.2.5", "A.14.2.6", "A.14.2.7", "A.14.2.8", "A.14.2.9", "A.14.3.1"],  # System acquisition
            "A.15": ["A.15.1.1", "A.15.1.2", "A.15.1.3", "A.15.2.1", "A.15.2.2"],  # Supplier relationships
            "A.16": ["A.16.1.1", "A.16.1.2", "A.16.1.3", "A.16.1.4", "A.16.1.5", "A.16.1.6", "A.16.1.7"],  # Incident management
            "A.17": ["A.17.1.1", "A.17.1.2", "A.17.1.3", "A.17.2.1"],  # Business continuity
            "A.18": ["A.18.1.1", "A.18.1.2", "A.18.1.3", "A.18.1.4", "A.18.1.5", "A.18.2.1", "A.18.2.2", "A.18.2.3"]  # Compliance
        }

    def analyze_coverage(self, policies: List[Dict]) -> Dict:
        """
        Analyzes compliance coverage from generated policies

        Args:
            policies: List of policy dictionaries with compliance_mapping

        Returns:
            Dict with NIST/ISO coverage analysis
        """
        nist_covered = set()
        iso_covered = set()

        # Extract all control mentions from policies
        for policy in policies:
            if "compliance_mapping" in policy:
                mappings = policy["compliance_mapping"]

                # Extract NIST controls
                if "NIST CSF" in mappings:
                    controls = mappings["NIST CSF"]
                    if isinstance(controls, list):
                        nist_covered.update(controls)
                    elif isinstance(controls, str):
                        # Handle comma-separated strings
                        nist_covered.update([c.strip() for c in controls.split(',')])

                # Extract ISO controls
                if "ISO 27001" in mappings:
                    controls = mappings["ISO 27001"]
                    if isinstance(controls, list):
                        iso_covered.update(controls)
                    elif isinstance(controls, str):
                        iso_covered.update([c.strip() for c in controls.split(',')])

        # Get all defined controls
        all_nist = self._get_all_nist_controls()
        all_iso = self._get_all_iso_controls()

        # Calculate gaps
        nist_gaps = set(all_nist) - nist_covered
        iso_gaps = set(all_iso) - iso_covered

        # Calculate coverage by category
        nist_by_function = self._analyze_nist_by_function(nist_covered)
        iso_by_domain = self._analyze_iso_by_domain(iso_covered)

        return {
            "nist_csf": {
                "total_controls": len(all_nist),
                "covered_controls": len(nist_covered),
                "coverage_percentage": round((len(nist_covered) / len(all_nist)) * 100, 1) if all_nist else 0,
                "covered": sorted(list(nist_covered)),
                "gaps": sorted(list(nist_gaps)),
                "by_function": nist_by_function
            },
            "iso_27001": {
                "total_controls": len(all_iso),
                "covered_controls": len(iso_covered),
                "coverage_percentage": round((len(iso_covered) / len(all_iso)) * 100, 1) if all_iso else 0,
                "covered": sorted(list(iso_covered)),
                "gaps": sorted(list(iso_gaps)),
                "by_domain": iso_by_domain
            },
            "overall_score": round(
                ((len(nist_covered) / len(all_nist) if all_nist else 0) +
                 (len(iso_covered) / len(all_iso) if all_iso else 0)) / 2 * 100, 1
            )
        }

    def _get_all_nist_controls(self) -> List[str]:
        """Returns flat list of all NIST CSF controls"""
        all_controls = []
        for controls in self.nist_csf_controls.values():
            all_controls.extend(controls)
        return all_controls

    def _get_all_iso_controls(self) -> List[str]:
        """Returns flat list of all ISO 27001 controls"""
        all_controls = []
        for controls in self.iso_27001_controls.values():
            all_controls.extend(controls)
        return all_controls

    def _analyze_nist_by_function(self, covered: Set[str]) -> Dict:
        """Analyzes NIST coverage by function (Identify, Protect, etc.)"""
        functions = {
            "Identify": ["ID.AM", "ID.BE", "ID.GV", "ID.RA", "ID.RM", "ID.SC"],
            "Protect": ["PR.AC", "PR.AT", "PR.DS", "PR.IP", "PR.MA", "PR.PT"],
            "Detect": ["DE.AE", "DE.CM", "DE.DP"],
            "Respond": ["RS.RP", "RS.CO", "RS.AN", "RS.MI", "RS.IM"],
            "Recover": ["RC.RP", "RC.IM", "RC.CO"]
        }

        result = {}
        for function_name, categories in functions.items():
            total = 0
            covered_count = 0

            for category in categories:
                if category in self.nist_csf_controls:
                    controls = self.nist_csf_controls[category]
                    total += len(controls)
                    covered_count += sum(1 for c in controls if c in covered)

            result[function_name] = {
                "total": total,
                "covered": covered_count,
                "percentage": round((covered_count / total) * 100, 1) if total > 0 else 0
            }

        return result

    def _analyze_iso_by_domain(self, covered: Set[str]) -> Dict:
        """Analyzes ISO coverage by domain (A.5, A.6, etc.)"""
        result = {}

        for domain, controls in self.iso_27001_controls.items():
            covered_count = sum(1 for c in controls if c in covered)
            result[domain] = {
                "total": len(controls),
                "covered": covered_count,
                "percentage": round((covered_count / len(controls)) * 100, 1) if controls else 0
            }

        return result

    def generate_report(self, analysis: Dict) -> str:
        """
        Generates human-readable compliance coverage report

        Args:
            analysis: Output from analyze_coverage()

        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 80)
        report.append("COMPLIANCE COVERAGE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall score
        report.append(f"Overall Compliance Score: {analysis['overall_score']}%")
        report.append("")

        # NIST CSF Section
        nist = analysis['nist_csf']
        report.append("-" * 80)
        report.append("NIST CYBERSECURITY FRAMEWORK (CSF)")
        report.append("-" * 80)
        report.append(f"Coverage: {nist['covered_controls']}/{nist['total_controls']} controls ({nist['coverage_percentage']}%)")
        report.append("")

        # NIST by function
        report.append("Coverage by Function:")
        for function, data in nist['by_function'].items():
            report.append(f"  {function:12s}: {data['covered']}/{data['total']:2d} ({data['percentage']:5.1f}%)")

        report.append("")
        report.append(f"Covered Controls ({len(nist['covered'])}):")
        if nist['covered']:
            # Group by category for better readability
            for i in range(0, len(nist['covered']), 8):
                report.append("  " + ", ".join(nist['covered'][i:i+8]))
        else:
            report.append("  None")

        report.append("")
        report.append(f"Gaps ({len(nist['gaps'])}):")
        if nist['gaps']:
            for i in range(0, len(nist['gaps']), 8):
                report.append("  " + ", ".join(nist['gaps'][i:i+8]))
        else:
            report.append("  None - Full coverage achieved!")

        report.append("")

        # ISO 27001 Section
        iso = analysis['iso_27001']
        report.append("-" * 80)
        report.append("ISO 27001:2013 ANNEX A")
        report.append("-" * 80)
        report.append(f"Coverage: {iso['covered_controls']}/{iso['total_controls']} controls ({iso['coverage_percentage']}%)")
        report.append("")

        # ISO by domain
        report.append("Coverage by Domain:")
        for domain, data in iso['by_domain'].items():
            report.append(f"  {domain:6s}: {data['covered']}/{data['total']:2d} ({data['percentage']:5.1f}%)")

        report.append("")
        report.append(f"Covered Controls ({len(iso['covered'])}):")
        if iso['covered']:
            for i in range(0, len(iso['covered']), 10):
                report.append("  " + ", ".join(iso['covered'][i:i+10]))
        else:
            report.append("  None")

        report.append("")
        report.append(f"Gaps ({len(iso['gaps'])}):")
        if iso['gaps']:
            for i in range(0, len(iso['gaps']), 10):
                report.append("  " + ", ".join(iso['gaps'][i:i+10]))
        else:
            report.append("  None - Full coverage achieved!")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Test with sample policies
    sample_policies = [
        {
            "vulnerability": {"title": "SQL Injection", "severity": "HIGH"},
            "compliance_mapping": {
                "NIST CSF": ["PR.AC-4", "DE.CM-7", "ID.RA-1"],
                "ISO 27001": ["A.14.2.5", "A.12.6.1", "A.9.4.1"]
            }
        },
        {
            "vulnerability": {"title": "XSS", "severity": "MEDIUM"},
            "compliance_mapping": {
                "NIST CSF": ["PR.DS-5", "DE.CM-1"],
                "ISO 27001": ["A.14.1.2", "A.14.2.1"]
            }
        }
    ]

    analyzer = ComplianceCoverageAnalyzer()
    result = analyzer.analyze_coverage(sample_policies)

    print(analyzer.generate_report(result))
    print("\nJSON Output:")
    import json
    print(json.dumps(result, indent=2))
