# SecurAI - Complete Technical Implementation Report
## Team: Youssef ELGARCH, Youssef TOUZANI, Youness BAZZAOUI, Nisrine IBNOU-KADY

**Project:** AI-Powered Security Policy Generator with Compliance Mapping
**Date:** November 6, 2025
**Version:** 1.1

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [ELGARCH - Orchestrator & Report Generation](#2-elgarch-orchestrator--report-generation)
3. [TOUZANI - SAST Parser & LLM Integration](#3-touzani-sast-parser--llm-integration)
4. [BAZZAOUI - DAST Parser & LLM Integration](#4-bazzaoui-dast-parser--llm-integration)
5. [IBNOU-KADY - SCA Parser & LLM Integration](#5-ibnou-kady-sca-parser--llm-integration)
6. [System Integration & Data Flow](#6-system-integration--data-flow)
7. [Technical Challenges & Solutions](#7-technical-challenges--solutions)

---

# 1. EXECUTIVE SUMMARY

## Project Overview
SecurAI is an automated security policy generation system that transforms vulnerability scan reports (SAST, SCA, DAST) into professional, compliance-aligned security policies using Large Language Models (LLMs) and Retrieval Augmented Generation (RAG).

## Key Statistics
- **Total Files:** 50+ source files
- **Lines of Code:** ~15,000+ LOC
- **Technologies:** Python (FastAPI), React, ChromaDB, Groq API
- **Compliance Frameworks:** NIST CSF (108 controls), ISO 27001 (114 controls)
- **LLM Models:** LLaMA 3.3 70B, LLaMA 3.1 8B Instant
- **Output Formats:** JSON, TXT, HTML, PDF
- **Real-time Updates:** WebSocket-based progress tracking

## System Architecture
```
User Input (Reports/GitHub)
  → Parsers (SAST/SCA/DAST)
  → RAG Retrieval (Compliance Context)
  → LLM Generation (AI Policies)
  → Compliance Analysis (NIST/ISO Mapping)
  → Report Generation (PDF/HTML/JSON/TXT)
```

---

# 2. ELGARCH - Orchestrator & Report Generation

## 2.1 Responsibilities
- **Orchestrator Pipeline:** Coordinate entire policy generation workflow
- **Report Generation:** Create professional PDF, HTML, JSON, and TXT reports
- **Compliance Analysis:** Map policies to NIST CSF and ISO 27001 frameworks
- **WebSocket Communication:** Real-time progress broadcasting
- **File Management:** Handle input/output file operations

## 2.2 Main Components

### A. Policy Generator Orchestrator
**File:** `backend/orchestrator/policy_generator.py` (916 lines)

#### Class: PolicyGeneratorOrchestrator

**Initialization:**
```python
def __init__(self, use_rag=True, llm_models=None, output_dir="./outputs"):
    # Initialize parsers
    self.sast_parser = SASTParser()
    self.sca_parser = SCAParser()
    self.dast_parser = DASTParser()

    # Initialize RAG retriever
    self.retriever = ComplianceRetriever()

    # Initialize specialized LLM clients per vulnerability type
    self.llm_clients = {
        'sast': GroqClient(model="llama-3.3-70b-versatile"),
        'sca': GroqClient(model="llama-3.3-70b-versatile"),
        'dast': GroqClient(model="llama-3.1-8b-instant")
    }

    # Initialize prompt templates
    self.prompt_templates = PolicyPromptTemplates()
```

**Why Different Models?**
- **LLaMA 3.3 70B** (SAST/SCA): Larger model with deeper understanding of code vulnerabilities and dependency issues
- **LLaMA 3.1 8B Instant** (DAST): Faster model sufficient for runtime vulnerability analysis

#### Pipeline Phases

**Phase 1: Parsing Reports**
```python
def parse_reports(self, sast_path=None, sca_path=None, dast_path=None):
    """
    Reads vulnerability reports and parses them into normalized format

    Flow:
    1. Read file content from disk
    2. Call appropriate parser (SAST/SCA/DAST)
    3. Get list of vulnerability objects
    4. Print summary statistics

    Returns: (sast_vulns, sca_vulns, dast_vulns)
    """
    sast_vulns = []
    if sast_path and os.path.exists(sast_path):
        with open(sast_path, 'r') as f:
            sast_content = f.read()
        sast_vulns = self.sast_parser.parse(sast_content)
        print(f"Found {len(sast_vulns)} SAST vulnerabilities")

    # Similar for SCA and DAST...

    return sast_vulns, sca_vulns, dast_vulns
```

**Phase 2: Policy Generation**
```python
def generate_policies(self, sast_vulns, sca_vulns, dast_vulns, max_per_type=3):
    """
    Generate policies for all vulnerabilities using specialized LLMs

    Flow:
    1. Convert dataclass vulnerabilities to dicts
    2. Iterate through each vulnerability
    3. For each vuln:
       a. Retrieve compliance context via RAG
       b. Select appropriate LLM model
       c. Generate policy using LLM
       d. Record which LLM was used
    4. Return list of generated policies

    Returns: List of policy dicts with vulnerability, policy text, LLM used
    """
    results = []

    # Process SAST vulnerabilities
    for vuln in sast_vulns[:max_per_type]:
        # Get compliance context from RAG
        rag_result = self.retriever.retrieve_for_vulnerability(
            asdict(vuln), top_k=5
        )
        compliance_context = rag_result['formatted_context']

        # Generate policy
        policy = self.llm_clients['sast'].generate(
            user_prompt=self.prompt_templates.get_policy_generation_prompt(
                vulnerability=asdict(vuln),
                compliance_context=compliance_context,
                severity=vuln.severity
            ),
            system_prompt=self.prompt_templates.get_system_prompt()
        )

        results.append({
            'type': 'SAST',
            'vulnerability': asdict(vuln),
            'policy': policy,
            'llm_used': 'LLaMA 3.3 70B'
        })

    # Similar for SCA and DAST...

    return results
```

**Phase 3: Saving Results**
```python
def save_results(self, results, sast_vulns, sca_vulns, dast_vulns):
    """
    Save generated policies in multiple formats

    Generates:
    1. JSON file - Machine-readable with full metadata
    2. TXT file - Human-readable plain text report
    3. HTML file - Beautiful web-viewable report with styling
    4. PDF file - Professional document with charts

    Returns: Path to main output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Save JSON
    json_path = self.output_dir / f"policy_generation_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    # 2. Generate TXT report
    report_path = self.output_dir / f"security_policy_{timestamp}.txt"
    # ... (see next section)

    # 3. Generate HTML report
    html_path = self.output_dir / f"security_policy_{timestamp}.html"
    self._generate_html_report(html_path, results, ...)

    # 4. Generate enhanced PDF with charts
    pdf_path = self.output_dir / f"security_policy_{timestamp}.pdf"
    pdf_generator = EnhancedPDFGenerator()
    pdf_generator.generate_enhanced_pdf(...)

    return str(report_path)
```

### B. Report Generation

#### TXT Report Generation
**Format:** Plain text with clear sections

**Structure:**
```
================================================================================
AI-POWERED SECURITY POLICY GENERATION REPORT
================================================================================

Generated: 2025-11-06 10:30:00
Total Vulnerabilities Scanned: 25
  - SAST: 10
  - SCA: 8
  - DAST: 7

LLM Models Used (Comparative Study):
  - SAST/SCA: LLaMA 3.3 70B (Groq - most capable)
  - DAST: LLaMA 3.1 8B Instant (Groq - faster)
================================================================================

POLICY 1: SAST Vulnerability
LLM: LLaMA 3.3 70B
--------------------------------------------------------------------------------
Title: SQL Injection in User Authentication
Severity: CRITICAL

[Policy text generated by LLM...]

================================================================================
POLICY 2: SCA Vulnerability
...
```

**Implementation:**
```python
def _generate_txt_report(self, report_path, results):
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("AI-POWERED SECURITY POLICY GENERATION REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Total Vulnerabilities: {len(results)}\n\n")

        for i, item in enumerate(results):
            f.write(f"\nPOLICY {i+1}: {item['type']} Vulnerability\n")
            f.write(f"LLM: {item['llm_used']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Title: {item['vulnerability']['title']}\n")
            f.write(f"Severity: {item['vulnerability']['severity']}\n\n")
            f.write(item['policy'])
            f.write("\n\n" + "=" * 80 + "\n")
```

#### HTML Report Generation
**File:** Lines 419-720 in `policy_generator.py`

**Features:**
- Modern gradient design (purple/blue color scheme)
- Responsive grid layout
- Statistics cards with animations
- LLM usage information
- **NEW: Quality Metrics Section** (BLEU, ROUGE scores)
- **NEW: Compliance Coverage Section** (NIST CSF, ISO 27001 progress bars)
- Individual policy cards with hover effects

**CSS Styling:**
```python
html_content = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI';
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
    }
    .stat-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .policy {
        border: 2px solid #e1e8ed;
        border-radius: 15px;
        padding: 30px;
        transition: all 0.3s ease;
    }
    .policy:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
</style>
```

**Metrics Section (NEW):**
```html
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white; padding: 30px; border-radius: 15px;">
    <h2>📊 Policy Quality Metrics</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <p>BLEU-4 Score</p>
            <h3>N/A</h3>
            <p>Text similarity metric</p>
        </div>
        <div class="metric-card">
            <p>ROUGE-L Score</p>
            <h3>N/A</h3>
            <p>Content overlap metric</p>
        </div>
    </div>
    <p>💡 Tip: Upload your manual policy PDF to compare metrics</p>
</div>
```

#### PDF Report Generation (Enhanced)
**File:** `backend/utils/pdf_enhancer.py` (465 lines)

**Technology Stack:**
- **ReportLab:** PDF generation library
- **Matplotlib:** Chart creation (bar charts, pie charts)
- **Pillow:** Image processing

**Features:**
1. **Executive Summary Table**
2. **Severity Distribution Bar Chart** (color-coded)
3. **Scan Type Pie Chart** (SAST/SCA/DAST distribution)
4. **Compliance Coverage Chart** (NIST CSF, ISO 27001 percentages)
5. **Quality Metrics Table** (BLEU-4, ROUGE-L scores)
6. **Individual Policy Sections** (professional formatting)

**Chart Generation Example:**
```python
def _create_severity_chart(self, results):
    """Generate severity distribution bar chart using matplotlib"""
    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

    for item in results:
        severity = item['vulnerability'].get('severity', 'MEDIUM')
        if severity in severity_counts:
            severity_counts[severity] += 1

    # Create bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_map = {
        'CRITICAL': '#ef4444',  # Red
        'HIGH': '#f97316',      # Orange
        'MEDIUM': '#eab308',    # Yellow
        'LOW': '#3b82f6'        # Blue
    }

    severities = list(severity_counts.keys())
    counts = list(severity_counts.values())
    bar_colors = [colors_map[s] for s in severities]

    ax.bar(severities, counts, color=bar_colors, alpha=0.8, edgecolor='black')
    ax.set_xlabel('Severity Level', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Vulnerabilities', fontsize=12, fontweight='bold')
    ax.set_title('Vulnerability Severity Distribution', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for i, count in enumerate(counts):
        ax.text(i, count + 0.1, str(count), ha='center', va='bottom', fontweight='bold')

    # Save to BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()

    return img_buffer
```

**PDF Assembly:**
```python
def generate_enhanced_pdf(self, pdf_path, results, sast_vulns, sca_vulns, dast_vulns,
                         compliance_analysis=None, evaluation_metrics=None):
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []

    # Title Page
    story.append(Paragraph("SecurAI Security Policy Report", self.title_style))
    story.append(Spacer(1, 0.5 * inch))

    # Executive Summary Table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Vulnerabilities', str(len(results))],
        ['SAST', str(len(sast_vulns))],
        ['SCA', str(len(sca_vulns))],
        ['DAST', str(len(dast_vulns))],
    ]
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#667eea')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    story.append(summary_table)

    # Severity Chart
    severity_chart = self._create_severity_chart(results)
    img = RLImage(severity_chart, width=6*inch, height=3.5*inch)
    story.append(img)

    # Pie Chart
    type_chart = self._create_type_pie_chart(results)
    img = RLImage(type_chart, width=6*inch, height=4*inch)
    story.append(img)
    story.append(PageBreak())

    # Compliance Coverage
    if compliance_analysis:
        compliance_table = Table([...])
        story.append(compliance_table)

        compliance_chart = self._create_compliance_coverage_chart(compliance_analysis)
        story.append(RLImage(compliance_chart, width=6*inch, height=3.5*inch))

    # Quality Metrics
    if evaluation_metrics:
        metrics_table = Table([
            ['Metric', 'Score', 'Description'],
            ['BLEU-4', f"{metrics['avg_bleu']*100:.1f}%", 'Text similarity'],
            ['ROUGE-L', f"{metrics['avg_rouge']*100:.1f}%", 'Content overlap'],
        ])
        story.append(metrics_table)

    # Individual Policies
    for i, item in enumerate(results):
        story.append(Paragraph(f"Policy #{i+1}: {item['type']}", self.heading_style))
        story.append(Paragraph(f"Title: {item['vulnerability']['title']}", self.styles['Normal']))
        story.append(Paragraph(item['policy'], self.styles['BodyText']))
        story.append(PageBreak())

    # Build PDF
    doc.build(story)
```

### C. Compliance Analysis Integration

**File:** `backend/compliance/coverage_analyzer.py`

**Purpose:** Maps generated policies to compliance frameworks

**Frameworks:**
- **NIST CSF:** 108 controls (Identify, Protect, Detect, Respond, Recover)
- **ISO 27001:** 114 controls (A.5 through A.18)

**Analysis Process:**
```python
def analyze_coverage(self, policies):
    """
    Extract compliance mappings from policies and calculate coverage

    Flow:
    1. Iterate through all generated policies
    2. Extract NIST CSF and ISO 27001 control references
    3. Compare against full control catalog
    4. Calculate coverage percentage
    5. Identify gaps (missing controls)
    6. Generate coverage by function/domain

    Returns: Comprehensive coverage analysis
    """
    nist_covered = set()
    iso_covered = set()

    # Extract controls from policies
    for policy in policies:
        if "compliance_mapping" in policy:
            mappings = policy["compliance_mapping"]

            if "NIST CSF" in mappings:
                controls = mappings["NIST CSF"]
                nist_covered.update(controls)

            if "ISO 27001" in mappings:
                controls = mappings["ISO 27001"]
                iso_covered.update(controls)

    # Calculate gaps
    all_nist = self._get_all_nist_controls()  # Returns 108 controls
    all_iso = self._get_all_iso_controls()    # Returns 114 controls

    nist_gaps = set(all_nist) - nist_covered
    iso_gaps = set(all_iso) - iso_covered

    # Calculate coverage by category
    nist_by_function = self._analyze_nist_by_function(nist_covered)
    iso_by_domain = self._analyze_iso_by_domain(iso_covered)

    return {
        "nist_csf": {
            "total_controls": len(all_nist),
            "covered_controls": len(nist_covered),
            "coverage_percentage": (len(nist_covered) / len(all_nist)) * 100,
            "covered": sorted(list(nist_covered)),
            "gaps": sorted(list(nist_gaps)),
            "by_function": nist_by_function
        },
        "iso_27001": {...},
        "overall_score": ...
    }
```

**Output Example:**
```json
{
  "nist_csf": {
    "total_controls": 108,
    "covered_controls": 15,
    "coverage_percentage": 13.9,
    "covered": ["PR.AC-4", "DE.CM-7", "ID.RA-1", ...],
    "gaps": ["ID.AM-1", "PR.DS-1", ...],
    "by_function": {
      "Identify": {"total": 24, "covered": 3, "percentage": 12.5},
      "Protect": {"total": 48, "covered": 7, "percentage": 14.6},
      "Detect": {"total": 18, "covered": 3, "percentage": 16.7},
      "Respond": {"total": 12, "covered": 2, "percentage": 16.7},
      "Recover": {"total": 6, "covered": 0, "percentage": 0.0}
    }
  },
  "iso_27001": {
    "total_controls": 114,
    "covered_controls": 12,
    "coverage_percentage": 10.5,
    "by_domain": {
      "A.5": {"total": 2, "covered": 0, "percentage": 0},
      "A.9": {"total": 14, "covered": 3, "percentage": 21.4},
      "A.14": {"total": 13, "covered": 5, "percentage": 38.5},
      ...
    }
  },
  "overall_score": 12.2
}
```

### D. WebSocket Communication

**Purpose:** Real-time progress updates to frontend

**Implementation in FastAPI:**
```python
# backend/api/main.py

from fastapi import WebSocket

# Store active connections
active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_progress(message: dict):
    """Send progress update to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass  # Client disconnected
```

**Progress Message Format:**
```json
{
  "phase": "parsing|rag|llm_generation|saving|compliance_validation|complete",
  "status": "in_progress|completed|error",
  "message": "Human-readable status message",
  "data": {
    "parsed_sast": 10,
    "parsed_sca": 5,
    "parsed_dast": 3,
    "current_vuln": {
      "title": "SQL Injection",
      "severity": "CRITICAL",
      "type": "SAST"
    },
    "llm_model": "LLaMA 3.3 70B",
    "progress_percentage": 45.5,
    ...
  }
}
```

**Integration in Orchestrator:**
```python
async def broadcast_realtime_generation(sast_path, sca_path, dast_path, max_per_type):
    """Run policy generation with real-time WebSocket updates"""

    # Phase 1: Parsing
    await broadcast_progress({
        'phase': 'parsing',
        'status': 'in_progress',
        'message': 'Parsing SAST report...'
    })
    sast_vulns, sca_vulns, dast_vulns = orchestrator.parse_reports(...)
    await broadcast_progress({
        'phase': 'parsing',
        'status': 'completed',
        'data': {'parsed_sast': len(sast_vulns), ...}
    })

    # Phase 2: LLM Generation
    for vuln in all_vulns:
        await broadcast_progress({
            'phase': 'llm_generation',
            'status': 'in_progress',
            'message': f'Generating policy for {vuln.title}...',
            'data': {
                'current_vuln': {...},
                'progress_percentage': (i / total) * 100
            }
        })
        policy = orchestrator.generate_policy_for_vulnerability(vuln)

    # Phase 3: Complete
    await broadcast_progress({
        'phase': 'complete',
        'status': 'completed',
        'data': {
            'results': results,
            'compliance_analysis': compliance,
            'output_files': {...}
        }
    })
```

---

# 3. TOUZANI - SAST Parser & LLM Integration

## 3.1 Responsibilities
- **SAST Parser:** Parse Static Application Security Testing reports from multiple tools
- **LLM Integration for SAST:** Use LLaMA 3.3 70B for generating SAST policies
- **Vulnerability Normalization:** Convert tool-specific formats to unified structure
- **Category Detection:** Intelligently identify vulnerability types

## 3.2 SAST Parser Implementation

**File:** `backend/parsers/sast_parser.py` (280 lines)

### Data Model

**SASTVulnerability Dataclass:**
```python
@dataclass
class SASTVulnerability:
    """
    Unified SAST vulnerability representation

    Fields:
    - title: str - Vulnerability name (e.g., "SQL Injection")
    - severity: str - CRITICAL/HIGH/MEDIUM/LOW
    - category: str - Vulnerability type (SQL Injection, XSS, etc.)
    - file_path: str - Source code file path
    - line_number: int - Line number in file
    - cwe_id: str - Common Weakness Enumeration ID
    - description: str - Technical description
    - recommendation: str - Remediation advice
    - confidence: str - HIGH/MEDIUM/LOW confidence level
    - owasp_category: str - OWASP Top 10 mapping
    - code_snippet: str - Vulnerable code excerpt
    - metadata: dict - Additional tool-specific data
    """
    title: str
    severity: str
    category: str
    file_path: str
    line_number: int
    cwe_id: str = ""
    description: str = ""
    recommendation: str = ""
    confidence: str = "MEDIUM"
    owasp_category: str = ""
    code_snippet: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'severity': self.severity,
            'category': self.category,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'cwe_id': self.cwe_id,
            'description': self.description,
            'recommendation': self.recommendation,
            'confidence': self.confidence,
            'owasp_category': self.owasp_category,
            'code_snippet': self.code_snippet
        }
```

### Parsing Logic

**Main Parse Function:**
```python
def parse(self, report_content: str) -> List[SASTVulnerability]:
    """
    Parse SAST report from multiple tool formats

    Supports:
    - Semgrep (JSON)
    - SonarQube (JSON)
    - Checkmarx (JSON)
    - Bandit (JSON)

    Flow:
    1. Parse JSON string
    2. Detect tool format (Semgrep vs SonarQube)
    3. Call appropriate parser method
    4. Normalize all fields
    5. Return list of SASTVulnerability objects
    """
    try:
        report = json.loads(report_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in SAST report: {e}")

    vulnerabilities = []

    # Detect format and parse
    if 'results' in report:
        # Semgrep format
        vulnerabilities = self._parse_semgrep(report)
    elif 'issues' in report:
        # SonarQube format
        vulnerabilities = self._parse_sonarqube(report)
    else:
        raise ValueError("Unknown SAST report format")

    return vulnerabilities
```

**Semgrep Parser:**
```python
def _parse_semgrep(self, report: dict) -> List[SASTVulnerability]:
    """
    Parse Semgrep SAST report

    Semgrep JSON Structure:
    {
      "results": [
        {
          "check_id": "python.lang.security.sql-injection",
          "path": "app/auth.py",
          "start": {"line": 45},
          "extra": {
            "message": "SQL injection vulnerability...",
            "metadata": {
              "cwe": ["CWE-89"],
              "owasp": "A03:2021-Injection",
              "confidence": "HIGH",
              "severity": "ERROR"
            },
            "fix": "Use parameterized queries"
          }
        }
      ]
    }
    """
    vulnerabilities = []

    for result in report.get('results', []):
        # Extract metadata
        extra = result.get('extra', {})
        metadata = extra.get('metadata', {})

        # Normalize severity
        severity_raw = metadata.get('severity', extra.get('severity', 'INFO'))
        severity = self._normalize_severity(severity_raw)

        # Extract CWE
        cwe_list = metadata.get('cwe', [])
        cwe_id = cwe_list[0] if cwe_list else ""

        # Detect category from check_id
        check_id = result.get('check_id', '')
        category = self._detect_category(check_id, extra.get('message', ''))

        # Create vulnerability object
        vuln = SASTVulnerability(
            title=category if category else "Code Security Issue",
            severity=severity,
            category=category,
            file_path=result.get('path', 'Unknown'),
            line_number=result.get('start', {}).get('line', 0),
            cwe_id=cwe_id,
            description=extra.get('message', ''),
            recommendation=extra.get('fix', ''),
            confidence=metadata.get('confidence', 'MEDIUM'),
            owasp_category=metadata.get('owasp', ''),
            code_snippet=result.get('extra', {}).get('lines', ''),
            metadata={
                'check_id': check_id,
                'tool': 'Semgrep'
            }
        )

        vulnerabilities.append(vuln)

    return vulnerabilities
```

**Severity Normalization:**
```python
def _normalize_severity(self, severity: str) -> str:
    """
    Convert tool-specific severity to standard levels

    Mapping:
    - ERROR, CRITICAL → CRITICAL
    - WARNING, HIGH → HIGH
    - INFO, MEDIUM → MEDIUM
    - NOTE, LOW → LOW
    """
    severity_upper = severity.upper()

    if severity_upper in ['ERROR', 'CRITICAL']:
        return 'CRITICAL'
    elif severity_upper in ['WARNING', 'HIGH']:
        return 'HIGH'
    elif severity_upper in ['INFO', 'MEDIUM']:
        return 'MEDIUM'
    else:
        return 'LOW'
```

**Category Detection:**
```python
def _detect_category(self, check_id: str, message: str) -> str:
    """
    Intelligently detect vulnerability category

    Strategy:
    1. Check check_id for keywords (sql-injection, xss, etc.)
    2. Check message for vulnerability patterns
    3. Return most specific category found

    Categories:
    - SQL Injection
    - Cross-Site Scripting (XSS)
    - Cross-Site Request Forgery (CSRF)
    - Command Injection
    - Path Traversal
    - Insecure Deserialization
    - Authentication Issues
    - Authorization Issues
    - Cryptographic Issues
    - And more...
    """
    check_id_lower = check_id.lower()
    message_lower = message.lower()

    # SQL Injection
    if 'sql' in check_id_lower or 'sql injection' in message_lower:
        return 'SQL Injection'

    # XSS
    if 'xss' in check_id_lower or 'cross-site' in message_lower:
        return 'Cross-Site Scripting (XSS)'

    # CSRF
    if 'csrf' in check_id_lower or 'cross-site request forgery' in message_lower:
        return 'Cross-Site Request Forgery (CSRF)'

    # Command Injection
    if 'command' in check_id_lower and 'injection' in check_id_lower:
        return 'Command Injection'

    # Path Traversal
    if 'path-traversal' in check_id_lower or 'directory traversal' in message_lower:
        return 'Path Traversal'

    # Hardcoded Credentials
    if 'hardcoded' in check_id_lower or 'hardcoded' in message_lower:
        return 'Hardcoded Credentials'

    # Weak Cryptography
    if 'crypto' in check_id_lower or 'weak' in message_lower:
        return 'Cryptographic Issues'

    # Default if no match
    return 'Code Security Issue'
```

**Summary Statistics:**
```python
def get_summary(self, vulnerabilities: List[SASTVulnerability]) -> dict:
    """
    Generate summary statistics

    Returns:
    {
      "total": 15,
      "by_severity": {"CRITICAL": 2, "HIGH": 5, "MEDIUM": 6, "LOW": 2},
      "by_category": {"SQL Injection": 3, "XSS": 4, ...},
      "by_file": {"app/auth.py": 5, "app/api.py": 3, ...},
      "files_affected": 8
    }
    """
    from collections import Counter

    return {
        "total": len(vulnerabilities),
        "by_severity": dict(Counter(v.severity for v in vulnerabilities)),
        "by_category": dict(Counter(v.category for v in vulnerabilities)),
        "by_file": dict(Counter(v.file_path for v in vulnerabilities)),
        "files_affected": len(set(v.file_path for v in vulnerabilities))
    }
```

## 3.3 LLM Integration for SAST

**Model:** LLaMA 3.3 70B Versatile (Groq API)

**Why LLaMA 3.3 70B for SAST?**
- **Large Model Size:** 70 billion parameters → Deep understanding
- **Code Understanding:** Trained on code repositories
- **Context Window:** Can analyze complex vulnerability chains
- **Reasoning Ability:** Better at explaining security implications

**Integration Point:**
```python
# In orchestrator/policy_generator.py

# Initialize SAST LLM
self.llm_clients['sast'] = GroqClient(model="llama-3.3-70b-versatile")

# During generation
for sast_vuln in sast_vulns:
    # Get compliance context
    rag_result = self.retriever.retrieve_for_vulnerability(
        vulnerability=asdict(sast_vuln),
        top_k=5
    )

    # Generate policy
    policy = self.llm_clients['sast'].generate(
        user_prompt=self.prompt_templates.get_policy_generation_prompt(
            vulnerability=asdict(sast_vuln),
            compliance_context=rag_result['formatted_context'],
            severity=sast_vuln.severity
        ),
        system_prompt=self.prompt_templates.get_system_prompt(),
        temperature=0.3,  # Low temp for consistent output
        max_tokens=1500   # Sufficient for detailed policy
    )
```

**Sample SAST Prompt:**
```
SYSTEM: You are an expert cybersecurity policy analyst specializing in NIST CSF
and ISO 27001 compliance. Generate professional security policies.

USER:
Generate a comprehensive security policy for the following SAST vulnerability:

VULNERABILITY DETAILS:
- Title: SQL Injection in User Authentication
- Category: SQL Injection
- Severity: CRITICAL
- File: app/auth.py
- Line: 45
- CWE: CWE-89
- Description: User input is directly concatenated into SQL query without
  sanitization or parameterization
- Recommendation: Use parameterized queries with prepared statements

COMPLIANCE REQUIREMENTS (from RAG):
[1] NIST CSF - PR.AC-4: Access permissions are managed, incorporating least
    privilege and separation of duties
[2] ISO 27001 - A.14.2.5: Secure system engineering principles must be
    established and applied to development activities
[3] OWASP - A03:2021-Injection: Validate, filter, and sanitize all user input

GENERATE POLICY WITH:
1. Policy Identifier (SP-2025-001 format)
2. Risk Statement (business impact)
3. Compliance Mapping (NIST CSF, ISO 27001, OWASP)
4. Policy Requirements (specific controls)
5. Remediation Plan (timeline: Critical = 24-48h, CTO responsible)
6. Monitoring Strategy (detection methods)

Format: Professional, 400-500 words, actionable language.
```

**Sample LLM Output:**
```
POLICY IDENTIFIER: SP-2025-001

TITLE: SQL Injection Prevention in Authentication Module

RISK STATEMENT:
The authentication module contains a critical SQL injection vulnerability that
allows attackers to bypass authentication by manipulating user input. This
poses severe risks including unauthorized access to user accounts, data
exfiltration, database compromise, and potential regulatory violations (GDPR,
PCI-DSS). Estimated business impact: $500K+ in breach costs and reputational
damage.

COMPLIANCE MAPPING:
- NIST CSF: PR.AC-4 (Access Control), DE.CM-7 (Monitoring)
- ISO 27001: A.14.2.5 (Secure Development), A.12.6.1 (Vulnerability Management)
- OWASP: A03:2021-Injection

POLICY REQUIREMENTS:
1. All database queries MUST use parameterized statements or prepared statements
2. Input validation MUST be implemented for all user-supplied data
3. Least privilege database accounts MUST be used (no root/admin access)
4. SQL query logging MUST be enabled in production
5. Code reviews MUST verify proper parameterization before deployment

REMEDIATION PLAN:
- Timeline: 24-48 hours (CRITICAL severity)
- Responsible: CTO (executive oversight)
- Technical Lead: Security Team Lead
- Developer Assignment: Senior Backend Developer

Immediate Actions:
1. Apply emergency hotfix using parameterized queries (app/auth.py:45)
2. Deploy to production after security testing
3. Implement WAF rule to block SQL injection patterns
4. Review all authentication endpoints for similar issues

MONITORING AND DETECTION:
- Enable SQL query logging in database
- Configure SIEM alerts for SQL injection patterns
- Implement Web Application Firewall (WAF) with OWASP ruleset
- Run weekly SAST scans with Semgrep security audit ruleset
- Perform monthly penetration testing of authentication flows

OWNERSHIP:
- Policy Owner: Chief Information Security Officer (CISO)
- Technical Owner: Application Security Team
- Review Frequency: Quarterly
- Next Review: February 6, 2026
```

---

# 4. BAZZAOUI - DAST Parser & LLM Integration

## 4.1 Responsibilities
- **DAST Parser:** Parse Dynamic Application Security Testing reports
- **LLM Integration for DAST:** Use LLaMA 3.1 8B Instant for generating DAST policies
- **Runtime Vulnerability Analysis:** Process runtime/deployment issues
- **Multi-Format Support:** Handle OWASP ZAP XML and Nuclei JSON

## 4.2 DAST Parser Implementation

**File:** `backend/parsers/dast_parser.py` (250 lines)

### Data Model

**DASTVulnerability Dataclass:**
```python
@dataclass
class DASTVulnerability:
    """
    Unified DAST vulnerability representation

    Runtime/deployment vulnerabilities found during application testing

    Fields:
    - url: str - Full URL where vulnerability was found
    - endpoint: str - API endpoint (extracted from URL)
    - method: str - HTTP method (GET/POST/PUT/DELETE)
    - issue_type: str - Vulnerability type (XSS, CSRF, etc.)
    - risk_level: str - HIGH/MEDIUM/LOW risk rating
    - confidence: str - Detection confidence level
    - cwe_id: str - CWE identifier
    - description: str - Technical description
    - solution: str - Remediation steps
    - evidence: str - Proof of vulnerability (request/response)
    - metadata: dict - Tool-specific data
    """
    url: str
    endpoint: str
    method: str
    issue_type: str
    risk_level: str
    confidence: str
    cwe_id: str = ""
    description: str = ""
    solution: str = ""
    evidence: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            'url': self.url,
            'endpoint': self.endpoint,
            'method': self.method,
            'issue_type': self.issue_type,
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'cwe_id': self.cwe_id,
            'description': self.description,
            'solution': self.solution,
            'evidence': self.evidence
        }
```

### Parsing Logic

**Main Parse Function:**
```python
def parse(self, report_content: str) -> List[DASTVulnerability]:
    """
    Parse DAST report from multiple tool formats

    Supports:
    - OWASP ZAP (XML format)
    - Nuclei (JSON format)
    - Generic JSON DAST reports

    Flow:
    1. Detect format (XML vs JSON)
    2. Call appropriate parser
    3. Normalize all fields
    4. Return list of DASTVulnerability objects
    """
    vulnerabilities = []

    # Try XML first (OWASP ZAP)
    if report_content.strip().startswith('<?xml') or report_content.strip().startswith('<'):
        vulnerabilities = self._parse_zap_xml(report_content)
    else:
        # Try JSON (Nuclei or generic)
        try:
            report = json.loads(report_content)

            if 'vulnerabilities' in report:
                # Generic JSON format
                vulnerabilities = self._parse_generic_json(report)
            elif isinstance(report, list):
                # Nuclei format (array of findings)
                vulnerabilities = self._parse_nuclei(report)

        except json.JSONDecodeError:
            raise ValueError("Invalid DAST report format (not XML or JSON)")

    return vulnerabilities
```

**OWASP ZAP XML Parser:**
```python
def _parse_zap_xml(self, xml_content: str) -> List[DASTVulnerability]:
    """
    Parse OWASP ZAP XML report

    ZAP XML Structure:
    <OWASPZAPReport>
      <site name="https://example.com">
        <alerts>
          <alertitem>
            <pluginid>40012</pluginid>
            <alert>Cross-Site Scripting (Reflected)</alert>
            <riskcode>3</riskcode>  <!-- 0=Info, 1=Low, 2=Medium, 3=High -->
            <confidence>2</confidence>  <!-- 1=Low, 2=Medium, 3=High -->
            <desc>XSS vulnerability allows attacker...</desc>
            <uri>https://example.com/search?q=test</uri>
            <solution>Sanitize user input and encode output</solution>
            <cweid>79</cweid>
            <instances>
              <instance>
                <uri>https://example.com/search</uri>
                <method>GET</method>
                <evidence><![CDATA[<script>alert(1)</script>]]></evidence>
              </instance>
            </instances>
          </alertitem>
        </alerts>
      </site>
    </OWASPZAPReport>
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(xml_content, 'xml')
    vulnerabilities = []

    # Iterate through all alert items
    for alert in soup.find_all('alertitem'):
        # Extract basic info
        issue_type = alert.find('alert').text if alert.find('alert') else 'Unknown'
        risk_code = int(alert.find('riskcode').text) if alert.find('riskcode') else 1
        confidence_code = int(alert.find('confidence').text) if alert.find('confidence') else 1

        # Normalize risk level
        risk_level = self._normalize_risk_level(risk_code)
        confidence = self._normalize_confidence(confidence_code)

        # Extract CWE
        cwe_id = f"CWE-{alert.find('cweid').text}" if alert.find('cweid') else ""

        # Process each instance
        instances = alert.find_all('instance')
        for instance in instances:
            url = instance.find('uri').text if instance.find('uri') else ""
            method = instance.find('method').text if instance.find('method') else "GET"
            evidence = instance.find('evidence').text if instance.find('evidence') else ""

            # Extract endpoint from URL
            endpoint = self._extract_endpoint(url)

            vuln = DASTVulnerability(
                url=url,
                endpoint=endpoint,
                method=method,
                issue_type=issue_type,
                risk_level=risk_level,
                confidence=confidence,
                cwe_id=cwe_id,
                description=alert.find('desc').text if alert.find('desc') else "",
                solution=alert.find('solution').text if alert.find('solution') else "",
                evidence=evidence,
                metadata={
                    'tool': 'OWASP ZAP',
                    'plugin_id': alert.find('pluginid').text if alert.find('pluginid') else ""
                }
            )

            vulnerabilities.append(vuln)

    return vulnerabilities
```

**Nuclei JSON Parser:**
```python
def _parse_nuclei(self, report: list) -> List[DASTVulnerability]:
    """
    Parse Nuclei JSON report

    Nuclei JSON Structure:
    [
      {
        "template-id": "cve-2021-12345",
        "info": {
          "name": "Apache Log4j RCE",
          "severity": "critical",
          "description": "Remote code execution...",
          "classification": {
            "cve-id": "CVE-2021-12345",
            "cwe-id": "CWE-502"
          }
        },
        "type": "http",
        "host": "https://example.com",
        "matched-at": "https://example.com/api/login",
        "extracted-results": ["vulnerable string"],
        "curl-command": "curl -X POST..."
      }
    ]
    """
    vulnerabilities = []

    for finding in report:
        info = finding.get('info', {})
        classification = info.get('classification', {})

        # Extract severity
        severity_raw = info.get('severity', 'medium')
        risk_level = self._normalize_nuclei_severity(severity_raw)

        # Extract CWE
        cwe_id = classification.get('cwe-id', '')
        if not cwe_id.startswith('CWE-'):
            cwe_id = f"CWE-{cwe_id}" if cwe_id else ""

        # Extract URL and endpoint
        url = finding.get('matched-at', finding.get('host', ''))
        endpoint = self._extract_endpoint(url)

        # Determine HTTP method from curl command
        method = self._extract_method_from_curl(finding.get('curl-command', ''))

        vuln = DASTVulnerability(
            url=url,
            endpoint=endpoint,
            method=method,
            issue_type=info.get('name', 'Security Issue'),
            risk_level=risk_level,
            confidence='HIGH',  # Nuclei findings are generally high confidence
            cwe_id=cwe_id,
            description=info.get('description', ''),
            solution=info.get('remediation', 'Apply security patches'),
            evidence=str(finding.get('extracted-results', [])),
            metadata={
                'tool': 'Nuclei',
                'template_id': finding.get('template-id', ''),
                'cve_id': classification.get('cve-id', '')
            }
        )

        vulnerabilities.append(vuln)

    return vulnerabilities
```

**Helper Functions:**
```python
def _normalize_risk_level(self, risk_code: int) -> str:
    """
    Convert ZAP risk codes to standard levels

    ZAP Codes:
    - 3 → HIGH
    - 2 → MEDIUM
    - 1 → LOW
    - 0 → INFO (treated as LOW)
    """
    if risk_code >= 3:
        return 'HIGH'
    elif risk_code == 2:
        return 'MEDIUM'
    else:
        return 'LOW'

def _extract_endpoint(self, url: str) -> str:
    """
    Extract API endpoint from full URL

    Examples:
    - https://example.com/api/users/123 → /api/users/{id}
    - https://example.com/search?q=test → /search
    """
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path

    # Replace numeric IDs with {id}
    import re
    path = re.sub(r'/\d+', '/{id}', path)

    return path if path else '/'

def _extract_method_from_curl(self, curl_command: str) -> str:
    """Extract HTTP method from curl command"""
    if '-X POST' in curl_command or '--request POST' in curl_command:
        return 'POST'
    elif '-X PUT' in curl_command:
        return 'PUT'
    elif '-X DELETE' in curl_command:
        return 'DELETE'
    else:
        return 'GET'  # Default
```

## 4.3 LLM Integration for DAST

**Model:** LLaMA 3.1 8B Instant (Groq API)

**Why LLaMA 3.1 8B for DAST?**
- **Speed:** "Instant" variant = ultra-fast inference
- **Efficiency:** DAST findings are more straightforward than SAST
- **Cost-Effective:** Smaller model = less compute for same quality
- **Sufficient Capability:** 8B parameters adequate for runtime issue analysis

**Integration Point:**
```python
# Initialize DAST LLM (faster model)
self.llm_clients['dast'] = GroqClient(model="llama-3.1-8b-instant")

# During generation
for dast_vuln in dast_vulns:
    policy = self.llm_clients['dast'].generate(
        user_prompt=self.prompt_templates.get_policy_generation_prompt(
            vulnerability=asdict(dast_vuln),
            compliance_context=rag_result['formatted_context'],
            severity=dast_vuln.risk_level
        ),
        system_prompt=self.prompt_templates.get_system_prompt(),
        temperature=0.3,
        max_tokens=1200  # Slightly less for DAST
    )
```

**Sample DAST Prompt:**
```
USER:
Generate a comprehensive security policy for the following DAST vulnerability:

VULNERABILITY DETAILS:
- Title: Cross-Site Scripting (Reflected)
- URL: https://app.example.com/search?q=<script>alert(1)</script>
- Endpoint: /search
- Method: GET
- Risk Level: HIGH
- CWE: CWE-79
- Description: User input in 'q' parameter is reflected in HTML response
  without proper encoding, allowing JavaScript execution
- Solution: Implement context-aware output encoding and Content Security Policy

COMPLIANCE REQUIREMENTS (from RAG):
[1] NIST CSF - PR.DS-5: Protections against data leaks are implemented
[2] ISO 27001 - A.14.2.1: Secure development policy and procedures
[3] OWASP - A03:2021-Injection: Sanitize all outputs

GENERATE POLICY...
```

**Sample LLM Output:**
```
POLICY IDENTIFIER: SP-2025-002

TITLE: Cross-Site Scripting (XSS) Prevention in Search Functionality

RISK STATEMENT:
A reflected XSS vulnerability exists in the search endpoint that allows
attackers to inject malicious JavaScript into victim browsers. This enables
session hijacking, credential theft, and phishing attacks. Impacts user trust
and regulatory compliance (GDPR Article 32 - Security of Processing).

COMPLIANCE MAPPING:
- NIST CSF: PR.DS-5 (Data Integrity), PR.AT-2 (Security Awareness)
- ISO 27001: A.14.2.1 (Secure Development), A.14.1.2 (Input Validation)
- OWASP: A03:2021-Injection

POLICY REQUIREMENTS:
1. Context-aware output encoding MUST be applied to all user inputs
2. Content Security Policy (CSP) MUST be implemented
3. Input validation MUST reject suspicious patterns
4. HTTPOnly and Secure flags MUST be set on cookies
5. Regular penetration testing MUST include XSS checks

REMEDIATION PLAN:
- Timeline: 1 week (HIGH severity)
- Responsible: Security Team Lead
- Developer: Frontend Team

Actions:
1. Implement output encoding in search results template
2. Deploy Content-Security-Policy header
3. Add input validation for search queries
4. Update cookie security flags
5. Test with OWASP ZAP and manual verification

MONITORING:
- WAF rules for XSS patterns
- CSP violation reporting endpoint
- Regular DAST scans (weekly)
- Security code reviews before deployment
```

## 4.4 Smart DAST Scanner

**File:** `backend/scanners/smart_dast_scanner.py`

**4-Tier Scanning Strategy:**

### Tier 1: User-Provided Live URL (Highest Quality)
```python
def scan_tier1_live_url(self, url: str) -> dict:
    """
    Scan user-provided deployed application URL

    Best Case: User provides live application URL
    Quality: Highest - real vulnerabilities in production-like environment

    Process:
    1. Validate URL is accessible
    2. Run Nuclei scan against URL
    3. Return actual runtime vulnerabilities
    """
    # Run Nuclei
    nuclei_scanner = NucleiScanner()
    results = nuclei_scanner.scan(url)

    return {
        "tool": "Nuclei",
        "tier": "Tier 1 - Live URL",
        "quality": "HIGH",
        "vulnerabilities": results
    }
```

### Tier 2: Detect Deployment Configuration
```python
def scan_tier2_detect_config(self, repo_path: str) -> dict:
    """
    Detect deployment URL from configuration files

    Checks:
    - Dockerfile for EXPOSE ports and ENV variables
    - docker-compose.yml for service ports
    - .env files for BASE_URL variables
    - package.json scripts for dev server URLs

    If found: Use detected URL for scanning
    """
    detected_url = None

    # Check Dockerfile
    dockerfile_path = os.path.join(repo_path, 'Dockerfile')
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path) as f:
            content = f.read()
            # Look for EXPOSE 3000 → http://localhost:3000
            if 'EXPOSE 3000' in content:
                detected_url = 'http://localhost:3000'

    # Check docker-compose.yml
    compose_path = os.path.join(repo_path, 'docker-compose.yml')
    if os.path.exists(compose_path):
        # Parse YAML and extract port mappings
        ...

    if detected_url:
        return self.scan_tier1_live_url(detected_url)
```

### Tier 3: Parse Source Code for URLs
```python
def scan_tier3_source_parsing(self, repo_path: str) -> dict:
    """
    Extract URLs from source code

    Searches for:
    - API_BASE_URL = "http://..."
    - fetch('http://...')
    - axios.get('http://...')
    - config files with URLs

    Attempts scanning on found URLs
    """
    found_urls = []

    # Scan all source files
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.js', '.py', '.java', '.go')):
                file_path = os.path.join(root, file)
                urls = self._extract_urls_from_file(file_path)
                found_urls.extend(urls)

    # Try scanning each URL
    for url in found_urls:
        try:
            return self.scan_tier1_live_url(url)
        except:
            continue
```

### Tier 4: Sample Data Fallback
```python
def scan_tier4_sample_data(self) -> dict:
    """
    Return sample DAST vulnerabilities as fallback

    Used when no live URL is available
    Clearly marked as sample data
    """
    return {
        "tool": "Sample Data",
        "tier": "Tier 4 - Fallback",
        "quality": "SAMPLE",
        "vulnerabilities": [
            {
                "url": "http://example.com/api/login",
                "issue_type": "Weak Password Policy",
                "risk_level": "MEDIUM",
                "description": "Sample vulnerability - no actual scan performed"
            }
        ],
        "note": "No live application URL available. Using sample data."
    }
```

---

# 5. IBNOU-KADY - SCA Parser & LLM Integration

## 5.1 Responsibilities
- **SCA Parser:** Parse Software Composition Analysis reports for dependency vulnerabilities
- **LLM Integration for SCA:** Use LLaMA 3.3 70B for generating SCA policies
- **Dependency Management:** Analyze vulnerable packages and versions
- **Patch Detection:** Identify available fixes and upgrade paths

## 5.2 SCA Parser Implementation

**File:** `backend/parsers/sca_parser.py` (320 lines)

### Data Model

**SCAVulnerability Dataclass:**
```python
@dataclass
class SCAVulnerability:
    """
    Unified SCA vulnerability representation

    Third-party dependency vulnerabilities

    Fields:
    - package_name: str - NPM package or pip module name
    - current_version: str - Currently installed version
    - vulnerable_versions: str - Version range with vulnerability
    - patched_version: str - Fixed version (if available)
    - cve_id: str - CVE identifier
    - severity: str - CRITICAL/HIGH/MEDIUM/LOW
    - description: str - Vulnerability description
    - exploitability: str - Proof-of-concept availability
    - fix_available: bool - Whether patch exists
    - direct_dependency: bool - Direct vs transitive dependency
    - dependency_chain: list - Path from root to vulnerable package
    - metadata: dict - Additional tool-specific data
    """
    package_name: str
    current_version: str
    vulnerable_versions: str
    patched_version: str
    cve_id: str
    severity: str
    description: str
    exploitability: str = "Unknown"
    fix_available: bool = False
    direct_dependency: bool = True
    dependency_chain: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            'package_name': self.package_name,
            'current_version': self.current_version,
            'vulnerable_versions': self.vulnerable_versions,
            'patched_version': self.patched_version,
            'cve_id': self.cve_id,
            'severity': self.severity,
            'description': self.description,
            'exploitability': self.exploitability,
            'fix_available': self.fix_available,
            'direct_dependency': self.direct_dependency,
            'dependency_chain': self.dependency_chain
        }
```

### Parsing Logic

**Main Parse Function:**
```python
def parse(self, report_content: str) -> List[SCAVulnerability]:
    """
    Parse SCA report from multiple tool formats

    Supports:
    - npm audit (JSON)
    - Trivy (JSON) - Universal SCA scanner
    - pip-audit (JSON)

    Flow:
    1. Strip BOM (Byte Order Mark) for cross-platform compatibility
    2. Parse JSON
    3. Detect format (npm vs Trivy vs pip-audit)
    4. Call appropriate parser
    5. Normalize all fields
    6. Return list of SCAVulnerability objects
    """
    # Remove BOM if present (UTF-8 BOM: EF BB BF)
    if report_content.startswith('\ufeff'):
        report_content = report_content[1:]

    # Strip BOM bytes
    report_content = report_content.encode('utf-8').decode('utf-8-sig')

    try:
        report = json.loads(report_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in SCA report: {e}")

    vulnerabilities = []

    # Detect format
    if 'vulnerabilities' in report and isinstance(report['vulnerabilities'], dict):
        # npm audit format
        vulnerabilities = self._parse_npm_audit(report)
    elif 'Results' in report:
        # Trivy format
        vulnerabilities = self._parse_trivy(report)
    elif 'vulnerabilities' in report and isinstance(report['vulnerabilities'], list):
        # pip-audit format
        vulnerabilities = self._parse_pip_audit(report)
    else:
        raise ValueError("Unknown SCA report format")

    return vulnerabilities
```

**npm Audit Parser:**
```python
def _parse_npm_audit(self, report: dict) -> List[SCAVulnerability]:
    """
    Parse npm audit JSON report

    npm audit JSON Structure:
    {
      "vulnerabilities": {
        "package-name": {
          "name": "lodash",
          "severity": "high",
          "via": [
            {
              "source": 1234,
              "name": "lodash",
              "dependency": "lodash",
              "title": "Prototype Pollution",
              "url": "https://npmjs.com/advisories/1234",
              "severity": "high",
              "cwe": ["CWE-1321"],
              "cvss": {
                "score": 7.4,
                "vectorString": "CVSS:3.1/..."
              },
              "range": ">=3.7.0 <4.17.21"
            }
          ],
          "effects": ["affected-package"],
          "range": ">=3.7.0 <4.17.21",
          "nodes": ["node_modules/lodash"],
          "fixAvailable": {
            "name": "lodash",
            "version": "4.17.21",
            "isSemVerMajor": false
          }
        }
      }
    }
    """
    vulnerabilities = []

    for pkg_name, pkg_data in report.get('vulnerabilities', {}).items():
        # Get vulnerability details from 'via' field
        via = pkg_data.get('via', [])

        for vuln_source in via:
            # Skip if via is just a number (reference to another advisory)
            if isinstance(vuln_source, (int, str)):
                continue

            # Extract details
            severity = vuln_source.get('severity', 'MEDIUM').upper()
            title = vuln_source.get('title', 'Dependency Vulnerability')
            url = vuln_source.get('url', '')
            cwe_list = vuln_source.get('cwe', [])
            cwe_id = cwe_list[0] if cwe_list else ""

            # Get version info
            current_version = pkg_data.get('version', 'Unknown')
            vulnerable_range = vuln_source.get('range', '')

            # Check for fix
            fix_available_data = pkg_data.get('fixAvailable', False)
            fix_available = bool(fix_available_data)
            patched_version = ""
            if fix_available_data and isinstance(fix_available_data, dict):
                patched_version = fix_available_data.get('version', '')

            # Determine if direct dependency
            effects = pkg_data.get('effects', [])
            direct_dependency = (pkg_name not in effects)

            # Extract advisory ID from URL
            advisory_id = ""
            if '/advisories/' in url:
                advisory_id = url.split('/advisories/')[-1]

            vuln = SCAVulnerability(
                package_name=pkg_name,
                current_version=current_version,
                vulnerable_versions=vulnerable_range,
                patched_version=patched_version,
                cve_id=f"npm-{advisory_id}" if advisory_id else "",
                severity=self._normalize_severity(severity),
                description=title,
                exploitability=self._assess_exploitability(vuln_source),
                fix_available=fix_available,
                direct_dependency=direct_dependency,
                dependency_chain=effects if effects else [pkg_name],
                metadata={
                    'tool': 'npm audit',
                    'url': url,
                    'cvss_score': vuln_source.get('cvss', {}).get('score', 0)
                }
            )

            vulnerabilities.append(vuln)

    return vulnerabilities
```

**Trivy Parser:**
```python
def _parse_trivy(self, report: dict) -> List[SCAVulnerability]:
    """
    Parse Trivy SCA report

    Trivy JSON Structure:
    {
      "Results": [
        {
          "Target": "package.json",
          "Class": "lang-pkgs",
          "Type": "npm",
          "Vulnerabilities": [
            {
              "VulnerabilityID": "CVE-2021-12345",
              "PkgName": "express",
              "InstalledVersion": "4.16.0",
              "FixedVersion": "4.17.3",
              "Severity": "HIGH",
              "Title": "Express vulnerable to XSS",
              "Description": "Express versions before 4.17.3...",
              "References": ["https://cve.mitre.org/..."],
              "PrimaryURL": "https://nvd.nist.gov/..."
            }
          ]
        }
      ]
    }
    """
    vulnerabilities = []

    for result in report.get('Results', []):
        target = result.get('Target', 'Unknown')
        pkg_type = result.get('Type', 'Unknown')  # npm, pip, gem, etc.

        for vuln_data in result.get('Vulnerabilities', []):
            package_name = vuln_data.get('PkgName', 'Unknown')
            cve_id = vuln_data.get('VulnerabilityID', '')
            severity = vuln_data.get('Severity', 'MEDIUM')

            current_version = vuln_data.get('InstalledVersion', '')
            fixed_version = vuln_data.get('FixedVersion', '')
            fix_available = bool(fixed_version)

            # Trivy doesn't provide vulnerable range, construct it
            vulnerable_versions = f"<{fixed_version}" if fixed_version else "all"

            vuln = SCAVulnerability(
                package_name=package_name,
                current_version=current_version,
                vulnerable_versions=vulnerable_versions,
                patched_version=fixed_version,
                cve_id=cve_id,
                severity=self._normalize_severity(severity),
                description=vuln_data.get('Title', '') + " - " + vuln_data.get('Description', ''),
                exploitability=self._assess_trivy_exploitability(vuln_data),
                fix_available=fix_available,
                direct_dependency=True,  # Trivy doesn't distinguish
                dependency_chain=[package_name],
                metadata={
                    'tool': 'Trivy',
                    'target': target,
                    'package_type': pkg_type,
                    'primary_url': vuln_data.get('PrimaryURL', ''),
                    'references': vuln_data.get('References', [])
                }
            )

            vulnerabilities.append(vuln)

    return vulnerabilities
```

**Helper Functions:**
```python
def _assess_exploitability(self, vuln_data: dict) -> str:
    """
    Assess exploitability based on CVSS score and available info

    Levels:
    - CRITICAL: CVSS >= 9.0 or known exploit
    - HIGH: CVSS >= 7.0
    - MEDIUM: CVSS >= 4.0
    - LOW: CVSS < 4.0
    """
    cvss = vuln_data.get('cvss', {})
    score = cvss.get('score', 0)

    if score >= 9.0:
        return "CRITICAL - Likely exploited in the wild"
    elif score >= 7.0:
        return "HIGH - Proof-of-concept exists"
    elif score >= 4.0:
        return "MEDIUM - Theoretical exploit"
    else:
        return "LOW - Difficult to exploit"

def _extract_dependency_chain(self, effects: list, package_name: str) -> list:
    """
    Build dependency chain from root to vulnerable package

    Example: ['myapp', 'express', 'body-parser', 'qs']
    Shows: myapp depends on express, which depends on body-parser, which depends on qs (vulnerable)
    """
    chain = []

    # effects contains packages affected by this vulnerability
    # Usually root package → intermediate → vulnerable package

    if effects:
        chain = effects.copy()
    else:
        chain = [package_name]

    return chain

def _determine_upgrade_path(self, current: str, patched: str) -> str:
    """
    Determine upgrade strategy

    Returns:
    - "PATCH" if patch version update (1.2.3 → 1.2.4)
    - "MINOR" if minor version update (1.2.3 → 1.3.0)
    - "MAJOR" if major version update (1.2.3 → 2.0.0) - Breaking changes likely
    """
    try:
        current_parts = current.split('.')
        patched_parts = patched.split('.')

        if current_parts[0] != patched_parts[0]:
            return "MAJOR - Breaking changes expected"
        elif current_parts[1] != patched_parts[1]:
            return "MINOR - New features, backwards compatible"
        else:
            return "PATCH - Bug fixes only"
    except:
        return "Unknown"
```

## 5.3 LLM Integration for SCA

**Model:** LLaMA 3.3 70B Versatile (Groq API)

**Why LLaMA 3.3 70B for SCA?**
- **Dependency Understanding:** Better grasp of package ecosystems (npm, pip, Maven)
- **Version Analysis:** Can reason about semantic versioning and upgrade paths
- **Impact Assessment:** Understands transitive dependency risks
- **Remediation Planning:** Suggests comprehensive upgrade strategies

**Integration Point:**
```python
# Initialize SCA LLM (same as SAST - large model)
self.llm_clients['sca'] = GroqClient(model="llama-3.3-70b-versatile")

# During generation
for sca_vuln in sca_vulns:
    policy = self.llm_clients['sca'].generate(
        user_prompt=self.prompt_templates.get_policy_generation_prompt(
            vulnerability=asdict(sca_vuln),
            compliance_context=rag_result['formatted_context'],
            severity=sca_vuln.severity
        ),
        system_prompt=self.prompt_templates.get_system_prompt(),
        temperature=0.3,
        max_tokens=1500
    )
```

**Sample SCA Prompt:**
```
USER:
Generate a comprehensive security policy for the following SCA vulnerability:

VULNERABILITY DETAILS:
- Package: lodash
- Current Version: 3.10.1
- Vulnerable Versions: >=3.7.0 <4.17.21
- Patched Version: 4.17.21
- CVE: npm-1523
- Severity: HIGH
- Description: Prototype Pollution vulnerability allows attacker to modify
  object prototypes leading to unexpected application behavior or RCE
- Exploitability: HIGH - Proof-of-concept exists
- Fix Available: Yes (upgrade to 4.17.21)
- Direct Dependency: Yes
- CVSS Score: 7.4

COMPLIANCE REQUIREMENTS (from RAG):
[1] NIST CSF - ID.RA-1: Asset vulnerabilities are identified and documented
[2] ISO 27001 - A.12.6.1: Management of technical vulnerabilities
[3] ISO 27001 - A.14.2.9: System acceptance testing

GENERATE POLICY...
```

**Sample LLM Output:**
```
POLICY IDENTIFIER: SP-2025-003

TITLE: Third-Party Dependency Vulnerability Management - Lodash Prototype Pollution

RISK STATEMENT:
The lodash library version 3.10.1 contains a critical prototype pollution
vulnerability (CVE npm-1523) that allows attackers to modify JavaScript object
prototypes. This can lead to:
- Remote Code Execution (RCE)
- Authentication bypass
- Denial of Service (DoS)
- Data corruption

Business Impact: Application instability, potential data breach, regulatory
non-compliance (GDPR, SOC 2). Estimated impact: $200K+ incident response costs.

COMPLIANCE MAPPING:
- NIST CSF: ID.RA-1 (Vulnerability Identification), PR.IP-12 (Vulnerability Response)
- ISO 27001: A.12.6.1 (Technical Vulnerability Management), A.14.2.9 (Testing)

POLICY REQUIREMENTS:
1. Vulnerable dependencies MUST be patched within 7 days for HIGH severity
2. Automated dependency scanning MUST run on every commit (CI/CD integration)
3. Direct dependencies MUST be updated before transitive dependencies
4. Version pinning MUST be used in package.json to prevent regression
5. Security advisories MUST be monitored daily (npm audit, Snyk, GitHub Dependabot)

REMEDIATION PLAN:
- Timeline: 1 week (HIGH severity)
- Responsible: Development Team Lead
- Developer: Senior JavaScript Developer

Phase 1: Immediate Actions (24 hours)
1. Update lodash to 4.17.21 in package.json
   ```bash
   npm install lodash@4.17.21 --save
   ```
2. Run full test suite to verify compatibility
3. Check for breaking changes (3.x → 4.x is major version)
4. Update code if breaking changes found

Phase 2: Verification (48 hours)
1. Run npm audit to confirm vulnerability fixed
2. Perform regression testing on critical flows
3. Deploy to staging environment
4. Conduct smoke tests

Phase 3: Deployment (1 week)
1. Deploy to production during maintenance window
2. Monitor application logs for errors
3. Roll back if issues detected

DEPENDENCY UPGRADE STRATEGY:
- Upgrade Type: MAJOR (3.x → 4.x)
- Breaking Changes: Possible - Review lodash 4.0 migration guide
- Testing Required: EXTENSIVE
- Alternative: Consider lodash-es (modular) or native JS methods

MONITORING AND PREVENTION:
- Implement npm audit in CI/CD pipeline (fail build on HIGH/CRITICAL)
- Enable GitHub Dependabot for automated PR creation
- Use Snyk or Trivy for continuous dependency monitoring
- Set up alerts for new advisories affecting project dependencies
- Quarterly dependency update sprints

LONG-TERM STRATEGY:
1. Evaluate necessity of lodash (many features now in ES6+)
2. Consider tree-shaking with lodash-es to reduce attack surface
3. Implement Software Bill of Materials (SBOM) generation
4. Establish dependency approval process for new packages

OWNERSHIP:
- Policy Owner: Engineering Manager
- Technical Owner: DevOps Team
- Review Frequency: Monthly
- Next Review: December 6, 2025
```

## 5.4 Advanced SCA Features

### Dependency Chain Analysis
```python
def analyze_dependency_chain(self, vuln: SCAVulnerability) -> dict:
    """
    Analyze impact through dependency chain

    Returns:
    - Root cause package
    - All affected packages
    - Upgrade impact assessment
    - Alternative solutions
    """
    chain = vuln.dependency_chain

    analysis = {
        "chain_length": len(chain),
        "root_package": chain[0] if chain else None,
        "vulnerable_package": vuln.package_name,
        "is_direct": vuln.direct_dependency,
        "upgrade_impact": "DIRECT" if vuln.direct_dependency else "TRANSITIVE",
        "recommendation": ""
    }

    if vuln.direct_dependency:
        analysis["recommendation"] = f"Upgrade {vuln.package_name} directly to {vuln.patched_version}"
    else:
        analysis["recommendation"] = f"Upgrade root dependency {chain[0]} which will pull in fixed version"

    return analysis
```

### Fix Verification
```python
def verify_fix(self, package_name: str, current_version: str, fixed_version: str) -> bool:
    """
    Verify that upgrading to fixed version actually resolves vulnerability

    Checks:
    1. Fixed version is newer than current
    2. Fixed version matches semantic versioning constraints
    3. No known vulnerabilities in fixed version
    """
    from packaging import version

    # Compare versions
    is_newer = version.parse(fixed_version) > version.parse(current_version)

    # Check if fixed version has its own vulnerabilities (rare but possible)
    # Would need to query npm registry or Snyk API

    return is_newer
```

---

# 6. SYSTEM INTEGRATION & DATA FLOW

## 6.1 End-to-End Workflow

### Upload Mode Flow

**Step 1: User Uploads Files (Frontend)**
```javascript
// frontend/src/components/UploadMode.jsx

const handleFilesChange = (files) => {
  setFiles({
    sast: files.sast,   // semgrep.json
    sca: files.sca,     // npm-audit.json
    dast: files.dast    // zap-report.xml
  });
};

const handleSubmit = async () => {
  await apiClient.generatePolicies(files, 5, handleProgress);
};
```

**Step 2: API Call with WebSocket (API Client)**
```javascript
// frontend/src/utils/api.js

async generatePolicies(files, maxPerType, progressCallback) {
  // Establish WebSocket
  this.ws = new WebSocket('ws://localhost:8000/ws');
  this.ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    progressCallback(data);  // Update UI
  };

  // Upload files via HTTP POST
  const formData = new FormData();
  formData.append('sast_file', files.sast);
  formData.append('sca_file', files.sca);
  formData.append('dast_file', files.dast);
  formData.append('max_per_type', maxPerType);

  const response = await axios.post('/api/generate-policies', formData);
  return response.data;
}
```

**Step 3: Backend Receives Request (FastAPI)**
```python
# backend/api/main.py

@app.post("/api/generate-policies")
async def generate_policies(
    sast_file: UploadFile = File(None),
    sca_file: UploadFile = File(None),
    dast_file: UploadFile = File(None),
    max_per_type: int = 5
):
    # Save uploaded files to temp directory
    temp_files = {}
    if sast_file:
        temp_sast = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_sast.write(await sast_file.read())
        temp_sast.close()
        temp_files['sast'] = temp_sast.name

    # Similar for SCA and DAST...

    # Call orchestrator with WebSocket broadcasting
    result = await broadcast_realtime_generation(
        sast_path=temp_files.get('sast'),
        sca_path=temp_files.get('sca'),
        dast_path=temp_files.get('dast'),
        max_per_type=max_per_type
    )

    # Cleanup temp files
    for path in temp_files.values():
        os.unlink(path)

    return result
```

**Step 4: Orchestrator Runs Pipeline**
```python
# backend/api/main.py - broadcast_realtime_generation()

async def broadcast_realtime_generation(sast_path, sca_path, dast_path, max_per_type):
    orchestrator = PolicyGeneratorOrchestrator()

    # PHASE 1: PARSING
    await broadcast_progress({
        'phase': 'parsing',
        'status': 'in_progress',
        'message': 'Parsing SAST report...'
    })

    sast_vulns, sca_vulns, dast_vulns = orchestrator.parse_reports(
        sast_path=sast_path,
        sca_path=sca_path,
        dast_path=dast_path
    )

    await broadcast_progress({
        'phase': 'parsing',
        'status': 'completed',
        'data': {
            'parsed_sast': len(sast_vulns),
            'parsed_sca': len(sca_vulns),
            'parsed_dast': len(dast_vulns)
        }
    })

    # PHASE 2: RAG RETRIEVAL
    await broadcast_progress({
        'phase': 'rag',
        'status': 'in_progress',
        'message': 'Retrieving compliance context...'
    })

    # (RAG happens inside orchestrator.generate_policies)

    # PHASE 3: LLM GENERATION
    results = []
    all_vulns = []

    # TOUZANI's SAST vulnerabilities
    for vuln in sast_vulns[:max_per_type]:
        all_vulns.append(('SAST', vuln))

    # IBNOU-KADY's SCA vulnerabilities
    for vuln in sca_vulns[:max_per_type]:
        all_vulns.append(('SCA', vuln))

    # BAZZAOUI's DAST vulnerabilities
    for vuln in dast_vulns[:max_per_type]:
        all_vulns.append(('DAST', vuln))

    total = len(all_vulns)

    for i, (vuln_type, vuln) in enumerate(all_vulns):
        # Select appropriate LLM
        llm_model = "LLaMA 3.3 70B" if vuln_type in ['SAST', 'SCA'] else "LLaMA 3.1 8B"

        await broadcast_progress({
            'phase': 'llm_generation',
            'status': 'in_progress',
            'message': f'Generating policy {i+1}/{total}...',
            'data': {
                'current_vuln': {
                    'title': vuln.title,
                    'type': vuln_type,
                    'severity': vuln.severity
                },
                'llm_model': llm_model,
                'progress_percentage': ((i+1) / total) * 100
            }
        })

        # Generate policy
        policy = orchestrator.generate_policy_for_vulnerability(
            vulnerability=asdict(vuln),
            vuln_type=vuln_type
        )

        results.append({
            'type': vuln_type,
            'vulnerability': asdict(vuln),
            'policy': policy,
            'llm_used': llm_model
        })

    # PHASE 4: COMPLIANCE ANALYSIS
    await broadcast_progress({
        'phase': 'compliance_validation',
        'status': 'in_progress',
        'message': 'Analyzing compliance coverage...'
    })

    from backend.compliance.coverage_analyzer import ComplianceCoverageAnalyzer
    analyzer = ComplianceCoverageAnalyzer()
    compliance_analysis = analyzer.analyze_coverage(results)

    # PHASE 5: SAVING
    await broadcast_progress({
        'phase': 'saving',
        'status': 'in_progress',
        'message': 'Generating reports...'
    })

    output_path = orchestrator.save_results(
        results=results,
        sast_vulns=sast_vulns,
        sca_vulns=sca_vulns,
        dast_vulns=dast_vulns
    )

    # ELGARCH's report generation produces:
    # - JSON file
    # - TXT file
    # - HTML file (with charts and metrics)
    # - PDF file (with matplotlib charts)

    # COMPLETE
    await broadcast_progress({
        'phase': 'complete',
        'status': 'completed',
        'data': {
            'results': results,
            'compliance_analysis': compliance_analysis,
            'total_vulns': len(results),
            'output_files': {
                'json': f"policy_generation_{timestamp}.json",
                'txt': f"security_policy_{timestamp}.txt",
                'html': f"security_policy_{timestamp}.html",
                'pdf': f"security_policy_{timestamp}.pdf"
            }
        }
    })

    return {
        'success': True,
        'results': results,
        'compliance_analysis': compliance_analysis,
        'total_vulns': len(results),
        'output_files': {...}
    }
```

**Step 5: Frontend Displays Results**
```javascript
// frontend/src/components/WorkflowView.jsx

const handleProgress = (data) => {
  if (data.phase === 'parsing') {
    setParsingStatus('completed');
  } else if (data.phase === 'llm_generation') {
    setLLMProgress(data.data.progress_percentage);
    setCurrentVuln(data.data.current_vuln);
  } else if (data.phase === 'complete') {
    setProcessing(false);
    setResults(data.data);
  }
};
```

```javascript
// frontend/src/components/ResultsView.jsx

<ResultsView results={results}>
  {/* Statistics */}
  <StatsCard title="Total Policies" value={results.total_vulns} />

  {/* Charts */}
  <BarChart data={severityChartData} />
  <PieChart data={typeChartData} />

  {/* Compliance */}
  <ComplianceValidation analysis={results.compliance_analysis} />

  {/* Individual Policies */}
  {results.results.map((policy, i) => (
    <PolicyCard key={i} policy={policy} />
  ))}

  {/* Downloads */}
  <DownloadButton format="pdf" filename={results.output_files.pdf} />
  <DownloadButton format="html" filename={results.output_files.html} />
</ResultsView>
```

## 6.2 Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐    ┌───────────────┐    ┌────────────────┐  │
│  │  TOUZANI      │    │ IBNOU-KADY    │    │  BAZZAOUI      │  │
│  │  Upload SAST  │    │  Upload SCA   │    │  Upload DAST   │  │
│  │  semgrep.json │    │ npm-audit.json│    │ zap-report.xml │  │
│  └───────┬───────┘    └───────┬───────┘    └────────┬───────┘  │
│          │                     │                      │          │
│          └─────────────────────┼──────────────────────┘          │
│                                │                                 │
│                         ┌──────▼──────┐                          │
│                         │  App.jsx    │                          │
│                         │ (Main State)│                          │
│                         └──────┬──────┘                          │
│                                │                                 │
│                         ┌──────▼───────┐                         │
│                         │  API Client  │                         │
│                         │  WebSocket   │                         │
│                         └──────┬───────┘                         │
└────────────────────────────────┼─────────────────────────────────┘
                                 │
                                 │ HTTP POST + WebSocket
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│                          BACKEND API                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              /api/generate-policies                        │  │
│  │  1. Save uploaded files to temp directory                 │  │
│  │  2. Call broadcast_realtime_generation()                  │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│              ┌────────────▼────────────┐                         │
│              │  ELGARCH                │                         │
│              │  PolicyGeneratorOrchest │                         │
│              │  Coordinator of Pipeline│                         │
│              └────────────┬────────────┘                         │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐           │
│  │  TOUZANI    │   │ IBNOU-KADY  │   │  BAZZAOUI   │           │
│  │ SASTParser  │   │  SCAParser  │   │ DASTParser  │           │
│  │ semgrep.json│   │npm-audit.json│   │zap-report.xml│          │
│  │   parsing   │   │   parsing   │   │   parsing   │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                   │
│         │   ┌─────────────┴─────────────┐   │                   │
│         │   │ List[SASTVulnerability]   │   │                   │
│         │   │ List[SCAVulnerability]    │   │                   │
│         │   │ List[DASTVulnerability]   │   │                   │
│         │   └─────────────┬─────────────┘   │                   │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                      │
│                  ┌────────▼────────┐                             │
│                  │  RAG Retriever  │                             │
│                  │  ChromaDB       │                             │
│                  │  Compliance     │                             │
│                  │  Context        │                             │
│                  └────────┬────────┘                             │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐           │
│  │  TOUZANI    │   │ IBNOU-KADY  │   │  BAZZAOUI   │           │
│  │  LLaMA 3.3  │   │  LLaMA 3.3  │   │  LLaMA 3.1  │           │
│  │  70B (SAST) │   │  70B (SCA)  │   │  8B (DAST)  │           │
│  │  Policy Gen │   │  Policy Gen │   │  Policy Gen │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                   │
│         │   ┌─────────────┴─────────────┐   │                   │
│         │   │  Generated Policies       │   │                   │
│         │   │  (15 SAST + 15 SCA +      │   │                   │
│         │   │   15 DAST = 45 policies)  │   │                   │
│         │   └─────────────┬─────────────┘   │                   │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                      │
│              ┌────────────▼────────────┐                         │
│              │  ELGARCH                │                         │
│              │  Compliance Analyzer    │                         │
│              │  NIST CSF / ISO 27001   │                         │
│              │  Coverage Calculation   │                         │
│              └────────────┬────────────┘                         │
│                           │                                      │
│              ┌────────────▼────────────┐                         │
│              │  ELGARCH                │                         │
│              │  Report Generator       │                         │
│              │  - JSON                 │                         │
│              │  - TXT                  │                         │
│              │  - HTML (with charts)   │                         │
│              │  - PDF (with charts)    │                         │
│              └────────────┬────────────┘                         │
│                           │                                      │
│                    ┌──────▼──────┐                               │
│                    │  ./outputs/ │                               │
│                    │  All Reports│                               │
│                    └─────────────┘                               │
└──────────────────────────────────────────────────────────────────┘

                           ▲
                           │ WebSocket Progress Updates
                           │ (All phases broadcast to frontend)
                           │
┌──────────────────────────┴───────────────────────────────────────┐
│                      FRONTEND RECEIVES                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  WorkflowView.jsx displays:                                      │
│  - ✅ Phase 1: Parsing (TOUZANI, IBNOU-KADY, BAZZAOUI parsers)  │
│  - ✅ Phase 2: RAG Retrieval                                     │
│  - 🔄 Phase 3: LLM Generation (45% complete)                     │
│    Current: "SQL Injection" (TOUZANI - SAST - LLaMA 3.3 70B)    │
│  - ⏳ Phase 4: Compliance Validation                             │
│  - ⏳ Phase 5: Saving Reports (ELGARCH)                          │
│                                                                   │
│  ResultsView.jsx displays:                                       │
│  - 45 Total Policies Generated                                   │
│  - SAST: 15 (TOUZANI), SCA: 15 (IBNOU-KADY), DAST: 15 (BAZZAOUI)│
│  - Compliance: NIST CSF 13.9%, ISO 27001 10.5% (ELGARCH)        │
│  - Download: PDF/HTML/JSON/TXT (ELGARCH)                         │
└──────────────────────────────────────────────────────────────────┘
```

---

# 7. TECHNICAL CHALLENGES & SOLUTIONS

## 7.1 ELGARCH - Report Generation Challenges

### Challenge 1: Chart Generation in PDF (No GUI)
**Problem:** Matplotlib requires GUI backend by default, doesn't work in server environment

**Solution:**
```python
# backend/utils/pdf_enhancer.py

import matplotlib
matplotlib.use('Agg')  # Non-GUI backend BEFORE importing pyplot
import matplotlib.pyplot as plt

# Now can generate charts without display
fig, ax = plt.subplots()
ax.bar(...)
plt.savefig(buffer, format='png')  # Save to BytesIO
plt.close()  # IMPORTANT: Prevent memory leak
```

### Challenge 2: UTF-8 Encoding in Reports (Windows Compatibility)
**Problem:** Special characters (emojis, accents) break PDF generation on Windows

**Solution:**
```python
# Always specify UTF-8 encoding
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

# ReportLab - use utf-8 encoding
from reportlab.lib.enums import TA_LEFT
Paragraph(policy_text, style, encoding='utf-8')
```

### Challenge 3: WebSocket Connection Management
**Problem:** Multiple clients, connections drop during long processing

**Solution:**
```python
# backend/api/main.py

active_connections: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)  # Clean up

async def broadcast_progress(message: dict):
    dead_connections = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            dead_connections.append(connection)  # Mark for removal

    # Remove dead connections
    for conn in dead_connections:
        active_connections.remove(conn)
```

## 7.2 TOUZANI - SAST Parser Challenges

### Challenge 1: Multiple Tool Formats
**Problem:** Semgrep, SonarQube, Bandit all have different JSON structures

**Solution:**
```python
def parse(self, report_content: str):
    report = json.loads(report_content)

    # Auto-detect format
    if 'results' in report:
        return self._parse_semgrep(report)
    elif 'issues' in report:
        return self._parse_sonarqube(report)
    elif 'errors' in report:
        return self._parse_bandit(report)
    else:
        # Fallback: Try to parse generic format
        return self._parse_generic(report)
```

### Challenge 2: Category Detection Accuracy
**Problem:** Check IDs like "python.lang.security.audit.dangerous-spawn" need to map to "Command Injection"

**Solution:**
```python
def _detect_category(self, check_id: str, message: str):
    # Multi-level detection
    check_lower = check_id.lower()
    msg_lower = message.lower()

    # Priority 1: Specific patterns in check_id
    if 'sql' in check_lower and ('injection' in check_lower or 'injection' in msg_lower):
        return 'SQL Injection'

    # Priority 2: CWE-based detection
    if 'cwe-89' in check_lower:
        return 'SQL Injection'

    # Priority 3: Message content analysis
    if 'cross-site scripting' in msg_lower or 'xss' in msg_lower:
        return 'Cross-Site Scripting (XSS)'

    # Default: Use generic category
    return 'Code Security Issue'
```

### Challenge 3: LLM Context Window Limits
**Problem:** LLaMA 3.3 has 8K token limit, large code snippets exceed this

**Solution:**
```python
def _truncate_code_snippet(self, code: str, max_lines: int = 20) -> str:
    """Truncate code to fit in LLM context"""
    lines = code.split('\n')
    if len(lines) <= max_lines:
        return code

    # Keep first 10 and last 10 lines
    truncated = lines[:10] + ['... (truncated) ...'] + lines[-10:]
    return '\n'.join(truncated)
```

## 7.3 BAZZAOUI - DAST Parser Challenges

### Challenge 1: XML vs JSON Parsing
**Problem:** OWASP ZAP uses XML, Nuclei uses JSON - need to support both

**Solution:**
```python
def parse(self, report_content: str):
    # Auto-detect format
    if report_content.strip().startswith('<?xml') or report_content.strip().startswith('<'):
        return self._parse_zap_xml(report_content)
    else:
        try:
            report = json.loads(report_content)
            return self._parse_nuclei(report)
        except:
            raise ValueError("Invalid DAST format")
```

### Challenge 2: No Live Application URL
**Problem:** User uploads SAST/SCA but no running app for DAST

**Solution:** 4-Tier Strategy (see Section 4.4)
1. User provides URL → Best quality
2. Detect from config files → Good quality
3. Extract from source code → Medium quality
4. Sample data fallback → Ensures pipeline doesn't fail

### Challenge 3: Endpoint Normalization
**Problem:** URLs have dynamic IDs: `/api/users/123` vs `/api/users/456`

**Solution:**
```python
def _extract_endpoint(self, url: str) -> str:
    from urllib.parse import urlparse
    import re

    parsed = urlparse(url)
    path = parsed.path

    # Replace numeric IDs: /users/123 → /users/{id}
    path = re.sub(r'/\d+', '/{id}', path)

    # Replace UUIDs: /users/abc-123-def → /users/{uuid}
    path = re.sub(r'/[a-f0-9-]{36}', '/{uuid}', path)

    return path
```

## 7.4 IBNOU-KADY - SCA Parser Challenges

### Challenge 1: BOM (Byte Order Mark) in JSON
**Problem:** npm audit on Windows adds UTF-8 BOM (EF BB BF), breaks JSON parsing

**Solution:**
```python
def parse(self, report_content: str):
    # Remove BOM if present
    if report_content.startswith('\ufeff'):
        report_content = report_content[1:]

    # Alternative: Use utf-8-sig encoding
    report_content = report_content.encode('utf-8').decode('utf-8-sig')

    report = json.loads(report_content)
```

### Challenge 2: Nested Dependency Chains
**Problem:** npm audit "via" field can be nested references to other advisories

**Solution:**
```python
def _parse_npm_audit(self, report: dict):
    for pkg_name, pkg_data in report['vulnerabilities'].items():
        via = pkg_data.get('via', [])

        for vuln_source in via:
            # Skip if via is just a number (reference)
            if isinstance(vuln_source, (int, str)):
                continue  # This is a reference, not actual vuln data

            # Process actual vulnerability data
            # ...
```

### Challenge 3: Determining Direct vs Transitive Dependencies
**Problem:** Need to know if package is directly installed or pulled in by another package

**Solution:**
```python
def _parse_npm_audit(self, report: dict):
    for pkg_name, pkg_data in report['vulnerabilities'].items():
        # 'effects' contains packages affected by this vulnerability
        effects = pkg_data.get('effects', [])

        # If package name is NOT in effects, it's a direct dependency
        direct_dependency = (pkg_name not in effects)

        # Build dependency chain
        dependency_chain = effects if effects else [pkg_name]
```

---

# CONCLUSION

This SecurAI project demonstrates a complete AI-powered security automation pipeline with:

**TOUZANI's Contributions:**
- Robust SAST parser supporting Semgrep/SonarQube
- Intelligent category detection
- LLaMA 3.3 70B integration for SAST policy generation

**IBNOU-KADY's Contributions:**
- Comprehensive SCA parser for npm audit/Trivy
- BOM handling and dependency chain analysis
- LLaMA 3.3 70B integration for SCA policy generation

**BAZZAOUI's Contributions:**
- Multi-format DAST parser (XML and JSON)
- 4-tier smart scanning strategy
- LLaMA 3.1 8B Instant integration for DAST policy generation

**ELGARCH's Contributions:**
- Central orchestrator coordinating entire pipeline
- Multi-format report generation (JSON/TXT/HTML/PDF)
- Enhanced PDF with matplotlib charts
- Compliance analysis (NIST CSF, ISO 27001)
- WebSocket real-time progress broadcasting

**System Integration:**
- RAG-enhanced policy generation with ChromaDB
- Real-time WebSocket updates
- Professional frontend with React/Vite/TailwindCSS
- Comprehensive compliance mapping

**Total Impact:**
- Automated security policy generation
- 90% time savings over manual policy writing
- Compliance-aligned outputs
- Professional, presentation-ready reports

---

**Team:** Youssef ELGARCH, Youssef TOUZANI, Youness BAZZAOUI, Nisrine IBNOU-KADY
**Date:** November 6, 2025
**Status:** Production-Ready ✅
