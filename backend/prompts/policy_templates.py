"""
Policy Generation Prompt Templates
Structured prompts for LLM-based security policy generation
"""

from typing import Dict, List


class PolicyPromptTemplates:
    """Prompt templates for different LLM models and policy types"""

    @staticmethod
    def get_system_prompt() -> str:
        """
        System prompt that sets the role and context for all LLMs

        Returns:
            System prompt string
        """
        return """You are an expert cybersecurity policy analyst and technical writer specializing in translating technical vulnerability reports into professional security policies that comply with international standards (NIST Cybersecurity Framework and ISO/IEC 27001:2022).

Your role is to:
1. Analyze technical security vulnerabilities
2. Map them to specific NIST CSF and ISO 27001 controls
3. Generate clear, actionable security policy sections
4. Provide business context and risk explanations
5. Recommend specific remediation steps with timelines

Guidelines:
- Use professional, formal language suitable for executive review
- Reference specific NIST CSF functions/categories and ISO 27001 Annex A controls
- Provide both technical and business impact descriptions
- Include measurable success criteria
- Assign clear ownership and deadlines based on severity
- Follow industry best practices (OWASP, CWE, CVE standards)"""

    @staticmethod
    def get_policy_generation_prompt(
        vulnerability: Dict,
        compliance_context: str,
        severity: str
    ) -> str:
        """
        Generate prompt for creating a security policy from a vulnerability

        Args:
            vulnerability: Dict with title, description, category, etc.
            compliance_context: Relevant NIST/ISO sections from RAG
            severity: CRITICAL, HIGH, MEDIUM, LOW

        Returns:
            Formatted prompt string
        """

        # Extract vulnerability details (handle SAST, SCA, DAST formats)
        # SAST: has title, file_path, line_number
        # SCA: has package_name, cve_id, current_version
        # DAST: has alert/name, url, method

        title = vulnerability.get('title') or \
                f"{vulnerability.get('package_name', '')} - {vulnerability.get('cve_id', '')}" or \
                vulnerability.get('alert') or \
                vulnerability.get('name') or \
                'Unknown vulnerability'

        description = vulnerability.get('description', 'No description available')

        category = vulnerability.get('category') or \
                   vulnerability.get('package_name') or \
                   'General'

        cwe_id = vulnerability.get('cwe_id', '')

        file_path = vulnerability.get('file_path') or \
                    vulnerability.get('url') or \
                    vulnerability.get('package_name', '')

        line_number = vulnerability.get('line_number', '')

        recommendation = vulnerability.get('recommendation') or \
                        vulnerability.get('solution', '')

        # Build location string
        location = file_path
        if line_number:
            location += f" (line {line_number})"

        prompt = f"""Generate a comprehensive security policy section for the following vulnerability:

VULNERABILITY DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {title}
Category: {category}
Severity: {severity}
{f'CWE: {cwe_id}' if cwe_id else ''}
Location: {location}

Description:
{description}

{f'Technical Recommendation: {recommendation}' if recommendation else ''}

RELEVANT COMPLIANCE REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{compliance_context}

TASK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate a professional security policy section that includes:

1. POLICY IDENTIFIER
   - Unique policy ID (format: SP-YYYY-NNN)
   - Policy title aligned with the vulnerability category

2. RISK STATEMENT
   - Business impact explanation (non-technical language)
   - Potential consequences if exploited
   - Affected systems/data/users

3. COMPLIANCE MAPPING
   - Specific NIST CSF references (Function.Category format, e.g., PR.DS-5)
   - Specific ISO 27001 Annex A controls (e.g., A.14.2.5)
   - Relevant industry standards (OWASP, CWE, etc.)

4. POLICY REQUIREMENTS
   - Clear security controls to be implemented
   - Technical and procedural requirements
   - Success criteria and validation methods

5. REMEDIATION PLAN
   - Specific technical actions required
   - Responsible party (based on severity: Critical→CTO, High→Security Lead, Medium→Dev Lead, Low→Developer)
   - Timeline (Critical: 24-48h, High: 1 week, Medium: 2 weeks, Low: 1 month)
   - Verification steps (code review, re-scan, penetration test, etc.)

6. MONITORING AND DETECTION
   - How to detect similar vulnerabilities in the future
   - Logging and alerting requirements
   - Continuous monitoring strategies

FORMAT REQUIREMENTS:
- Use clear section headers
- Professional tone suitable for compliance audits
- Concrete, actionable language (avoid vague terms)
- Include specific technical details where appropriate
- Maximum length: 400-500 words

Generate the policy section now:"""

        return prompt

    @staticmethod
    def get_aggregation_prompt(
        individual_policies: List[str],
        total_vulnerabilities: int,
        severity_breakdown: Dict[str, int]
    ) -> str:
        """
        Generate prompt for aggregating multiple policies into executive summary

        Args:
            individual_policies: List of generated policy sections
            total_vulnerabilities: Total number of vulnerabilities
            severity_breakdown: Dict with counts per severity level

        Returns:
            Aggregation prompt
        """

        policies_text = "\n\n".join([
            f"POLICY {i+1}:\n{policy}"
            for i, policy in enumerate(individual_policies[:5])  # First 5 for context
        ])

        prompt = f"""You are reviewing {total_vulnerabilities} security policy sections generated from a DevSecOps scan.

SEVERITY BREAKDOWN:
- Critical: {severity_breakdown.get('CRITICAL', 0)}
- High: {severity_breakdown.get('HIGH', 0)}
- Medium: {severity_breakdown.get('MEDIUM', 0)}
- Low: {severity_breakdown.get('LOW', 0)}

SAMPLE POLICIES (first 5):
{policies_text}

TASK:
Generate an EXECUTIVE SUMMARY that includes:

1. OVERVIEW
   - Total vulnerabilities discovered
   - Overall risk level assessment
   - Key affected systems/components

2. CRITICAL FINDINGS
   - Top 3-5 most critical issues
   - Immediate actions required
   - Business impact summary

3. COMPLIANCE STATUS
   - NIST CSF coverage gaps
   - ISO 27001 control deficiencies
   - Regulatory implications

4. REMEDIATION ROADMAP
   - Phase 1: Critical fixes (24-48 hours)
   - Phase 2: High priority (1 week)
   - Phase 3: Medium/Low priority (2-4 weeks)

5. RECOMMENDATIONS
   - Process improvements
   - Preventive measures
   - Security posture enhancements

Keep the executive summary concise (300-400 words) and suitable for C-level review.

Generate the executive summary now:"""

        return prompt

    @staticmethod
    def get_comparative_study_prompt(
        vulnerability: Dict,
        compliance_context: str
    ) -> str:
        """
        Special prompt for comparative LLM study
        Uses standardized format to enable fair comparison

        Args:
            vulnerability: Vulnerability details
            compliance_context: RAG context

        Returns:
            Standardized prompt for comparison
        """

        title = vulnerability.get('title', 'Unknown')
        category = vulnerability.get('category', 'General')
        severity = vulnerability.get('severity', 'MEDIUM')

        prompt = f"""SECURITY POLICY GENERATION TASK

Vulnerability: {title}
Category: {category}
Severity: {severity}

Compliance Context:
{compliance_context[:500]}

Generate a security policy section (200-250 words) that includes:
1. Risk statement (business impact)
2. NIST CSF and ISO 27001 mappings
3. Remediation requirements with timeline
4. Monitoring recommendations

Use professional tone. Reference specific controls. Be concise and actionable."""

        return prompt

    @staticmethod
    def get_refinement_prompt(
        initial_policy: str,
        validation_issues: List[str]
    ) -> str:
        """
        Prompt for refining a policy that failed validation

        Args:
            initial_policy: The original generated policy
            validation_issues: List of issues found

        Returns:
            Refinement prompt
        """

        issues_text = "\n".join([f"- {issue}" for issue in validation_issues])

        prompt = f"""The following security policy section has validation issues:

ORIGINAL POLICY:
{initial_policy}

VALIDATION ISSUES:
{issues_text}

TASK:
Rewrite the policy section to address all validation issues while maintaining:
- Professional tone
- Compliance references (NIST CSF, ISO 27001)
- Actionable recommendations
- Clear structure

Generate the improved policy section now:"""

        return prompt


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("POLICY PROMPT TEMPLATES TEST")
    print("=" * 60)

    templates = PolicyPromptTemplates()

    # Test 1: System prompt
    print("\n1. System Prompt:")
    print("-" * 60)
    system_prompt = templates.get_system_prompt()
    print(system_prompt[:200] + "...")
    print(f"Length: {len(system_prompt)} characters")

    # Test 2: Policy generation prompt
    print("\n2. Policy Generation Prompt:")
    print("-" * 60)
    test_vuln = {
        'title': 'SQL Injection in login endpoint',
        'description': 'User input is directly concatenated into SQL query without sanitization',
        'category': 'Injection',
        'severity': 'CRITICAL',
        'cwe_id': 'CWE-89',
        'file_path': 'src/auth/login.js',
        'line_number': 42,
        'recommendation': 'Use parameterized queries or prepared statements'
    }

    test_compliance = """[NIST CSF] PR.DS-5 - Protections against data leaks are implemented
[ISO 27001] A.14.2.5 - Secure system engineering principles
[NIST CSF] DE.CM-4 - Malicious code is detected"""

    policy_prompt = templates.get_policy_generation_prompt(
        test_vuln,
        test_compliance,
        'CRITICAL'
    )
    print(policy_prompt[:300] + "...")
    print(f"Length: {len(policy_prompt)} characters")

    # Test 3: Aggregation prompt
    print("\n3. Aggregation Prompt:")
    print("-" * 60)
    sample_policies = [
        "Policy 1: SQL Injection - Critical risk requiring immediate remediation...",
        "Policy 2: XSS Vulnerability - High risk in user input handling...",
        "Policy 3: Outdated dependency - Medium risk security update needed..."
    ]

    severity_breakdown = {
        'CRITICAL': 5,
        'HIGH': 12,
        'MEDIUM': 18,
        'LOW': 7
    }

    agg_prompt = templates.get_aggregation_prompt(
        sample_policies,
        42,
        severity_breakdown
    )
    print(agg_prompt[:300] + "...")
    print(f"Length: {len(agg_prompt)} characters")

    # Test 4: Comparative study prompt
    print("\n4. Comparative Study Prompt:")
    print("-" * 60)
    comp_prompt = templates.get_comparative_study_prompt(
        test_vuln,
        test_compliance
    )
    print(comp_prompt[:300] + "...")
    print(f"Length: {len(comp_prompt)} characters")

    # Test 5: Refinement prompt
    print("\n5. Refinement Prompt:")
    print("-" * 60)
    test_issues = [
        "Missing NIST CSF reference",
        "No timeline specified",
        "Vague remediation steps"
    ]

    ref_prompt = templates.get_refinement_prompt(
        "Original policy text here...",
        test_issues
    )
    print(ref_prompt[:300] + "...")
    print(f"Length: {len(ref_prompt)} characters")

    print("\n" + "=" * 60)
    print("All prompt templates generated successfully!")
    print("=" * 60)
