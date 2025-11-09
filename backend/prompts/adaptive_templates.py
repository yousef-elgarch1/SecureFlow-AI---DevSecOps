"""
Adaptive Policy Prompt Templates
Generates prompts tailored to user expertise level and role
"""

from typing import Dict
from backend.models.user_profile import UserProfile, ExpertiseLevel


class AdaptivePolicyPrompts:
    """Generate adaptive prompts based on user profile"""

    @staticmethod
    def get_beginner_sast_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """
        SAST Policy Prompt for Beginners/Junior Developers
        Focus: Learning, detailed explanations, code examples with comments
        """
        title = vulnerability.get('title', 'Security Vulnerability')
        description = vulnerability.get('description', '')
        file_path = vulnerability.get('file_path', '')
        line_number = vulnerability.get('line_number', '')
        severity = vulnerability.get('severity', 'MEDIUM')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a beginner-friendly security policy for a JUNIOR DEVELOPER with LIMITED security experience.

{user_context}

VULNERABILITY DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {title}
Location: {file_path}:{line_number}
Severity: {severity}
Description: {description}

COMPLIANCE CONTEXT:
{compliance_context}

REQUIREMENTS:
✓ Start with "What is this vulnerability?" - Explain in simple terms (like explaining to a friend)
✓ Explain WHY it's dangerous with a real-world analogy or example
✓ Provide BEFORE and AFTER code examples with line-by-line comments
✓ Include step-by-step remediation instructions (numbered list, very detailed)
✓ Add testing instructions (how to verify the fix works)
✓ Include learning resources (OWASP links, tutorials, documentation)
✓ Use simple language, avoid security jargon or explain technical terms
✓ Focus on practical "how-to" guidance

FORMAT YOUR RESPONSE AS:

## 📚 Understanding the Issue

### What is {title}?
[Explain in simple, non-technical terms what this vulnerability is]

### Why is it Dangerous?
[Explain the risks with a real-world example: "An attacker could..."]

### Real-World Impact:
[Describe what could happen: data breach, account takeover, etc.]

## 💻 How to Fix It

### Current Code (Vulnerable):
```
[Show the vulnerable code with comments explaining what's wrong]
```

### Fixed Code (Secure):
```
[Show the corrected code with comments explaining why it's secure]
```

### Step-by-Step Fix:
1. [First step in detail]
2. [Second step in detail]
3. [Continue...]

## ✅ Testing Your Fix

### How to Verify:
1. [Testing step 1]
2. [Testing step 2]

### Test Cases:
```
[Provide actual test code they can run]
```

## 🎓 Learn More

- OWASP Guide: [Relevant OWASP link]
- Tutorial: [Link to beginner-friendly tutorial]
- Best Practices: [Link to coding guidelines]

## 📋 Compliance

This fix helps meet:
- NIST CSF: [List controls from context]
- ISO 27001: [List controls from context]

## ⏰ Timeline

Priority: {severity}
Estimated Time: [Estimate in hours/days]
Deadline: [Based on severity]

Remember: Security is a learning process. Don't hesitate to ask for help!"""

    @staticmethod
    def get_intermediate_sast_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """
        SAST Policy Prompt for Intermediate/Senior Developers
        Focus: Technical solutions, best practices, frameworks
        """
        title = vulnerability.get('title', 'Security Vulnerability')
        description = vulnerability.get('description', '')
        file_path = vulnerability.get('file_path', '')
        line_number = vulnerability.get('line_number', '')
        severity = vulnerability.get('severity', 'MEDIUM')
        cwe_id = vulnerability.get('cwe_id', '')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a technical security policy for a SENIOR DEVELOPER with solid programming skills.

{user_context}

VULNERABILITY DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {title}
Location: {file_path}:{line_number}
Severity: {severity}
{f'CWE: {cwe_id}' if cwe_id else ''}
Description: {description}

COMPLIANCE CONTEXT:
{compliance_context}

REQUIREMENTS:
✓ Focus on technical implementation and best practices
✓ Provide code examples using modern frameworks/libraries
✓ Discuss architectural patterns and design principles
✓ Include integration with CI/CD pipeline (automated testing)
✓ Mention performance considerations if relevant
✓ Provide code review checklist
✓ Skip basic explanations (they know what {title} is)

FORMAT YOUR RESPONSE AS:

## Policy: {title} Prevention

