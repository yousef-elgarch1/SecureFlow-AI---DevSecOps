# AI-Powered DevSecOps Security Policy Generator
## Comprehensive Technical Report

**Project Title:** Automated Security Policy Generation System with AI and Multi-Scanner Integration
**Version:** 1.0
**Date:** November 2025
**Author:** GL Project Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [System Architecture](#3-system-architecture)
4. [Backend Technologies & Implementation](#4-backend-technologies--implementation)
5. [Frontend Technologies & Implementation](#5-frontend-technologies--implementation)
6. [Security Scanning Engines](#6-security-scanning-engines)
7. [AI & LLM Integration](#7-ai--llm-integration)
8. [RAG System & Compliance Mapping](#8-rag-system--compliance-mapping)
9. [Authentication & GitHub OAuth](#9-authentication--github-oauth)
10. [Operational Modes](#10-operational-modes)
11. [Data Flow & Pipeline](#11-data-flow--pipeline)
12. [Report Generation System](#12-report-generation-system)
13. [Testing & Validation](#13-testing--validation)
14. [Deployment & Configuration](#14-deployment--configuration)
15. [Performance & Scalability](#15-performance--scalability)
16. [Future Enhancements](#16-future-enhancements)
17. [Conclusion](#17-conclusion)

---

## 1. Executive Summary

### 1.1 Project Purpose

The AI-Powered DevSecOps Security Policy Generator is an innovative automated system that transforms raw vulnerability scan reports into comprehensive, compliance-mapped security policies using advanced Large Language Models (LLMs). The system integrates three critical security testing methodologies:

- **SAST** (Static Application Security Testing) - Code analysis
- **SCA** (Software Composition Analysis) - Dependency vulnerabilities
- **DAST** (Dynamic Application Security Testing) - Runtime testing

### 1.2 Key Innovation

This project combines cutting-edge AI technology with traditional security scanning to create a unified, intelligent DevSecOps platform that:

1. **Automates Policy Generation** - Converts technical vulnerabilities into actionable security policies
2. **Maps to Compliance Frameworks** - Automatically links vulnerabilities to NIST CSF, ISO 27001, OWASP
3. **Provides Dual Operational Modes** - Supports both file upload and direct GitHub repository scanning
4. **Real-Time Progress Tracking** - WebSocket-powered live updates during processing
5. **Multi-Format Output** - Generates TXT, HTML, PDF, and JSON reports

### 1.3 Target Users

- **Security Engineers** - Automated vulnerability-to-policy conversion
- **DevOps Teams** - CI/CD integration for continuous security
- **Compliance Officers** - Framework-mapped policy documentation
- **Development Teams** - Security guidance for remediation

### 1.4 Technology Stack Summary

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI, Python 3.11, WebSockets |
| **Frontend** | React 18, Vite, TailwindCSS, Recharts |
| **AI/LLM** | Groq API (LLaMA 3.3 70B, LLaMA 3.1 8B) |
| **RAG** | ChromaDB, Sentence Transformers, LangChain |
| **Scanners** | Semgrep (SAST), Trivy (SCA), OWASP ZAP (DAST) |
| **Authentication** | GitHub OAuth 2.0 |
| **Report Generation** | ReportLab, WeasyPrint, BeautifulSoup4 |

---

## 2. Project Overview

### 2.1 Problem Statement

Modern software development faces several critical challenges in security policy management:

1. **Manual Policy Creation** - Security teams spend hours converting vulnerability reports into policies
2. **Inconsistent Documentation** - Different formats and standards across teams
3. **Compliance Gaps** - Difficulty mapping vulnerabilities to regulatory frameworks
4. **Slow Remediation** - Lack of clear, actionable guidance for developers
5. **Scalability Issues** - Cannot handle large-scale scanning results efficiently

### 2.2 Solution Architecture

Our system addresses these challenges through:

#### 2.2.1 Automated Vulnerability Parsing
- Universal parsers for SAST, SCA, and DAST reports
- Support for multiple tool formats (Semgrep, npm audit, OWASP ZAP)
- Normalized vulnerability data structures

#### 2.2.2 AI-Powered Policy Generation
- Specialized LLMs for different vulnerability types
- Context-aware policy creation with compliance mapping
- Template-based structured output

#### 2.2.3 Real-Time Processing
- WebSocket-based progress tracking
- Asynchronous pipeline execution
- Interactive frontend dashboard

#### 2.2.4 Multi-Modal Input
- Direct GitHub repository scanning
- Manual report file upload
- Support for public and private repositories

### 2.3 System Features

#### Core Features
1. **Vulnerability Scanning**
   - SAST: Semgrep for code analysis
   - SCA: Trivy for dependency checking
   - DAST: 4-tier fallback system (URL → Auto-detect → Docker → Sample data)

2. **AI Policy Generation**
   - LLaMA 3.3 70B for SAST/SCA (most capable)
   - LLaMA 3.1 8B Instant for DAST (faster)
   - RAG-enhanced context retrieval

3. **Compliance Mapping**
   - NIST Cybersecurity Framework
   - ISO 27001:2013
   - OWASP Top 10

4. **Multi-Format Reports**
   - Text (.txt) - Human-readable
   - HTML (.html) - Interactive web view
   - PDF (.pdf) - Professional documents
   - JSON (.json) - Machine-readable data

5. **GitHub Integration**
   - OAuth 2.0 authentication
   - Public and private repository support
   - Branch selection
   - Automated cloning and scanning

6. **Real-Time Dashboard**
   - Live progress updates via WebSocket
   - Phase-by-phase visualization
   - Severity-based vulnerability distribution
   - Compliance framework breakdown

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Upload Mode  │  │ GitHub Mode  │  │   Results    │     │
│  │   Component  │  │  Component   │  │   Dashboard  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                           │                                  │
│                     React Router                             │
│                           │                                  │
│                   ┌───────▼────────┐                        │
│                   │   API Client   │                        │
│                   │  (axios + WS)  │                        │
│                   └───────┬────────┘                        │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP/WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     API Gateway Layer                        │
│                      (FastAPI)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WebSocket Manager                       │   │
│  │       (Real-time Progress Broadcasting)              │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                    │                             │
│  ┌────────▼────────┐  ┌───────▼────────┐                  │
│  │ Upload Endpoint │  │ GitHub Endpoint│                  │
│  │  /api/upload    │  │  /api/scan-   │                  │
│  │                  │  │   github       │                  │
│  └─────────────────┘  └────────────────┘                  │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                  Processing Layer                             │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Policy Generator Orchestrator                │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │   Parsers    │  │ RAG Retriever│  │ LLM Clients │ │  │
│  │  │ SAST/SCA/    │  │  (ChromaDB)  │  │   (Groq)    │ │  │
│  │  │   DAST       │  │              │  │             │ │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              GitHub Scanner Module                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │   Cloner     │  │   Semgrep    │  │   Trivy    │  │  │
│  │  │              │  │   Scanner    │  │   Scanner  │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Smart DAST Scanner (4-Tier)                  │  │
│  │  Tier 1: User URL → Tier 2: Auto-detect →             │  │
│  │  Tier 3: Docker → Tier 4: Sample Data                  │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                   Data/Storage Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │  ChromaDB   │  │   Outputs   │  │  Temp Files  │         │
│  │  (Vectors)  │  │  (Reports)  │  │  (Scans)     │         │
│  └─────────────┘  └─────────────┘  └──────────────┘         │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 Component Architecture

#### 3.2.1 Frontend Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── UploadMode.jsx          # File upload interface
│   │   ├── GitHubMode.jsx          # GitHub scanning interface
│   │   ├── GitHubLogin.jsx         # OAuth authentication
│   │   ├── ResultsView.jsx         # Policy display
│   │   ├── WorkflowView.jsx        # Progress tracking
│   │   ├── RealTimeDashboard.jsx   # Live statistics
│   │   └── workflow/
│   │       ├── PhaseSection.jsx    # Pipeline phases
│   │       ├── ParserStep.jsx      # Parser progress
│   │       ├── RAGStep.jsx         # RAG retrieval
│   │       └── LLMGenerationStep.jsx # AI generation
│   ├── pages/
│   │   └── GitHubCallback.jsx      # OAuth callback handler
│   ├── utils/
│   │   └── api.js                  # API client + WebSocket
│   ├── App.jsx                     # Main application
│   └── main.jsx                    # Entry point
├── package.json
├── vite.config.js
└── tailwind.config.js
```

#### 3.2.2 Backend Architecture

```
backend/
├── api/
│   ├── main.py                     # FastAPI application
│   └── github_oauth.py             # OAuth endpoints
├── orchestrator/
│   └── policy_generator.py         # Main orchestration
├── parsers/
│   ├── sast_parser.py              # SAST report parsing
│   ├── sca_parser.py               # SCA report parsing
│   └── dast_parser.py              # DAST report parsing
├── scanners/
│   ├── github_scanner.py           # Repository operations
│   ├── smart_dast_scanner.py       # 4-tier DAST system
│   ├── zap_scanner.py              # OWASP ZAP integration
│   └── nuclei_scanner.py           # Nuclei integration
├── rag/
│   ├── retriever.py                # Compliance retrieval
│   ├── vector_store.py             # ChromaDB wrapper
│   └── init_vectordb.py            # Database initialization
├── llm_integrations/
│   ├── groq_client.py              # Groq API client
│   └── huggingface_client.py       # HuggingFace client
├── prompts/
│   └── policy_templates.py         # LLM prompt templates
└── compliance/
    └── frameworks/
        ├── nist_csf.json           # NIST framework
        ├── iso_27001.json          # ISO 27001
        └── owasp_top10.json        # OWASP Top 10
```

### 3.3 Technology Stack Details

#### 3.3.1 Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.109.0 | REST API framework |
| **Uvicorn** | 0.27.0 | ASGI server |
| **WebSockets** | 12.0 | Real-time communication |
| **Pydantic** | 2.5.3 | Data validation |
| **ChromaDB** | 0.4.22 | Vector database |
| **Sentence Transformers** | 2.3.1 | Embeddings |
| **LangChain** | 0.1.4 | LLM orchestration |
| **Groq** | 0.4.2 | LLM API client |
| **httpx** | 0.26.0 | Async HTTP |
| **BeautifulSoup4** | 4.12.3 | XML/HTML parsing |
| **ReportLab** | 4.0.9 | PDF generation |
| **python-dotenv** | 1.0.1 | Environment management |

#### 3.3.2 Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **Vite** | 5.0.0 | Build tool |
| **React Router** | 7.9.5 | Routing |
| **Axios** | 1.6.0 | HTTP client |
| **TailwindCSS** | 3.3.0 | Styling |
| **Recharts** | 2.10.0 | Data visualization |
| **Lucide React** | 0.294.0 | Icons |

#### 3.3.3 Security Scanning Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| **Semgrep** | SAST | Source code | JSON |
| **Trivy** | SCA | Dependencies | JSON |
| **OWASP ZAP** | DAST | Running app | XML/JSON |
| **Nuclei** | DAST (fallback) | URLs | JSON |

---

## 4. Backend Technologies & Implementation

### 4.1 FastAPI Application (main.py)

#### 4.1.1 Core Structure

The FastAPI application serves as the central API gateway with the following key features:

**File:** `backend/api/main.py` (916 lines)

**Key Components:**
1. **CORS Middleware** - Enables cross-origin requests from frontend
2. **WebSocket Manager** - Handles multiple simultaneous connections
3. **Static File Serving** - Serves generated reports
4. **Async Processing** - ThreadPoolExecutor for concurrent operations
5. **Error Handling** - Comprehensive exception management

**Code Excerpt:**
```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)
```

#### 4.1.2 API Endpoints

**1. Health Check**
```
GET /api/health
Response: {"status": "healthy", "timestamp": "..."}
```

**2. Upload Mode**
```
POST /api/upload
Content-Type: multipart/form-data
Files: sast_file, sca_file, dast_file (optional)
Body: max_per_type (int)
Response: PolicyGenerationResponse
```

**3. GitHub Scanning**
```
POST /api/scan-github
Content-Type: application/json
Body: {
  "repo_url": "https://github.com/user/repo",
  "branch": "main",
  "scan_types": {"sast": true, "sca": true, "dast": false},
  "max_per_type": 5,
  "token": "optional_github_token",
  "dast_url": "optional_deployment_url"
}
Response: PolicyGenerationResponse
```

**4. WebSocket Connection**
```
WS /ws/progress
Messages: {
  "phase": "parsing|rag|generation|saving|complete",
  "status": "in_progress|success|error",
  "message": "Human-readable status",
  "data": {...}
}
```

**5. File Download**
```
GET /api/outputs/{filename}
Response: File content (TXT/HTML/PDF/JSON)
```

#### 4.1.3 Real-Time Progress Broadcasting

The system uses WebSockets to provide live updates during policy generation:

```python
async def broadcast_realtime_generation(
    sast_path: Optional[str],
    sca_path: Optional[str],
    dast_path: Optional[str],
    max_per_type: int = 5
) -> Dict:
    """
    Broadcast real-time policy generation updates to all WebSocket clients
    Returns: Dictionary with results, compliance_analysis, and output_files
    """

    # Phase 1: Parsing
    await broadcast_progress({
        'phase': 'parsing',
        'status': 'in_progress',
        'message': 'Parsing SAST report (Semgrep)...'
    })

    # Phase 2: RAG Retrieval
    await broadcast_progress({
        'phase': 'rag',
        'status': 'in_progress',
        'message': 'Retrieving compliance context...'
    })

    # Phase 3: LLM Generation (per vulnerability)
    for i, vuln in enumerate(vulnerabilities):
        await broadcast_progress({
            'phase': 'generation',
            'status': 'in_progress',
            'message': f'Generating policy {i+1}/{total}...'
        })

    # Phase 4: Saving
    await broadcast_progress({
        'phase': 'saving',
        'status': 'in_progress',
        'message': 'Saving reports...'
    })

    # Phase 5: Complete
    await broadcast_progress({
        'phase': 'complete',
        'status': 'success',
        'data': {
            'results': results,
            'output_files': output_files
        }
    })
```

### 4.2 Orchestrator (policy_generator.py)

#### 4.2.1 Pipeline Orchestration

The `PolicyGeneratorOrchestrator` class coordinates the entire policy generation workflow:

**File:** `backend/orchestrator/policy_generator.py` (916 lines)

**Initialization:**
```python
class PolicyGeneratorOrchestrator:
    def __init__(self, use_rag: bool = True, output_dir: str = "./outputs"):
        # Initialize parsers
        self.sast_parser = SASTParser()
        self.sca_parser = SCAParser()
        self.dast_parser = DASTParser()

        # Initialize RAG retriever
        if use_rag:
            self.retriever = ComplianceRetriever()

        # Initialize specialized LLM clients
        self.llm_clients = {
            'sast': GroqClient(model="llama-3.3-70b-versatile"),
            'sca': GroqClient(model="llama-3.3-70b-versatile"),
            'dast': GroqClient(model="llama-3.1-8b-instant")
        }

        # Initialize prompt templates
        self.prompt_templates = PolicyPromptTemplates()
```

#### 4.2.2 Three-Step Pipeline

**Step 1: Parse Reports**
```python
def parse_reports(self, sast_path, sca_path, dast_path):
    sast_vulns = []
    if sast_path:
        with open(sast_path, 'r') as f:
            sast_vulns = self.sast_parser.parse(f.read())

    sca_vulns = []
    if sca_path:
        with open(sca_path, 'r') as f:
            sca_vulns = self.sca_parser.parse(f.read())

    dast_vulns = []
    if dast_path:
        with open(dast_path, 'r') as f:
            dast_vulns = self.dast_parser.parse(f.read())

    return sast_vulns, sca_vulns, dast_vulns
```

**Step 2: Generate Policies**
```python
def generate_policy_for_vulnerability(self, vulnerability, vuln_type):
    # Get compliance context from RAG
    if self.use_rag:
        rag_result = self.retriever.retrieve_for_vulnerability(
            vulnerability,
            top_k=5
        )
        compliance_context = rag_result['formatted_context']

    # Generate prompt
    system_prompt = self.prompt_templates.get_system_prompt()
    user_prompt = self.prompt_templates.get_policy_generation_prompt(
        vulnerability,
        compliance_context,
        severity
    )

    # Select specialized LLM
    client = self.llm_clients.get(vuln_type.lower())

    # Generate policy
    policy = client.generate(
        user_prompt,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=1500
    )

    return policy
```

**Step 3: Save Results**
```python
def save_results(self, results, sast_vulns, sca_vulns, dast_vulns):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_path = self.output_dir / f"policy_generation_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Generate TXT report
    report_path = self.output_dir / f"security_policy_{timestamp}.txt"
    # ... (text formatting)

    # Generate HTML report
    html_path = self.output_dir / f"security_policy_{timestamp}.html"
    self._generate_html_report(...)

    # Generate PDF report
    pdf_path = self.output_dir / f"security_policy_{timestamp}.pdf"
    self._generate_pdf_report(...)

    return str(report_path)
```

### 4.3 Parsers

#### 4.3.1 SAST Parser (sast_parser.py)

**Purpose:** Parse Semgrep JSON reports into normalized vulnerability objects

**File:** `backend/parsers/sast_parser.py` (265 lines)

**Data Structure:**
```python
@dataclass
class SASTVulnerability:
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # SQL Injection, XSS, etc.
    file_path: str
    line_number: int
    cwe_id: Optional[str]
    description: str
    recommendation: str
    confidence: str = "HIGH"
```

**Parsing Logic:**
```python
def _parse_semgrep(self, data: Dict) -> List[SASTVulnerability]:
    vulnerabilities = []

    for result in data.get('results', []):
        extra = result.get('extra', {})
        metadata = extra.get('metadata', {})

        # Extract CWE
        cwe_id = metadata.get('cwe')

        # Normalize severity
        severity = self._normalize_severity(extra.get('severity', 'MEDIUM'))

        # Extract category
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
            recommendation=extra.get('fix', 'Review and fix'),
            confidence=metadata.get('confidence', 'HIGH')
        )

        vulnerabilities.append(vuln)

    return vulnerabilities
```

**Category Extraction:**
```python
def _extract_category(self, check_id: str, message: str) -> str:
    if 'sqli' in check_id.lower():
        return 'SQL Injection'
    elif 'xss' in check_id.lower():
        return 'Cross-Site Scripting (XSS)'
    elif 'csrf' in check_id.lower():
        return 'Cross-Site Request Forgery (CSRF)'
    elif 'path-traversal' in check_id.lower():
        return 'Path Traversal'
    elif 'command-injection' in check_id.lower():
        return 'Command Injection'
    elif 'hardcoded' in check_id.lower():
        return 'Hardcoded Secrets'
    # ... (more patterns)
    else:
        return 'Security Vulnerability'
```

#### 4.3.2 SCA Parser (sca_parser.py)

**Purpose:** Parse npm audit/Trivy reports into dependency vulnerability objects

**File:** `backend/parsers/sca_parser.py` (271 lines)

**Data Structure:**
```python
@dataclass
class SCAVulnerability:
    package_name: str
    current_version: str
    vulnerable_versions: str
    patched_version: Optional[str]
    cve_id: str
    severity: str
    description: str
    exploitability: Optional[str]
    fix_available: bool = False
```

**Parsing Logic (npm audit format):**
```python
def _parse_npm_audit(self, data: Dict) -> List[SCAVulnerability]:
    vulnerabilities = []
    vulns_data = data.get('vulnerabilities', {})

    for package_name, vuln_info_or_array in vulns_data.items():
        # Handle both single object and array formats
        vuln_list = vuln_info_or_array if isinstance(vuln_info_or_array, list) else [vuln_info_or_array]

        for vuln_info in vuln_list:
            severity = self._normalize_severity(vuln_info.get('severity', 'MEDIUM'))

            # Extract CVE/advisory
            cve_id = 'N/A'
            if 'cwe' in vuln_info:
                cwe_list = vuln_info['cwe']
                if isinstance(cwe_list, list) and cwe_list:
                    cve_id = cwe_list[0]

            # Get fix information
            fix_available = False
            patched_version = None
            fix_info = vuln_info.get('fixAvailable', {})
            if fix_info and isinstance(fix_info, dict):
                fix_available = True
                patched_version = fix_info.get('version', None)

            vuln = SCAVulnerability(
                package_name=package_name,
                current_version=vuln_info.get('version', 'Unknown'),
                vulnerable_versions=vuln_info.get('range', 'Unknown'),
                patched_version=patched_version,
                cve_id=cve_id,
                severity=severity,
                description=vuln_info.get('title', 'No description'),
                exploitability=None,
                fix_available=fix_available
            )

            vulnerabilities.append(vuln)

    return vulnerabilities
```

#### 4.3.3 DAST Parser (dast_parser.py)

**Purpose:** Parse OWASP ZAP XML reports into runtime vulnerability objects

**File:** `backend/parsers/dast_parser.py` (288 lines)

**Data Structure:**
```python
@dataclass
class DASTVulnerability:
    url: str
    endpoint: str
    method: str  # GET, POST, etc.
    issue_type: str  # SQL Injection, XSS, etc.
    risk_level: str
    confidence: str
    description: str
    solution: str
    cwe_id: Optional[str]
```

**Parsing Logic (OWASP ZAP XML):**
```python
def _parse_zap_xml(self, xml_content: str) -> List[DASTVulnerability]:
    vulnerabilities = []
    soup = BeautifulSoup(xml_content, 'xml')

    alerts = soup.find_all('alertitem')

    for alert in alerts:
        # Extract risk code and convert
        risk_code = alert.find('riskcode')
        risk_level = self._normalize_risk(
            risk_code.text if risk_code else '1'
        )

        # Extract CWE
        cwe_elem = alert.find('cweid')
        cwe_id = f"CWE-{cwe_elem.text}" if cwe_elem else None

        # Get instance details
        instances = alert.find_all('instance')
        if instances:
            first_instance = instances[0]
            url = first_instance.find('uri')
            method = first_instance.find('method')
            url_text = url.text if url else 'Unknown'
            method_text = method.text if method else 'GET'

        vuln = DASTVulnerability(
            url=url_text,
            endpoint=self._extract_endpoint(url_text),
            method=method_text,
            issue_type=alert.find('alert').text,
            risk_level=risk_level,
            confidence=alert.find('confidence').text,
            description=alert.find('desc').text,
            solution=alert.find('solution').text,
            cwe_id=cwe_id
        )

        vulnerabilities.append(vuln)

    return vulnerabilities
```

### 4.4 GitHub Scanner Module

#### 4.4.1 Repository Operations (github_scanner.py)

**Purpose:** Clone repositories and run security scans

**File:** `backend/scanners/github_scanner.py` (478 lines)

**Key Features:**
- OAuth-authenticated cloning for private repos
- Automatic retry on failure (3 attempts)
- Progress callback support
- Cross-platform compatibility (Windows, Linux, macOS)
- Automatic cleanup

**Clone Method:**
```python
def clone_repository(
    self,
    repo_url: str,
    branch: str = "main",
    token: Optional[str] = None,
    progress_callback=None
) -> Path:
    # Create temp directory
    self.temp_dir = tempfile.mkdtemp(prefix="github_scan_")

    # Build authenticated URL if token provided
    clone_url = repo_url
    if token:
        if clone_url.startswith('https://github.com/'):
            clone_url = clone_url.replace(
                'https://github.com/',
                f'https://{token}@github.com/'
            )

    # Retry up to 3 times
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, "--progress", clone_url, str(self.repo_path)],
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
        )

        if result.returncode == 0:
            return self.repo_path

        if attempt < max_retries:
            if progress_callback:
                progress_callback(f"Clone attempt {attempt} failed, retrying...")
            continue
        else:
            raise Exception(f"Git clone failed after {max_retries} attempts")

    return self.repo_path
```

**Semgrep Scanner:**
```python
class SemgrepScanner:
    @staticmethod
    def scan(repo_path: Path) -> Dict:
        # Run Semgrep with security rules
        result = subprocess.run(
            ["semgrep", "--config=auto", "--json", str(repo_path)],
            capture_output=True,
            text=True,
            timeout=300
        )

        scan_results = json.loads(result.stdout)

        # Convert to normalized format
        vulnerabilities = []
        for finding in scan_results.get('results', []):
            vuln = {
                "check_id": finding.get('check_id'),
                "severity": finding['extra']['severity'].upper(),
                "message": finding['extra']['message'],
                "file": finding['path'],
                "line": finding['start']['line'],
                "cwe": finding['extra']['metadata'].get('cwe')
            }
            vulnerabilities.append(vuln)

        return {
            "tool": "Semgrep",
            "scan_type": "SAST",
            "vulnerabilities": vulnerabilities,
            "raw_results": scan_results,  # Keep for parser
            "summary": {
                "total": len(vulnerabilities),
                "critical": len([v for v in vulnerabilities if v["severity"] == "CRITICAL"]),
                "high": len([v for v in vulnerabilities if v["severity"] == "HIGH"]),
                "medium": len([v for v in vulnerabilities if v["severity"] == "MEDIUM"]),
                "low": len([v for v in vulnerabilities if v["severity"] == "LOW"])
            }
        }
```

**Trivy SCA Scanner:**
```python
class TrivyScanner:
    @staticmethod
    def scan(repo_path: Path) -> Dict:
        # Run Trivy filesystem scan
        result = subprocess.run(
            ["trivy", "fs", "--format", "json", "--severity", "CRITICAL,HIGH,MEDIUM,LOW", str(repo_path)],
            capture_output=True,
            text=True,
            timeout=300
        )

        scan_results = json.loads(result.stdout)

        # Extract vulnerabilities
        vulnerabilities = []
        for result_item in scan_results.get('Results', []):
            for vuln in result_item.get('Vulnerabilities', []):
                vulnerabilities.append({
                    "package": vuln.get('PkgName'),
                    "version": vuln.get('InstalledVersion'),
                    "vulnerability_id": vuln.get('VulnerabilityID'),
                    "severity": vuln.get('Severity'),
                    "title": vuln.get('Title'),
                    "description": vuln.get('Description'),
                    "fixed_version": vuln.get('FixedVersion')
                })

        return {
            "tool": "Trivy",
            "scan_type": "SCA",
            "vulnerabilities": vulnerabilities,
            "summary": {
                "total": len(vulnerabilities),
                "critical": len([v for v in vulnerabilities if v["severity"] == "CRITICAL"]),
                "high": len([v for v in vulnerabilities if v["severity"] == "HIGH"])
            }
        }
```

#### 4.4.2 Smart DAST Scanner (smart_dast_scanner.py)

**Purpose:** 4-tier fallback system for dynamic testing

**File:** `backend/scanners/smart_dast_scanner.py` (370 lines)

**Tier Architecture:**
```python
class SmartDASTScanner:
    def scan(self, repo_path: Path, repo_url: str, branch: str, provided_url: Optional[str] = None):
        # Tier 1: User-provided URL
        if provided_url:
            if self._is_url_alive(provided_url):
                return self._scan_url(provided_url)

        # Tier 2: Auto-detect deployment
        detected_url = self._detect_deployment(repo_url, branch)
        if detected_url:
            if self._is_url_alive(detected_url):
                return self._scan_url(detected_url)

        # Tier 3: Docker-based local deployment
        try:
            docker_result = self._docker_deploy_and_scan(repo_path)
            if docker_result:
                return docker_result
        except Exception as e:
            logger.warning(f"Docker deployment failed: {e}")

        # Tier 4: Sample data fallback
        return self._generate_sample_dast_data()
```

**Auto-Detection Logic:**
```python
def _detect_deployment(self, repo_url: str, branch: str) -> Optional[str]:
    # GitHub Pages
    if 'github.com' in repo_url:
        parts = repo_url.split('/')
        username = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        pages_url = f"https://{username}.github.io/{repo_name}/"
        if self._is_url_alive(pages_url):
            return pages_url

    # Heroku
    heroku_url = f"https://{repo_name}.herokuapp.com"
    if self._is_url_alive(heroku_url):
        return heroku_url

    # Vercel
    vercel_url = f"https://{repo_name}.vercel.app"
    if self._is_url_alive(vercel_url):
        return vercel_url

    # Netlify
    netlify_url = f"https://{repo_name}.netlify.app"
    if self._is_url_alive(netlify_url):
        return netlify_url

    return None
```

**Docker Deployment:**
```python
def _docker_deploy_and_scan(self, repo_path: Path) -> Optional[Dict]:
    # Detect app type
    if (repo_path / "package.json").exists():
        return self._deploy_nodejs_app(repo_path)
    elif (repo_path / "requirements.txt").exists():
        return self._deploy_python_app(repo_path)
    elif (repo_path / "pom.xml").exists():
        return self._deploy_java_app(repo_path)

    return None

def _deploy_nodejs_app(self, repo_path: Path) -> Dict:
    # Build Docker image
    dockerfile_content = """
    FROM node:16-alpine
    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    EXPOSE 3000
    CMD ["npm", "start"]
    """

    dockerfile_path = repo_path / "Dockerfile.temp"
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)

    # Build image
    image_name = f"dast-scan-{uuid.uuid4().hex[:8]}"
    subprocess.run(["docker", "build", "-t", image_name, "-f", str(dockerfile_path), str(repo_path)])

    # Run container
    port = self._find_free_port()
    container_id = subprocess.run(
        ["docker", "run", "-d", "-p", f"{port}:3000", image_name],
        capture_output=True
    ).stdout.strip()

    # Wait for startup
    time.sleep(10)

    # Scan localhost
    scan_result = self._scan_url(f"http://localhost:{port}")

    # Cleanup
    subprocess.run(["docker", "stop", container_id])
    subprocess.run(["docker", "rm", container_id])
    subprocess.run(["docker", "rmi", image_name])

    return scan_result
```

---

## 5. Frontend Technologies & Implementation

### 5.1 React Application Structure

#### 5.1.1 Main Application (App.jsx)

**Purpose:** Root component managing application state and routing

**File:** `frontend/src/App.jsx`

**State Management:**
```javascript
const [mode, setMode] = useState('upload');  // 'upload' or 'github'
const [processing, setProcessing] = useState(false);
const [progress, setProgress] = useState([]);
const [results, setResults] = useState(null);
const [githubToken, setGithubToken] = useState(null);
const [githubUser, setGithubUser] = useState(null);
```

**WebSocket Integration:**
```javascript
useEffect(() => {
  apiClient.connectWebSocket((data) => {
    console.log('Progress update:', data);
    setProgress(prev => [...prev, data]);

    if (data.phase === 'complete') {
      setResults(data.data);
      setProcessing(false);
      apiClient.disconnectWebSocket();
    }
  });

  return () => apiClient.disconnectWebSocket();
}, []);
```

**Upload Handler:**
```javascript
const handleUpload = async (files, maxPerType) => {
  setProcessing(true);
  setProgress([]);
  setResults(null);

  try {
    const response = await apiClient.uploadFiles(
      files.sast,
      files.sca,
      files.dast,
      maxPerType
    );

    // WebSocket will update results
  } catch (error) {
    console.error('Upload failed:', error);
    setProcessing(false);
  }
};
```

**GitHub Scan Handler:**
```javascript
const handleGitHubScan = async (repoUrl, branch, scanTypes, maxPerType, dastUrl) => {
  setProcessing(true);
  setProgress([]);
  setResults(null);

  try {
    const response = await apiClient.scanGitHubRepo(
      repoUrl,
      branch,
      scanTypes,
      maxPerType,
      githubToken,
      dastUrl
    );

    // WebSocket will update results
  } catch (error) {
    console.error('GitHub scan failed:', error);
    setProcessing(false);
  }
};
```

### 5.2 Component Architecture

#### 5.2.1 Upload Mode Component

**File:** `frontend/src/components/UploadMode.jsx`

**Features:**
- Drag-and-drop file upload
- File type validation
- Preview of selected files
- Max vulnerabilities per type selection

**Key Code:**
```javascript
const UploadMode = ({ onUpload, processing }) => {
  const [files, setFiles] = useState({
    sast: null,
    sca: null,
    dast: null
  });
  const [maxPerType, setMaxPerType] = useState(5);

  const handleDrop = (e, type) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];

    // Validate file type
    if (type === 'sast' && droppedFile.name.endsWith('.json')) {
      setFiles(prev => ({ ...prev, sast: droppedFile }));
    } else if (type === 'sca' && droppedFile.name.endsWith('.json')) {
      setFiles(prev => ({ ...prev, sca: droppedFile }));
    } else if (type === 'dast' && (droppedFile.name.endsWith('.xml') || droppedFile.name.endsWith('.json'))) {
      setFiles(prev => ({ ...prev, dast: droppedFile }));
    } else {
      alert('Invalid file type!');
    }
  };

  const handleSubmit = () => {
    if (!files.sast && !files.sca && !files.dast) {
      alert('Please upload at least one file');
      return;
    }
    onUpload(files, maxPerType);
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* SAST Upload */}
        <FileDropZone
          type="sast"
          file={files.sast}
          onDrop={(e) => handleDrop(e, 'sast')}
          label="SAST Report (JSON)"
          icon={<Code className="w-12 h-12" />}
        />

        {/* SCA Upload */}
        <FileDropZone
          type="sca"
          file={files.sca}
          onDrop={(e) => handleDrop(e, 'sca')}
          label="SCA Report (JSON)"
          icon={<Package className="w-12 h-12" />}
        />

        {/* DAST Upload */}
        <FileDropZone
          type="dast"
          file={files.dast}
          onDrop={(e) => handleDrop(e, 'dast')}
          label="DAST Report (XML/JSON)"
          icon={<Globe className="w-12 h-12" />}
        />
      </div>

      {/* Max per type selector */}
      <div className="flex items-center gap-4">
        <label>Max vulnerabilities per type:</label>
        <select value={maxPerType} onChange={(e) => setMaxPerType(Number(e.target.value))}>
          <option value={3}>3</option>
          <option value={5}>5</option>
          <option value={10}>10</option>
          <option value={15}>15</option>
        </select>
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={processing || (!files.sast && !files.sca && !files.dast)}
        className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg"
      >
        {processing ? 'Generating...' : 'Generate Security Policies'}
      </button>
    </div>
  );
};
```

#### 5.2.2 GitHub Mode Component

**File:** `frontend/src/components/GitHubMode.jsx`

**Features:**
- OAuth login button
- Repository URL input
- Branch selection
- Scan type toggles (SAST/SCA/DAST)
- Optional DAST URL input

**Key Code:**
```javascript
const GitHubMode = ({ onScan, processing, githubUser, githubToken, onLogin }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [scanTypes, setScanTypes] = useState({
    sast: true,
    sca: true,
    dast: false
  });
  const [dastUrl, setDastUrl] = useState('');
  const [maxPerType, setMaxPerType] = useState(5);

  const handleSubmit = () => {
    if (!repoUrl) {
      alert('Please enter a repository URL');
      return;
    }

    if (!githubToken) {
      alert('Please log in with GitHub');
      return;
    }

    onScan(repoUrl, branch, scanTypes, maxPerType, dastUrl);
  };

  return (
    <div className="space-y-6">
      {/* GitHub Login */}
      {!githubUser ? (
        <GitHubLogin onLogin={onLogin} />
      ) : (
        <div className="flex items-center gap-4 p-4 bg-green-50 rounded-lg">
          <img src={githubUser.avatar_url} className="w-12 h-12 rounded-full" />
          <div>
            <p className="font-semibold">{githubUser.name || githubUser.login}</p>
            <p className="text-sm text-gray-600">@{githubUser.login}</p>
          </div>
        </div>
      )}

      {/* Repository URL */}
      <div>
        <label className="block text-sm font-medium mb-2">Repository URL</label>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/username/repo"
          className="w-full px-4 py-2 border rounded-lg"
        />
      </div>

      {/* Branch */}
      <div>
        <label className="block text-sm font-medium mb-2">Branch</label>
        <input
          type="text"
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          placeholder="main"
          className="w-full px-4 py-2 border rounded-lg"
        />
      </div>

      {/* Scan Types */}
      <div className="space-y-2">
        <label className="block text-sm font-medium mb-2">Scan Types</label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={scanTypes.sast}
              onChange={(e) => setScanTypes(prev => ({ ...prev, sast: e.target.checked }))}
            />
            <span>SAST (Code Analysis)</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={scanTypes.sca}
              onChange={(e) => setScanTypes(prev => ({ ...prev, sca: e.target.checked }))}
            />
            <span>SCA (Dependencies)</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={scanTypes.dast}
              onChange={(e) => setScanTypes(prev => ({ ...prev, dast: e.target.checked }))}
            />
            <span>DAST (Runtime)</span>
          </label>
        </div>
      </div>

      {/* DAST URL (optional) */}
      {scanTypes.dast && (
        <div>
          <label className="block text-sm font-medium mb-2">
            DAST URL (optional - leave blank for auto-detection)
          </label>
          <input
            type="text"
            value={dastUrl}
            onChange={(e) => setDastUrl(e.target.value)}
            placeholder="https://your-app.com"
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
      )}

      {/* Max per type */}
      <div className="flex items-center gap-4">
        <label>Max vulnerabilities per type:</label>
        <select value={maxPerType} onChange={(e) => setMaxPerType(Number(e.target.value))}>
          <option value={3}>3</option>
          <option value={5}>5</option>
          <option value={10}>10</option>
          <option value={15}>15</option>
        </select>
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={processing || !githubUser}
        className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg"
      >
        {processing ? 'Scanning...' : 'Start AI Generation'}
      </button>
    </div>
  );
};
```

#### 5.2.3 Workflow View Component

**File:** `frontend/src/components/WorkflowView.jsx`

**Purpose:** Real-time visualization of the processing pipeline

**Features:**
- Phase-by-phase progress tracking
- Animated progress indicators
- Detailed step information
- Error handling and display

**Key Code:**
```javascript
const WorkflowView = ({ progress }) => {
  const phases = {
    github_clone: { title: 'GitHub Clone', icon: <GitBranch /> },
    sast_scan: { title: 'SAST Scan', icon: <Code /> },
    sca_scan: { title: 'SCA Scan', icon: <Package /> },
    dast_scan: { title: 'DAST Scan', icon: <Globe /> },
    parsing: { title: 'Parsing Reports', icon: <FileText /> },
    rag: { title: 'RAG Retrieval', icon: <Database /> },
    generation: { title: 'AI Generation', icon: <Cpu /> },
    saving: { title: 'Saving Reports', icon: <Save /> },
    complete: { title: 'Complete', icon: <CheckCircle /> }
  };

  // Group progress updates by phase
  const phaseGroups = progress.reduce((acc, update) => {
    const phase = update.phase || 'other';
    if (!acc[phase]) acc[phase] = [];
    acc[phase].push(update);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {Object.entries(phases).map(([phaseKey, phaseInfo]) => {
        const phaseUpdates = phaseGroups[phaseKey] || [];
        const latestUpdate = phaseUpdates[phaseUpdates.length - 1];
        const status = latestUpdate?.status || 'pending';

        return (
          <PhaseSection
            key={phaseKey}
            title={phaseInfo.title}
            icon={phaseInfo.icon}
            status={status}
            updates={phaseUpdates}
          />
        );
      })}
    </div>
  );
};
```

#### 5.2.4 Results View Component

**File:** `frontend/src/components/ResultsView.jsx`

**Purpose:** Display generated policies with filtering and export options

**Features:**
- Policy cards with syntax highlighting
- Filter by type (SAST/SCA/DAST)
- Filter by severity
- Download reports
- Compliance framework breakdown

**Key Code:**
```javascript
const ResultsView = ({ results }) => {
  const [filterType, setFilterType] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');

  const filteredResults = results.results.filter(policy => {
    const typeMatch = filterType === 'all' || policy.type === filterType;
    const severityMatch = filterSeverity === 'all' || policy.vulnerability?.severity === filterSeverity;
    return typeMatch && severityMatch;
  });

  const downloadReport = async (format) => {
    const filename = results.output_files[format];
    window.open(`http://localhost:8000/api/outputs/${filename}`, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header with stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Policies"
          value={results.results.length}
          icon={<FileText />}
        />
        <StatsCard
          title="SAST"
          value={results.results.filter(r => r.type === 'SAST').length}
          icon={<Code />}
        />
        <StatsCard
          title="SCA"
          value={results.results.filter(r => r.type === 'SCA').length}
          icon={<Package />}
        />
        <StatsCard
          title="DAST"
          value={results.results.filter(r => r.type === 'DAST').length}
          icon={<Globe />}
        />
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">All Types</option>
          <option value="SAST">SAST</option>
          <option value="SCA">SCA</option>
          <option value="DAST">DAST</option>
        </select>

        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {/* Download buttons */}
      <div className="flex gap-4">
        <button onClick={() => downloadReport('txt')} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
          Download TXT
        </button>
        <button onClick={() => downloadReport('html')} className="px-4 py-2 bg-green-600 text-white rounded-lg">
          Download HTML
        </button>
        <button onClick={() => downloadReport('pdf')} className="px-4 py-2 bg-red-600 text-white rounded-lg">
          Download PDF
        </button>
        <button onClick={() => downloadReport('json')} className="px-4 py-2 bg-purple-600 text-white rounded-lg">
          Download JSON
        </button>
      </div>

      {/* Policy cards */}
      <div className="space-y-4">
        {filteredResults.map((policy, index) => (
          <PolicyCard key={index} policy={policy} index={index + 1} />
        ))}
      </div>
    </div>
  );
};
```

### 5.3 API Client & WebSocket

**File:** `frontend/src/utils/api.js`

**Purpose:** Centralized API communication with WebSocket support

**Key Features:**
- Axios for HTTP requests
- WebSocket for real-time updates
- Error handling
- Timeout management

**Implementation:**
```javascript
class APIClient {
  constructor() {
    this.baseURL = 'http://localhost:8000';
    this.ws = null;
  }

  // HTTP Methods
  async uploadFiles(sastFile, scaFile, dastFile, maxPerType) {
    const formData = new FormData();
    if (sastFile) formData.append('sast_file', sastFile);
    if (scaFile) formData.append('sca_file', scaFile);
    if (dastFile) formData.append('dast_file', dastFile);
    formData.append('max_per_type', maxPerType);

    const response = await axios.post(
      `${this.baseURL}/api/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 600000  // 10 minutes
      }
    );

    return response.data;
  }

  async scanGitHubRepo(repoUrl, branch, scanTypes, maxPerType, token, dastUrl) {
    const response = await axios.post(
      `${this.baseURL}/api/scan-github`,
      {
        repo_url: repoUrl,
        branch,
        scan_types: scanTypes,
        max_per_type: maxPerType,
        token,
        dast_url: dastUrl
      },
      { timeout: 1200000 }  // 20 minutes
    );

    return response.data;
  }

  // WebSocket Methods
  connectWebSocket(onMessage) {
    this.ws = new WebSocket(`ws://localhost:8000/ws/progress`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // GitHub OAuth Methods
  async getGitHubAuthUrl() {
    const response = await axios.get(`${this.baseURL}/api/auth/github`);
    return response.data;
  }

  async getGitHubUser(token) {
    const response = await axios.get(
      `${this.baseURL}/api/auth/github/user`,
      { params: { token } }
    );
    return response.data;
  }
}

export default new APIClient();
```

---

## 6. Security Scanning Engines

### 6.1 SAST: Semgrep

**Purpose:** Static code analysis to find security vulnerabilities in source code

**Tool:** Semgrep v1.45+
**Website:** https://semgrep.dev/
**License:** LGPL 2.1 (Open Source)

#### 6.1.1 Why Semgrep?

**Advantages:**
1. **Fast Performance** - Analyzes code 10x faster than traditional SAST tools
2. **Low False Positives** - Uses semantic analysis, not regex
3. **Multi-Language Support** - Python, JavaScript, Java, Go, Ruby, PHP, C, etc.
4. **Community Rules** - 2000+ pre-built security rules
5. **Easy Integration** - Simple CLI, JSON output
6. **Free Tier** - Unlimited scans on open-source projects

**Comparison with Alternatives:**

| Feature | Semgrep | SonarQube | Checkmarx | Bandit |
|---------|---------|-----------|-----------|--------|
| Speed | Fast | Medium | Slow | Fast |
| Languages | 30+ | 25+ | 30+ | Python only |
| False Positives | Low | Medium | High | Low |
| Cost | Free | Paid | Paid | Free |
| JSON Output | Yes | Yes | Yes | Yes |
| Ease of Use | Easy | Medium | Complex | Easy |

#### 6.1.2 Integration

**Command:**
```bash
semgrep --config=auto --json /path/to/repo
```

**Output Format:**
```json
{
  "results": [
    {
      "check_id": "python.django.security.injection.sql-injection",
      "path": "app/views.py",
      "start": {
        "line": 45,
        "col": 12
      },
      "end": {
        "line": 45,
        "col": 50
      },
      "extra": {
        "message": "User input in SQL query without parameterization",
        "severity": "HIGH",
        "metadata": {
          "cwe": "CWE-89",
          "owasp": "A03:2021",
          "confidence": "HIGH"
        },
        "fix": "Use parameterized queries"
      }
    }
  ]
}
```

#### 6.1.3 Detection Capabilities

**Vulnerability Types Detected:**
- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Command Injection (CWE-77)
- Path Traversal (CWE-22)
- Hardcoded Secrets (CWE-798)
- Insecure Deserialization (CWE-502)
- XML External Entity (CWE-611)
- Server-Side Request Forgery (CWE-918)
- Weak Cryptography (CWE-327)
- Session Fixation (CWE-384)

**Language-Specific Rules:**
- **Python**: Django, Flask, FastAPI security issues
- **JavaScript**: React, Node.js, Express vulnerabilities
- **Java**: Spring Boot, Struts security flaws
- **Go**: Standard library misuse, concurrency issues

### 6.2 SCA: Trivy

**Purpose:** Software Composition Analysis for dependency vulnerabilities

**Tool:** Trivy v0.48+
**Website:** https://trivy.dev/
**License:** Apache 2.0 (Open Source)

#### 6.2.1 Why Trivy?

**Advantages:**
1. **Universal Scanner** - Works with npm, pip, Maven, Go modules, Ruby gems, etc.
2. **Comprehensive Database** - CVE, GitHub Security Advisories, OS packages
3. **Container Scanning** - Docker images, Kubernetes manifests
4. **Infrastructure as Code** - Terraform, CloudFormation, Dockerfile
5. **Fast Updates** - Daily vulnerability database updates
6. **Offline Mode** - Can work without internet
7. **Free & Open Source** - No licensing costs

**Comparison with Alternatives:**

| Feature | Trivy | Snyk | npm audit | Safety |
|---------|-------|------|-----------|--------|
| Languages | All | All | JavaScript | Python |
| Container Scan | Yes | Yes | No | No |
| IaC Scan | Yes | Yes | No | No |
| Speed | Fast | Medium | Fast | Fast |
| Cost | Free | Paid | Free | Free |
| Offline Mode | Yes | No | No | No |

#### 6.2.2 Integration

**Command:**
```bash
trivy fs --format json --severity CRITICAL,HIGH,MEDIUM,LOW /path/to/repo
```

**Output Format:**
```json
{
  "Results": [
    {
      "Target": "package.json",
      "Class": "lang-pkgs",
      "Type": "npm",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2024-12345",
          "PkgName": "express",
          "InstalledVersion": "4.17.1",
          "FixedVersion": "4.18.2",
          "Severity": "HIGH",
          "Title": "Express.js Path Traversal vulnerability",
          "Description": "Versions of Express before 4.18.2 are vulnerable to path traversal...",
          "References": [
            "https://nvd.nist.gov/vuln/detail/CVE-2024-12345"
          ],
          "CVSS": {
            "nvd": {
              "V3Score": 7.5
            }
          }
        }
      ]
    }
  ]
}
```

#### 6.2.3 Detection Capabilities

**Vulnerability Sources:**
- **CVE Database** - National Vulnerability Database
- **GitHub Security Advisories** - Repository-specific vulnerabilities
- **npm Security Advisories** - JavaScript ecosystem
- **PyPI Safety DB** - Python package vulnerabilities
- **RubySec** - Ruby gem vulnerabilities
- **Rust Security Advisory** - Cargo vulnerabilities
- **Go Vulnerability Database** - Go module issues

**Package Managers Supported:**
- npm / yarn / pnpm (JavaScript)
- pip / Pipenv / Poetry (Python)
- Maven / Gradle (Java)
- Go modules (Go)
- Cargo (Rust)
- Bundler (Ruby)
- Composer (PHP)
- NuGet (.NET)

### 6.3 DAST: OWASP ZAP

**Purpose:** Dynamic Application Security Testing for runtime vulnerabilities

**Tool:** OWASP ZAP v2.14+
**Website:** https://www.zaproxy.org/
**License:** Apache 2.0 (Open Source)

#### 6.3.1 Why OWASP ZAP?

**Advantages:**
1. **Industry Standard** - OWASP flagship project
2. **Active Scanning** - Automatically tests for vulnerabilities
3. **Passive Scanning** - Monitors traffic without attacking
4. **API Testing** - REST, SOAP, GraphQL support
5. **Authentication** - Form-based, OAuth, API key support
6. **Extensible** - 100+ add-ons available
7. **Free & Open Source** - Enterprise-grade at no cost

**Comparison with Alternatives:**

| Feature | OWASP ZAP | Burp Suite | Acunetix | Nuclei |
|---------|-----------|------------|----------|--------|
| Active Scan | Yes | Yes (Pro) | Yes | Limited |
| Passive Scan | Yes | Yes | Yes | No |
| Authentication | Yes | Yes | Yes | Limited |
| API Testing | Yes | Yes | Yes | Yes |
| Cost | Free | $449/year | $4,500/year | Free |
| GUI | Yes | Yes | Yes | CLI only |
| CI/CD | Yes | Limited | Yes | Yes |

#### 6.3.2 Integration

**Command:**
```bash
zap-cli quick-scan --self-contained --spider -r https://target-app.com
```

**Output Format (XML):**
```xml
<?xml version="1.0"?>
<OWASPZAPReport>
  <site name="https://target-app.com">
    <alerts>
      <alertitem>
        <pluginid>40012</pluginid>
        <alert>Cross Site Scripting (Reflected)</alert>
        <riskcode>3</riskcode>
        <confidence>2</confidence>
        <riskdesc>High (Medium)</riskdesc>
        <desc>Cross-site Scripting (XSS) is an attack technique that involves echoing attacker-supplied code into a user's browser instance...</desc>
        <solution>Phase: Architecture and Design. Use a vetted library or framework that does not allow this weakness to occur...</solution>
        <reference>
          <uri>https://cwe.mitre.org/data/definitions/79.html</uri>
        </reference>
        <cweid>79</cweid>
        <wascid>8</wascid>
        <instances>
          <instance>
            <uri>https://target-app.com/search?q=&lt;script&gt;alert(1)&lt;/script&gt;</uri>
            <method>GET</method>
            <param>q</param>
            <attack>&lt;script&gt;alert(1)&lt;/script&gt;</attack>
            <evidence>&lt;script&gt;alert(1)&lt;/script&gt;</evidence>
          </instance>
        </instances>
      </alertitem>
    </alerts>
  </site>
</OWASPZAPReport>
```

#### 6.3.3 Detection Capabilities

**Vulnerability Types Detected:**
- **Injection Attacks** - SQL, Command, LDAP injection
- **Cross-Site Scripting (XSS)** - Reflected, Stored, DOM-based
- **Broken Authentication** - Weak passwords, session management
- **Sensitive Data Exposure** - Unencrypted data transmission
- **XML External Entities (XXE)** - XML parser vulnerabilities
- **Broken Access Control** - Unauthorized access
- **Security Misconfiguration** - Default credentials, verbose errors
- **Cross-Site Request Forgery (CSRF)** - State-changing requests
- **Insecure Deserialization** - Object injection
- **Using Components with Known Vulnerabilities**

**Scanning Modes:**
1. **Spider/Crawler** - Discovers all endpoints
2. **Passive Scanner** - Non-intrusive monitoring
3. **Active Scanner** - Attempts exploitation
4. **Ajax Spider** - JavaScript-heavy applications
5. **API Scanner** - OpenAPI/Swagger definitions

### 6.4 Scanner Comparison Matrix

| Aspect | Semgrep (SAST) | Trivy (SCA) | OWASP ZAP (DAST) |
|--------|----------------|-------------|------------------|
| **Analysis Type** | Static (code) | Static (dependencies) | Dynamic (runtime) |
| **Speed** | Fast (< 1 min) | Fast (< 30 sec) | Slow (5-15 min) |
| **False Positives** | Low | Very Low | Medium |
| **Coverage** | Code logic | Known CVEs | Runtime behavior |
| **Requires Running App** | No | No | Yes |
| **Language Specific** | Yes | Yes | No |
| **Network Access** | No | Optional | Required |
| **CPU Usage** | Medium | Low | High |
| **Memory Usage** | Medium | Low | High |

---

(Continuing in next response due to length limits...)

