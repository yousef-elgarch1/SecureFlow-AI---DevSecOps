# Mock Security Reports for Testing

This directory contains realistic mock security reports for testing the AI Security Policy Generator platform.

## Files

### 1. mock_sast_report.json
**Type:** Static Application Security Testing (SAST)
**Format:** Semgrep JSON output
**Vulnerabilities:** 8 findings

**Includes:**
- SQL Injection (ERROR - High severity)
- Cross-Site Scripting (WARNING - Medium severity)
- Path Traversal (ERROR - High severity)
- Session Cookie Misconfiguration (WARNING - Medium severity)
- Hardcoded Secrets (ERROR - Critical severity)
- Code Injection (ERROR - Critical severity)
- Open Redirect (WARNING - Medium severity)
- Weak Cryptographic Random (WARNING - Medium severity)

**CWE Coverage:**
- CWE-89: SQL Injection
- CWE-79: Cross-site Scripting
- CWE-22: Path Traversal
- CWE-1004: Cookie Without HttpOnly
- CWE-798: Hard-coded Credentials
- CWE-94: Code Injection
- CWE-601: Open Redirect
- CWE-330: Insufficient Randomness

### 2. mock_sca_report.json
**Type:** Software Composition Analysis (SCA)
**Format:** npm audit JSON output
**Vulnerabilities:** 11 package vulnerabilities

**Includes:**
- Prototype Pollution in lodash (High)
- Open Redirect in express (Medium)
- SSRF in axios (High)
- Insecure JWT defaults (Medium)
- Prototype Pollution in minimist (Critical)
- Prototype Pollution in qs (High)
- ReDoS in semver (Medium)
- SQL Injection in sqlite3 (Critical)
- Prototype Pollution in xml2js (Medium)
- SSRF in node-fetch (High)

**Severity Distribution:**
- Critical: 2
- High: 5
- Medium: 4
- Total: 11

### 3. mock_dast_report.xml
**Type:** Dynamic Application Security Testing (DAST)
**Format:** OWASP ZAP XML report
**Vulnerabilities:** 8 runtime findings

**Includes:**
- SQL Injection (High)
- Reflected XSS (High)
- Stored XSS (High)
- Missing CSRF Tokens (Medium)
- Weak Authentication (Medium)
- Cookie Without Secure Flag (Low)
- Missing Security Headers (Low)
- Information Disclosure (Low)
- Path Traversal (High)

**CWE Coverage:**
- CWE-89: SQL Injection
- CWE-79: Cross-site Scripting
- CWE-352: CSRF
- CWE-287: Weak Authentication
- CWE-614: Cookie Security
- CWE-693: Missing Security Headers
- CWE-200: Information Disclosure
- CWE-22: Path Traversal

## How to Use

### Upload to Frontend
1. Start the backend and frontend servers
2. Navigate to http://localhost:3000
3. Upload these files using the drag & drop interface:
   - **SAST Report:** `mock_sast_report.json`
   - **SCA Report:** `mock_sca_report.json`
   - **DAST Report:** `mock_dast_report.xml`
4. Click "Generate Security Policies"
5. Watch real-time processing
6. View generated policies with compliance mappings

### Test Individual Reports
You can upload any combination:
- Only SAST
- Only SCA
- Only DAST
- SAST + SCA
- SAST + DAST
- SCA + DAST
- All three (recommended for full testing)

### Expected Results

When all three reports are uploaded, the AI will generate:
- **27 security policies** (8 SAST + 11 SCA + 8 DAST)
- **Compliance mappings** to NIST CSF and ISO 27001
- **Quality metrics** (BLEU-4 and ROUGE-L scores)
- **Severity analysis** charts
- **Downloadable reports** in TXT and HTML formats

### Compliance Standards Covered

The generated policies will include mappings to:
- **NIST Cybersecurity Framework (CSF)**
  - Identify (ID)
  - Protect (PR)
  - Detect (DE)
  - Respond (RS)
  - Recover (RC)

- **ISO 27001:2013**
  - A.9: Access Control
  - A.12: Operations Security
  - A.13: Communications Security
  - A.14: System Acquisition, Development and Maintenance
  - A.18: Compliance

## Realistic Test Scenarios

### Scenario 1: Web Application Security Audit
Upload all three reports to simulate a comprehensive security assessment of a web application.

### Scenario 2: Dependency Vulnerability Assessment
Upload only `mock_sca_report.json` to focus on third-party library vulnerabilities.

### Scenario 3: Code Security Review
Upload only `mock_sast_report.json` to test static code analysis policy generation.

### Scenario 4: Penetration Testing Results
Upload only `mock_dast_report.xml` to simulate runtime vulnerability findings.

## Notes

- These are **realistic mock reports** based on common vulnerabilities
- All CWE IDs, OWASP categories, and severity levels are accurate
- The reports simulate findings from:
  - **Semgrep** for SAST
  - **npm audit** for SCA
  - **OWASP ZAP** for DAST
- File paths and code snippets are synthetic but representative
- All vulnerabilities are from OWASP Top 10 and common security issues

## Testing Checklist

- [ ] Backend API running on port 8000
- [ ] Frontend running on port 3000
- [ ] Upload SAST report
- [ ] Upload SCA report
- [ ] Upload DAST report
- [ ] Generate policies
- [ ] View real-time progress (4 phases)
- [ ] Check vulnerability counts displayed correctly
- [ ] View generated policies
- [ ] Verify compliance mappings present
- [ ] Check BLEU/ROUGE scores displayed
- [ ] Download TXT report
- [ ] Download HTML report
- [ ] Test with individual reports (not all three)
- [ ] Verify error handling (upload invalid file)

## Customization

To create your own test reports:
- **SAST:** Follow Semgrep JSON format
- **SCA:** Follow npm audit v2 format
- **DAST:** Follow OWASP ZAP XML format

See the existing files as templates.