### Risk Assessment
**Severity**: {severity}
{f'**CWE**: {cwe_id}' if cwe_id else ''}
**Attack Vector**: [Describe how this could be exploited]
**Business Impact**: [Financial, reputational, operational impact]

### Technical Remediation

#### Recommended Approach:
[Describe the best-practice solution using modern frameworks]

#### Code Example:
```python
# Before (Vulnerable)
[vulnerable code]

# After (Secure) - Using [Framework/Library]
[secure code with framework usage]
```

#### Alternative Approaches:
1. **Option 1**: [Approach 1 with pros/cons]
2. **Option 2**: [Approach 2 with pros/cons]

### Implementation Steps

1. **Update Dependencies**: [Required packages/versions]
2. **Refactor Code**: [Specific changes needed]
3. **Add Validation**: [Input validation logic]
4. **Configure Security Headers**: [If applicable]
5. **Update Tests**: [Test coverage requirements]

### Code Review Checklist

- [ ] All user input is validated/sanitized
- [ ] Framework security features are enabled
- [ ] Unit tests cover security scenarios
- [ ] No hardcoded credentials or secrets
- [ ] Error handling doesn't leak sensitive info

### CI/CD Integration

#### SAST Configuration:
```yaml
[Example Semgrep/SonarQube config to prevent this issue]
```

#### Pre-commit Hook:
```bash
[Git hook to check for this vulnerability]
```

### Compliance Mapping

**NIST Cybersecurity Framework**:
[List specific controls from compliance context with descriptions]

**ISO/IEC 27001:2022**:
[List specific Annex A controls from compliance context]

### Testing Strategy

#### Unit Tests:
```python
[Example unit test code]
```

#### Integration Tests:
[Testing approach for this vulnerability]

### Performance Considerations
[Discuss any performance implications of the fix]

### Timeline & Priority

**Priority**: {severity}
**Estimated Effort**: [Hours/days]
**Deadline**: [Based on severity]
**Assigned To**: [To be determined]

