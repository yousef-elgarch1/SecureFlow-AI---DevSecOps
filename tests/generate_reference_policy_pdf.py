"""
Generate Reference Policy PDF for Compliance Testing
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime

def generate_reference_policy_pdf(output_path):
    """Generate a comprehensive reference policy PDF for SQL Injection"""

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)

    # Container for the 'Flowable' objects
    elements = []

    # Define custom styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
    )

    # Title
    elements.append(Paragraph("SECURITY POLICY SP-REF-001", title_style))
    elements.append(Paragraph("SQL Injection Prevention Policy", heading1_style))
    elements.append(Spacer(1, 0.2*inch))

    # Document metadata
    metadata = [
        ['Document ID:', 'SP-REF-001'],
        ['Version:', '1.0'],
        ['Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Classification:', 'Internal Use'],
        ['Owner:', 'Information Security Team']
    ]

    metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))

    # 1. EXECUTIVE SUMMARY
    elements.append(Paragraph("1. EXECUTIVE SUMMARY", heading1_style))
    elements.append(Paragraph(
        "This security policy establishes mandatory requirements for preventing SQL injection "
        "vulnerabilities in all software applications developed, maintained, or deployed by the organization. "
        "SQL injection represents one of the most critical web application security risks, capable of "
        "compromising data confidentiality, integrity, and availability. This policy mandates the use of "
        "parameterized queries, input validation, and secure coding practices across all database interactions.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))

    # 2. PURPOSE
    elements.append(Paragraph("2. PURPOSE", heading1_style))
    elements.append(Paragraph(
        "The purpose of this policy is to:",
        body_style
    ))

    purpose_items = [
        "Eliminate SQL injection vulnerabilities from all application codebases",
        "Establish secure coding standards for database interactions",
        "Ensure compliance with industry security frameworks and regulations",
        "Protect sensitive data from unauthorized access, modification, or deletion",
        "Maintain the integrity and availability of database systems"
    ]

    for item in purpose_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.15*inch))

    # 3. SCOPE
    elements.append(Paragraph("3. SCOPE", heading1_style))
    elements.append(Paragraph(
        "This policy applies to:",
        body_style
    ))

    scope_items = [
        "All web applications, APIs, and services that interact with databases",
        "All software development teams and contractors",
        "Legacy applications undergoing maintenance or updates",
        "Third-party integrations that perform database queries",
        "Development, staging, and production environments"
    ]

    for item in scope_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.15*inch))

    # 4. RISK STATEMENT
    elements.append(Paragraph("4. RISK STATEMENT", heading1_style))
    elements.append(Paragraph(
        "SQL injection vulnerabilities allow attackers to execute arbitrary database queries through "
        "unsanitized user input, potentially leading to:",
        body_style
    ))

    risk_items = [
        "Unauthorized data access: Retrieval of sensitive customer data, credentials, and intellectual property",
        "Data modification: Alteration or deletion of critical business data",
        "Authentication bypass: Circumventing login mechanisms and access controls",
        "Privilege escalation: Gaining administrative access to database systems",
        "System compromise: Executing operating system commands in certain database configurations"
    ]

    for item in risk_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Paragraph(
        "The impact of successful SQL injection attacks can result in regulatory penalties, "
        "reputational damage, financial loss, and legal liability.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))

    # 5. POLICY STATEMENT
    elements.append(Paragraph("5. POLICY STATEMENT", heading1_style))
    elements.append(Paragraph(
        "All database interactions must implement the following mandatory security controls:",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("5.1 Parameterized Queries", heading2_style))
    elements.append(Paragraph(
        "All SQL queries must use parameterized statements or prepared statements. String concatenation "
        "of user input into SQL queries is strictly prohibited. Use of Object-Relational Mapping (ORM) "
        "frameworks with parameterized queries is recommended.",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("5.2 Input Validation", heading2_style))
    elements.append(Paragraph(
        "Implement strict input validation on all user-supplied data before database operations. "
        "Validation must include type checking, length restrictions, format verification, and "
        "whitelisting of acceptable characters. Reject invalid input rather than attempting sanitization.",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("5.3 Least Privilege Access", heading2_style))
    elements.append(Paragraph(
        "Database accounts used by applications must follow the principle of least privilege. "
        "Grant only the minimum permissions necessary for application functionality. Avoid using "
        "administrative or root database accounts in application connections.",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("5.4 Error Handling", heading2_style))
    elements.append(Paragraph(
        "Database error messages must not expose sensitive information such as table names, column names, "
        "or query structure. Implement generic error messages for end users while logging detailed "
        "errors securely for debugging purposes.",
        body_style
    ))
    elements.append(Spacer(1, 0.15*inch))

    # Page break
    elements.append(PageBreak())

    # 6. COMPLIANCE MAPPING
    elements.append(Paragraph("6. COMPLIANCE MAPPING", heading1_style))
    elements.append(Paragraph(
        "This policy aligns with the following security frameworks and standards:",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    compliance_data = [
        ['Framework', 'Control ID', 'Control Title'],
        ['NIST CSF', 'PR.DS-5', 'Protections against data leaks are implemented'],
        ['NIST CSF', 'PR.AC-4', 'Access permissions and authorizations are managed'],
        ['NIST CSF', 'DE.CM-1', 'The network is monitored to detect potential cybersecurity events'],
        ['ISO 27001', 'A.14.2.5', 'Secure system engineering principles'],
        ['ISO 27001', 'A.8.22', 'Segregation in networks'],
        ['ISO 27001', 'A.8.3', 'Handling of assets'],
        ['OWASP Top 10', 'A03:2021', 'Injection'],
        ['PCI DSS', '6.5.1', 'Injection flaws, particularly SQL injection']
    ]

    compliance_table = Table(compliance_data, colWidths=[1.5*inch, 1.2*inch, 3.3*inch])
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(compliance_table)
    elements.append(Spacer(1, 0.2*inch))

    # 7. REMEDIATION PLAN
    elements.append(Paragraph("7. REMEDIATION PLAN", heading1_style))
    elements.append(Paragraph(
        "Upon detection of SQL injection vulnerabilities, the following remediation process must be executed:",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    remediation_data = [
        ['Phase', 'Action', 'Timeline', 'Responsible Party'],
        ['1. Immediate', 'Notify security team and development lead', '0-2 hours', 'Security Operations'],
        ['2. Assessment', 'Analyze vulnerability scope and impact', '2-8 hours', 'AppSec Team'],
        ['3. Mitigation', 'Deploy WAF rules if immediate fix not possible', '8-12 hours', 'Security Engineering'],
        ['4. Development', 'Implement parameterized queries in code', '24-48 hours', 'Development Team'],
        ['5. Testing', 'Conduct code review and security testing', '48-72 hours', 'QA & Security'],
        ['6. Deployment', 'Deploy fix to production environment', '72-96 hours', 'DevOps Team'],
        ['7. Verification', 'Re-scan and validate vulnerability closed', '96-120 hours', 'Security Operations']
    ]

    remediation_table = Table(remediation_data, colWidths=[1*inch, 2.2*inch, 1.2*inch, 1.6*inch])
    remediation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(remediation_table)
    elements.append(Spacer(1, 0.2*inch))

    # 8. ROLES AND RESPONSIBILITIES
    elements.append(Paragraph("8. ROLES AND RESPONSIBILITIES", heading1_style))

    roles_data = [
        ['Role', 'Responsibilities'],
        ['Development Team', '• Implement parameterized queries in all code\n• Follow secure coding standards\n• Conduct peer code reviews'],
        ['Security Team', '• Perform vulnerability assessments\n• Provide security training\n• Monitor for SQL injection attempts'],
        ['QA Team', '• Test for SQL injection vulnerabilities\n• Validate remediation effectiveness\n• Verify compliance with policy'],
        ['DevOps Team', '• Deploy security patches promptly\n• Configure WAF rules\n• Maintain audit logging'],
        ['Management', '• Allocate resources for security initiatives\n• Enforce policy compliance\n• Review policy effectiveness quarterly']
    ]

    roles_table = Table(roles_data, colWidths=[1.8*inch, 4.2*inch])
    roles_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fadbd8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(roles_table)
    elements.append(Spacer(1, 0.2*inch))

    # Page break
    elements.append(PageBreak())

    # 9. MONITORING AND DETECTION
    elements.append(Paragraph("9. MONITORING AND DETECTION", heading1_style))
    elements.append(Paragraph(
        "The following monitoring controls must be implemented to detect SQL injection attempts:",
        body_style
    ))

    monitoring_items = [
        "Web Application Firewall (WAF): Deploy WAF rules to detect and block SQL injection patterns in real-time",
        "Database Activity Monitoring (DAM): Implement DAM solutions to track and alert on suspicious query patterns",
        "SIEM Integration: Forward security logs to SIEM for correlation and alerting on injection attempts",
        "Automated Scanning: Conduct quarterly SAST and DAST scans to identify vulnerabilities",
        "Penetration Testing: Perform annual penetration testing focused on injection vulnerabilities",
        "Security Logging: Enable comprehensive logging of all database queries and access attempts"
    ]

    for item in monitoring_items:
        parts = item.split(':', 1)
        if len(parts) == 2:
            elements.append(Paragraph(f"<b>{parts[0]}:</b>{parts[1]}", body_style))
        else:
            elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.15*inch))

    # 10. SUCCESS CRITERIA
    elements.append(Paragraph("10. SUCCESS CRITERIA", heading1_style))
    elements.append(Paragraph(
        "Policy effectiveness will be measured by the following success criteria:",
        body_style
    ))

    success_items = [
        "Zero SQL injection vulnerabilities detected in production environments",
        "100% of database queries use parameterized statements (verified through code audits)",
        "All developers complete secure coding training annually",
        "WAF successfully blocks 100% of simulated SQL injection attacks during testing",
        "Database access follows least privilege principle (verified through access reviews)",
        "No security incidents related to SQL injection in the past 12 months"
    ]

    for item in success_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.15*inch))

    # 11. ENFORCEMENT
    elements.append(Paragraph("11. ENFORCEMENT", heading1_style))
    elements.append(Paragraph(
        "Non-compliance with this policy may result in:",
        body_style
    ))

    enforcement_items = [
        "Code deployment blocked until vulnerabilities are remediated",
        "Mandatory security training for development team members",
        "Escalation to management for repeated violations",
        "Performance review implications for persistent non-compliance",
        "Termination of vendor contracts for third-party violations"
    ]

    for item in enforcement_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.15*inch))

    # 12. REVIEW AND UPDATES
    elements.append(Paragraph("12. REVIEW AND UPDATES", heading1_style))
    elements.append(Paragraph(
        "This policy will be reviewed and updated:",
        body_style
    ))

    review_items = [
        "Annually by the Information Security team",
        "Following any security incident related to SQL injection",
        "When significant changes occur to application architecture",
        "Upon updates to compliance frameworks (NIST CSF, ISO 27001, etc.)",
        "Based on feedback from development teams and security assessments"
    ]

    for item in review_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.2*inch))

    # 13. REFERENCES
    elements.append(Paragraph("13. REFERENCES", heading1_style))

    references_items = [
        "OWASP Top 10 2021: A03 Injection - https://owasp.org/Top10/A03_2021-Injection/",
        "NIST Cybersecurity Framework v1.1",
        "ISO/IEC 27001:2022 - Information security management",
        "PCI DSS v4.0 - Payment Card Industry Data Security Standard",
        "CWE-89: SQL Injection - https://cwe.mitre.org/data/definitions/89.html",
        "OWASP SQL Injection Prevention Cheat Sheet"
    ]

    for item in references_items:
        elements.append(Paragraph(f"• {item}", body_style))

    elements.append(Spacer(1, 0.3*inch))

    # Footer
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("_" * 80, body_style))
    elements.append(Paragraph(
        f"<b>Document Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        "<b>Classification:</b> Internal Use Only<br/>"
        "<b>Approved By:</b> Chief Information Security Officer",
        body_style
    ))

    # Build PDF
    doc.build(elements)
    print(f"[OK] Reference policy PDF generated: {output_path}")

if __name__ == "__main__":
    output_file = "data/sample_reports/sql_injection_reference_policy.pdf"
    generate_reference_policy_pdf(output_file)
    print(f"\n[OK] PDF file created successfully at: {output_file}")
    print("\nThis PDF can be uploaded to the compliance test feature to validate generated policies.")