### References
- OWASP: [Relevant OWASP guide]
- CWE: {f'https://cwe.mitre.org/data/definitions/{cwe_id}.html' if cwe_id else 'N/A'}
- Framework Docs: [Relevant framework security docs]"""

    @staticmethod
    def get_advanced_sast_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """
        SAST Policy Prompt for Advanced/Security Engineers
        Focus: Compliance details, threat modeling, detection strategies
        """
        title = vulnerability.get('title', 'Security Vulnerability')
        description = vulnerability.get('description', '')
        file_path = vulnerability.get('file_path', '')
        line_number = vulnerability.get('line_number', '')
        severity = vulnerability.get('severity', 'MEDIUM')
        cwe_id = vulnerability.get('cwe_id', '')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a comprehensive security policy for a SECURITY ENGINEER with DEEP security expertise.

{user_context}

VULNERABILITY DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: {title}
Location: {file_path}:{line_number}
Severity: {severity}
{f'CWE: {cwe_id}' if cwe_id else ''}
Description: {description}

COMPLIANCE CONTEXT:
{compliance_context}

REQUIREMENTS:
✓ Detailed NIST CSF and ISO 27001 mapping with full control descriptions
✓ CVSS v3.1 scoring breakdown
✓ Multiple remediation strategies with security/performance trade-offs
✓ Detection and monitoring strategies (SIEM rules, WAF patterns, IDS signatures)
✓ Incident response procedures if exploited
✓ Threat modeling and attack chain analysis
✓ Defense-in-depth recommendations
✓ Integration with security tools (SAST/DAST/IAST/SCA)
✓ Skip basic code examples (focus on architecture and detection)

FORMAT YOUR RESPONSE AS:

## Security Policy: {title}

### Executive Summary
[Brief non-technical summary for management: What, Why, Impact, Cost]

### Risk Analysis

#### CVSS v3.1 Score Breakdown:
- **Base Score**: [Calculate 0-10]
- **Attack Vector**: [Network/Adjacent/Local/Physical]
- **Attack Complexity**: [Low/High]
- **Privileges Required**: [None/Low/High]
- **User Interaction**: [None/Required]
- **Scope**: [Unchanged/Changed]
- **Confidentiality Impact**: [None/Low/High]
- **Integrity Impact**: [None/Low/High]
- **Availability Impact**: [None/Low/High]

#### Threat Intelligence:
- **Known Exploits**: [Are there public exploits?]
- **MITRE ATT&CK Techniques**: [Relevant techniques]
- **Attack Chain**: [Typical exploitation flow]

### Compliance Framework Mapping

#### NIST Cybersecurity Framework:
[For each control from compliance context, provide:]
- **Control ID**: PR.XX-X
- **Function**: [Identify/Protect/Detect/Respond/Recover]
- **Category**: [Specific category]
- **Implementation Requirements**: [How this policy meets the control]
- **Evidence Required**: [What auditors will look for]

#### ISO/IEC 27001:2022 Annex A:
[For each control from compliance context, provide:]
- **Control**: A.X.X
- **Objective**: [Control objective]
- **Implementation Guidance**: [Specific to this vulnerability]
- **Audit Trail**: [Documentation requirements]

#### Additional Frameworks:
- **OWASP ASVS**: [Relevant verification requirements]
- **PCI DSS**: [If applicable]
- **SOC 2**: [If applicable]

### Defense-in-Depth Strategy

#### Layer 1: Prevention
1. **Code Level**: [Secure coding practices]
2. **Framework Level**: [Security features to enable]
3. **Infrastructure Level**: [WAF, network controls]

#### Layer 2: Detection
1. **SIEM Correlation Rules**:
```
[Provide actual SIEM rule in Sigma/Splunk/ELK format]
```

2. **WAF Signatures**:
```
[ModSecurity/AWS WAF rule examples]
```

3. **IDS/IPS Patterns**:
[Snort/Suricata signatures if applicable]

4. **Log Monitoring**:
[What logs to monitor, what patterns to alert on]

#### Layer 3: Response

##### If Exploitation Detected:
1. **Immediate Actions** (0-15 minutes):
   - [Containment steps]
   - [Evidence preservation]

2. **Short-term Response** (15 min - 4 hours):
   - [Investigation steps]
   - [Impact assessment]

3. **Long-term Response** (4+ hours):
   - [Root cause analysis]
   - [Remediation deployment]
   - [Post-incident review]

### Remediation Strategies

#### Strategy A: Secure Framework Migration
- **Approach**: [Use framework security features]
- **Security**: ⭐⭐⭐⭐⭐
- **Performance**: ⭐⭐⭐⭐
- **Complexity**: ⭐⭐⭐
- **Cost**: [Estimate]
- **Timeline**: [Estimate]

#### Strategy B: Manual Validation Layer
- **Approach**: [Custom validation logic]
- **Security**: ⭐⭐⭐⭐
- **Performance**: ⭐⭐⭐
- **Complexity**: ⭐⭐
- **Cost**: [Estimate]
- **Timeline**: [Estimate]

#### Strategy C: Web Application Firewall
- **Approach**: [WAF rules as temporary mitigation]
- **Security**: ⭐⭐⭐
- **Performance**: ⭐⭐⭐⭐⭐
- **Complexity**: ⭐
- **Cost**: [Estimate]
- **Timeline**: [Immediate]
- **Note**: Temporary solution, implement A or B for permanent fix

#### Recommended Approach: [A/B/C] with justification

### Security Tool Integration

#### SAST Configuration:
```yaml
# Semgrep rule to prevent regression
[Provide actual Semgrep/CodeQL rule]
```

#### DAST Testing:
```python
# Automated security test
[Provide actual test code using OWASP ZAP API or similar]
```

#### SCA Monitoring:
[Package versions to track, vulnerability monitoring]

### Threat Modeling

#### Attack Scenarios:
1. **Scenario 1**: [Detailed attack flow]
   - **Likelihood**: [Low/Medium/High]
   - **Impact**: [Low/Medium/High/Critical]
   - **Detection**: [How we'd detect this]

2. **Scenario 2**: [Another attack vector]
   [Continue...]

#### Countermeasures Effectiveness:
[How each layer mitigates each scenario]

### Metrics & KPIs

#### Success Criteria:
- [ ] Zero {title} findings in SAST scans
- [ ] WAF blocking 100% of test attacks
- [ ] SIEM detecting exploitation attempts within 60 seconds
- [ ] Mean Time to Detect (MTTD): < 5 minutes
- [ ] Mean Time to Respond (MTTR): < 2 hours

#### Monitoring Dashboards:
- **Daily**: [Metrics to track daily]
- **Weekly**: [Metrics to track weekly]
- **Monthly**: [Compliance reporting metrics]

### Documentation Requirements

#### For Audit:
- [ ] Policy document approval signature
- [ ] Implementation evidence (code commits, configs)
- [ ] Testing results (SAST/DAST reports)
- [ ] Training completion records
- [ ] Exception approvals (if any)

#### For Operations:
- [ ] Runbook for incident response
- [ ] Escalation procedures
- [ ] Contact information
- [ ] Tool access requirements

### Budget & Resource Requirements

**One-Time Costs**:
- Development: [Hours × Rate]
- Testing: [Hours × Rate]
- Tools: [If new tools needed]
- **Total**: [Amount]

**Recurring Costs**:
- Monitoring: [Annual cost]
- Training: [Annual cost]
- Auditing: [Annual cost]
- **Total Annual**: [Amount]

**ROI Analysis**:
- Cost of Breach: [Industry average for this vulnerability type]
- Cost of Prevention: [Total from above]
- **Savings**: [Breach cost - Prevention cost]

### Timeline

| Phase | Duration | Responsible | Deliverable |
|-------|----------|-------------|-------------|
| Planning | [Days] | Security Team | Remediation plan approved |
| Development | [Days] | Dev Team | Code changes committed |
| Testing | [Days] | QA/Security | Test results documented |
| Deployment | [Days] | DevOps | Production deployment |
| Validation | [Days] | Security | Re-scan shows no issues |
| Documentation | [Days] | All | Audit package complete |

**Total Timeline**: [Days/Weeks]
**Critical Deadline**: [Date based on severity]

### References

- **CWE**: {f'https://cwe.mitre.org/data/definitions/{cwe_id}.html' if cwe_id else 'N/A'}
- **OWASP**: [Relevant OWASP guides]
- **NIST**: [Relevant NIST publications]
- **ISO 27001**: [Relevant ISO documents]
- **MITRE ATT&CK**: [Relevant techniques]
- **Threat Intelligence**: [Relevant threat reports]

### Approval & Ownership

**Policy Owner**: [CISO/Security Manager]
**Technical Owner**: [Security Architect]
**Implementation Owner**: [Dev Team Lead]
**Review Date**: [Quarterly/Annual]

---

**Classification**: CONFIDENTIAL - Security Policy
**Version**: 1.0
**Last Updated**: [Current date]"""

    @staticmethod
    def get_beginner_sca_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """SCA Policy Prompt for Beginners - Focus on understanding dependencies"""
        package = vulnerability.get('package_name', 'unknown-package')
        version = vulnerability.get('installed_version', '')
        fixed_version = vulnerability.get('fixed_version', '')
        cve_id = vulnerability.get('cve_id', '')
        severity = vulnerability.get('severity', 'MEDIUM')
        description = vulnerability.get('description', '')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a beginner-friendly security policy for updating vulnerable dependencies.

{user_context}

VULNERABLE DEPENDENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package: {package}
Current Version: {version}
Fixed Version: {fixed_version}
CVE ID: {cve_id}
Severity: {severity}
Description: {description}

COMPLIANCE CONTEXT:
{compliance_context}

REQUIREMENTS:
✓ Explain what package dependencies are (for beginners)
✓ Explain why outdated packages are dangerous
✓ Provide step-by-step update instructions
✓ Show before/after package.json or requirements.txt examples
✓ Explain how to verify the update worked
✓ Include testing instructions
✓ Simple language, avoid complex dependency jargon

FORMAT YOUR RESPONSE AS:

## 📦 Understanding Package Dependencies

### What are Dependencies?
[Explain in simple terms what {package} is and why we use it]

### Why is {version} Vulnerable?
**CVE ID**: {cve_id}
**Issue**: [Explain the vulnerability in simple terms]
**Risk**: [What could happen if we don't update]

### Who Discovered This?
[Credit to security researchers, explain CVE system briefly]

## 🔧 How to Fix It

### Step-by-Step Update Guide:

#### Step 1: Check Your Current Version
```bash
# For npm (JavaScript/Node.js)
npm list {package}

# For pip (Python)
pip show {package}
```

#### Step 2: Update the Package
```bash
# For npm
npm install {package}@{fixed_version}

# For pip
pip install {package}=={fixed_version}
```

#### Step 3: Update Your Lock File
```bash
# For npm
npm install

# For pip
pip freeze > requirements.txt
```

### Before (Vulnerable):
```json
// package.json or requirements.txt
"{package}": "{version}"
```

### After (Secure):
```json
"{package}": "{fixed_version}"
```

## ✅ Testing Your Update

### Test That It Still Works:
1. Run your application: `npm start` or `python app.py`
2. Test the features that use {package}
3. Run your test suite: `npm test` or `pytest`

### Verify the Version:
```bash
npm list {package}  # Should show {fixed_version}
```

## 🎓 Learn More

- **What is {cve_id}?**: https://nvd.nist.gov/vuln/detail/{cve_id}
- **Understanding CVEs**: [Link to beginner CVE guide]
- **Dependency Management**: [Link to package manager docs]

## 📋 Compliance

Keeping dependencies updated helps meet:
- NIST CSF: [Controls from context]
- ISO 27001: [Controls from context]

## ⏰ Timeline

Priority: {severity}
Time Needed: 30 minutes - 2 hours
Deadline: [Based on severity]

**Pro Tip**: Set up automated dependency scanning to catch these issues early!"""

    @staticmethod
    def get_intermediate_sca_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """SCA Policy Prompt for Intermediate users"""
        package = vulnerability.get('package_name', 'unknown-package')
        version = vulnerability.get('installed_version', '')
        fixed_version = vulnerability.get('fixed_version', '')
        cve_id = vulnerability.get('cve_id', '')
        severity = vulnerability.get('severity', 'MEDIUM')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a dependency update policy for SENIOR DEVELOPERS.

{user_context}

VULNERABLE DEPENDENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package: {package} @ {version}
Fixed in: {fixed_version}
CVE: {cve_id}
Severity: {severity}

COMPLIANCE CONTEXT:
{compliance_context}

FORMAT YOUR RESPONSE AS:

## Policy: Dependency Update - {package}

### Vulnerability Assessment
**CVE**: {cve_id}
**CVSS Score**: [From CVE database]
**Severity**: {severity}
**Affected Versions**: < {fixed_version}
**Exploitability**: [Known exploits? PoC available?]

### Remediation Strategy

#### Recommended Action:
Update {package} from {version} to {fixed_version}

#### Migration Steps:
1. **Review Changelog**: Check {package} release notes for breaking changes
2. **Update Dependency**: `npm install {package}@{fixed_version}` or `pip install {package}=={fixed_version}`
3. **Update Lock File**: Commit package-lock.json / requirements.txt
4. **Run Tests**: Ensure backward compatibility
5. **Deploy**: Follow standard deployment process

#### Potential Breaking Changes:
[List any API changes between {version} and {fixed_version}]

### Automated Scanning Integration

#### Dependabot Configuration:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

#### Snyk Integration:
```bash
snyk test
snyk monitor
```

### Compliance Mapping

**NIST CSF**:
[List controls with implementation details]

**ISO 27001**:
[List controls with implementation details]

### Testing Requirements

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security scan shows no CVE-{cve_id}
- [ ] Performance benchmarks unchanged
- [ ] No regression in functionality

### Timeline

**Priority**: {severity}
**Effort**: 2-4 hours
**Deadline**: [Date based on severity]"""

    @staticmethod
    def get_advanced_sca_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """SCA Policy Prompt for Advanced users - Supply chain security focus"""
        package = vulnerability.get('package_name', 'unknown-package')
        version = vulnerability.get('installed_version', '')
        fixed_version = vulnerability.get('fixed_version', '')
        cve_id = vulnerability.get('cve_id', '')
        severity = vulnerability.get('severity', 'MEDIUM')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a comprehensive supply chain security policy for SECURITY ENGINEERS.

{user_context}

VULNERABLE DEPENDENCY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package: {package}
Version: {version} → {fixed_version}
CVE: {cve_id}
Severity: {severity}

COMPLIANCE CONTEXT:
{compliance_context}

FORMAT YOUR RESPONSE AS:

## Supply Chain Security Policy: {package} Vulnerability

### Threat Intelligence

#### CVE Analysis:
- **CVE ID**: {cve_id}
- **CVSS v3.1**: [Full vector string]
- **CWE**: [Common Weakness]
- **Exploitation Status**: [Public exploits available?]
- **Patch Availability**: {fixed_version}
- **Vendor Response Time**: [How long from disclosure to patch?]

#### Attack Surface:
- **Direct Dependency**: [Yes/No - is this directly imported?]
- **Transitive Depth**: [How many levels deep in dependency tree?]
- **Usage in Code**: [Which modules/functions use this package?]
- **Attack Vectors**: [How could this be exploited in our context?]

### Supply Chain Risk Assessment

#### Package Trust Score:
- **Maintainer Activity**: [Active/Moderate/Abandoned]
- **Download Statistics**: [Weekly downloads]
- **Security Audit History**: [Previous CVEs]
- **Code Review Status**: [Has security review?]
- **Digital Signatures**: [Package signing verification]

#### Dependency Chain Analysis:
```
{package}@{version}
  ├── sub-dependency-1@version
  ├── sub-dependency-2@version (VULNERABLE)
  └── sub-dependency-3@version
```

### Remediation Options

#### Option 1: Direct Update (Recommended)
- **Action**: Update to {fixed_version}
- **Risk**: Breaking changes in major version bumps
- **Effort**: 2-4 hours (testing included)
- **Rollback Plan**: [Git revert process]

#### Option 2: Alternative Package
- **Candidates**: [List alternative packages]
- **Comparison**: [Feature parity, security posture]
- **Migration Cost**: [Estimated hours]

#### Option 3: Vendor Patch + Monitoring
- **Action**: Apply custom patch, monitor for official fix
- **Risk**: Technical debt, maintenance burden
- **Use Case**: If {fixed_version} has breaking changes

### Detection & Monitoring

#### SBOM (Software Bill of Materials):
```json
{{
  "bomFormat": "CycloneDX",
  "components": [
    {{
      "name": "{package}",
      "version": "{version}",
      "purl": "pkg:npm/{package}@{version}",
      "cpe": "[CPE if available]"
    }}
  ],
  "vulnerabilities": [
    {{
      "id": "{cve_id}",
      "source": "NVD"
    }}
  ]
}}
```

#### Continuous Monitoring:
```yaml
# GitHub Advanced Security
dependency-review:
  fail-on-severity: high
  allow-licenses:
    - MIT
    - Apache-2.0
  deny-licenses:
    - GPL-3.0
```

### Compliance Framework Mapping

#### NIST CSF:
[Detailed control mappings with evidence requirements]

#### ISO 27001:
[Annex A controls with implementation guidance]

#### SSDF (Secure Software Development Framework):
- **PO.3.2**: "Store and protect the integrity of third-party code"
- **PO.5.1**: "Gather and safeguard relevant data on software components"

### Incident Response Plan

#### If Exploitation Detected:
1. **Containment** (0-30 min):
   - Disable affected services
   - Block network egress from affected systems
   - Preserve logs and memory dumps

2. **Investigation** (30 min - 4 hours):
   - Review application logs for {cve_id} exploitation patterns
   - Check for data exfiltration
   - Identify scope of compromise

3. **Remediation** (4+ hours):
   - Deploy emergency patch
   - Rotate credentials
   - Restore from clean backups if needed

### Automation & Tooling

#### CI/CD Pipeline Integration:
```yaml
# .github/workflows/security-scan.yml
- name: Dependency Scan
  run: |
    npm audit --audit-level=high
    trivy fs --severity HIGH,CRITICAL .
    syft . -o cyclonedx > sbom.json
    grype sbom:sbom.json --fail-on high
```

#### Pre-commit Hooks:
```bash
#!/bin/bash
# Check for known vulnerabilities before commit
npm audit --audit-level=moderate
if [ $? -ne 0 ]; then
  echo "❌ Vulnerable dependencies detected!"
  exit 1
fi
```

### Metrics & KPIs

#### Target SLAs:
- **Critical CVEs**: Patched within 24 hours
- **High CVEs**: Patched within 7 days
- **Medium CVEs**: Patched within 30 days
- **SBOM Currency**: Updated on every build

#### Success Criteria:
- [ ] Zero known CVEs in production dependencies
- [ ] 100% SBOM coverage
- [ ] Automated alerts for new CVEs
- [ ] Dependency update SLA compliance > 95%

### Cost-Benefit Analysis

**Cost of Update**:
- Development: 4 hours × $[rate] = $[amount]
- Testing: 2 hours × $[rate] = $[amount]
- Deployment: 1 hour × $[rate] = $[amount]
- **Total**: $[amount]

**Cost of Breach**:
- Average data breach: $4.35M (IBM 2023)
- Dependency vulnerability exploitation: ~$500K-$2M
- Regulatory fines: [Relevant to industry]
- **ROI**: [Massive positive ROI]

### References

- **CVE**: https://nvd.nist.gov/vuln/detail/{cve_id}
- **Package Advisory**: [GitHub/npm advisory URL]
- **Snyk Database**: https://security.snyk.io/vuln/{cve_id}
- **NIST SSDF**: https://csrc.nist.gov/Projects/ssdf
- **SBOM Spec**: https://cyclonedx.org/"""

    @staticmethod
    def get_beginner_dast_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """DAST Policy Prompt for Beginners - Web security basics"""
        title = vulnerability.get('alert') or vulnerability.get('name', 'Web Vulnerability')
        url = vulnerability.get('url', '')
        method = vulnerability.get('method', 'GET')
        risk = vulnerability.get('risk_level', 'Medium')
        description = vulnerability.get('description', '')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a beginner-friendly web security policy.

{user_context}

WEB VULNERABILITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue: {title}
URL: {url}
Method: {method}
Risk: {risk}
Description: {description}

COMPLIANCE CONTEXT:
{compliance_context}

FORMAT YOUR RESPONSE AS:

## 🌐 Understanding Web Security

### What is {title}?
[Explain in simple terms what this web vulnerability is]

### Why is it Dangerous on Websites?
[Explain the risk for web applications specifically]

### Real Example:
[Show how an attacker could exploit this on a website]

## 🔧 How to Fix It

### Current Setup (Vulnerable):
[Describe the current insecure configuration]

### Secure Configuration:
[Step-by-step instructions to fix]

### Code Example:
```
[Show before/after code for web framework]
```

## ✅ Testing Your Fix

### Manual Test:
1. [Step-by-step testing instructions]
2. Use browser developer tools to verify

### Automated Test:
```
[Simple test script]
```

## 🎓 Learn More

- OWASP Guide: [Link]
- Web Security Basics: [Link]
- Browser Security Features: [Link]

## 📋 Compliance

This fix helps meet:
[NIST and ISO controls from context]

## ⏰ Timeline

Risk: {risk}
Time: [Estimate]
Priority: [Based on risk]"""

    @staticmethod
    def get_intermediate_dast_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """DAST Policy Prompt for Intermediate - Web app security"""
        title = vulnerability.get('alert') or vulnerability.get('name', 'Web Vulnerability')
        url = vulnerability.get('url', '')
        method = vulnerability.get('method', 'GET')
        risk = vulnerability.get('risk_level', 'Medium')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a web application security policy for SENIOR DEVELOPERS.

{user_context}

WEB VULNERABILITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue: {title}
Endpoint: {url}
HTTP Method: {method}
Risk Level: {risk}

COMPLIANCE CONTEXT:
{compliance_context}

FORMAT YOUR RESPONSE AS:

## Policy: {title} Prevention

### Vulnerability Analysis
**Endpoint**: {url}
**Method**: {method}
**Risk**: {risk}
**Attack Vector**: [How this is typically exploited]

### Technical Remediation

#### Web Framework Configuration:
[Framework-specific security settings]

#### HTTP Headers:
```
[Required security headers]
Content-Security-Policy: ...
X-Frame-Options: DENY
...
```

#### Implementation Example:
```javascript
// Express.js / Django / Flask example
[Code showing secure implementation]
```

### WAF Rule Configuration:
```
[ModSecurity or cloud WAF rule]
```

### Testing with OWASP ZAP:
```bash
zap-cli quick-scan {url}
```

### Compliance Mapping
[NIST and ISO controls]

### Timeline
Risk: {risk}
Effort: [Hours]
Deadline: [Date]"""

    @staticmethod
    def get_advanced_dast_prompt(vulnerability: Dict, compliance_context: str, user_profile: UserProfile) -> str:
        """DAST Policy Prompt for Advanced - WAF, monitoring, defense-in-depth"""
        title = vulnerability.get('alert') or vulnerability.get('name', 'Web Vulnerability')
        url = vulnerability.get('url', '')
        method = vulnerability.get('method', 'GET')
        risk = vulnerability.get('risk_level', 'Medium')

        user_context = user_profile.to_prompt_context() if user_profile else ""

        return f"""Generate a comprehensive web security policy for SECURITY ENGINEERS.

{user_context}

WEB VULNERABILITY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue: {title}
Endpoint: {url}
HTTP Method: {method}
Risk Level: {risk}

COMPLIANCE CONTEXT:
{compliance_context}

FORMAT YOUR RESPONSE AS:

## Web Application Security Policy: {title}

### Threat Assessment

#### Attack Surface:
- **Endpoint**: {url}
- **HTTP Method**: {method}
- **Authentication Required**: [Yes/No]
- **User Input Vectors**: [List all input points]

#### Threat Actor Profile:
- **Skill Level Required**: [Low/Medium/High]
- **Known Attack Tools**: [List tools that can exploit this]
- **Typical Goals**: [What attackers aim to achieve]

### Defense-in-Depth Strategy

#### Layer 1: Application Code
[Secure coding practices]

#### Layer 2: Web Application Firewall
```
# ModSecurity CRS Rule
[Actual WAF rule to block this attack]
```

#### Layer 3: Network Controls
[IP filtering, rate limiting, geo-blocking if relevant]

#### Layer 4: Monitoring & Detection
```python
# SIEM correlation rule (Splunk/ELK)
[Actual SIEM query to detect exploitation]
```

### WAF Configuration

#### AWS WAF:
```json
[AWS WAF rule JSON]
```

#### Cloudflare WAF:
```
[Cloudflare rule expression]
```

#### ModSecurity:
```
[ModSecurity rule]
```

### Incident Response

#### Detection Indicators:
- HTTP status code patterns
- Response time anomalies
- Error log patterns

#### Response Playbook:
[Detailed IR steps]

### Compliance Mapping

#### NIST CSF:
[Detailed controls with evidence]

#### ISO 27001:
[Annex A controls]

#### OWASP ASVS:
[Verification requirements]

#### PCI DSS (if applicable):
[Relevant requirements]

### Penetration Testing

#### Test Cases:
```bash
# OWASP ZAP Automation
[Actual ZAP script]
```

#### Nuclei Templates:
```yaml
# Custom Nuclei template
[YAML template for this vulnerability]
```

### Metrics & SLAs

**Detection SLA**: < 5 minutes
**Response SLA**: < 2 hours
**Remediation SLA**: [Based on risk]

### Budget & ROI
[Cost analysis]

### Timeline & Milestones
[Gantt chart in text]

### References
[Comprehensive reference list]"""

    @staticmethod
    def select_prompt(
        vulnerability_type: str,
        expertise_level: ExpertiseLevel,
        vulnerability: Dict,
        compliance_context: str,
        user_profile: UserProfile
    ) -> str:
        """
        Select appropriate prompt based on vulnerability type and user expertise

        Args:
            vulnerability_type: 'sast', 'sca', or 'dast'
            expertise_level: User's expertise level
            vulnerability: Vulnerability details
            compliance_context: RAG-retrieved compliance information
            user_profile: Complete user profile

        Returns:
            Formatted prompt string
        """
        prompt_map = {
            ('sast', ExpertiseLevel.BEGINNER): AdaptivePolicyPrompts.get_beginner_sast_prompt,
            ('sast', ExpertiseLevel.INTERMEDIATE): AdaptivePolicyPrompts.get_intermediate_sast_prompt,
            ('sast', ExpertiseLevel.ADVANCED): AdaptivePolicyPrompts.get_advanced_sast_prompt,
            ('sca', ExpertiseLevel.BEGINNER): AdaptivePolicyPrompts.get_beginner_sca_prompt,
            ('sca', ExpertiseLevel.INTERMEDIATE): AdaptivePolicyPrompts.get_intermediate_sca_prompt,
            ('sca', ExpertiseLevel.ADVANCED): AdaptivePolicyPrompts.get_advanced_sca_prompt,
            ('dast', ExpertiseLevel.BEGINNER): AdaptivePolicyPrompts.get_beginner_dast_prompt,
            ('dast', ExpertiseLevel.INTERMEDIATE): AdaptivePolicyPrompts.get_intermediate_dast_prompt,
            ('dast', ExpertiseLevel.ADVANCED): AdaptivePolicyPrompts.get_advanced_dast_prompt,
        }

        prompt_function = prompt_map.get(
            (vulnerability_type.lower(), expertise_level),
            AdaptivePolicyPrompts.get_intermediate_sast_prompt  # Default fallback
        )

        return prompt_function(vulnerability, compliance_context, user_profile)
