# SecurAI Project - Complete Structure Documentation

## Table of Contents
1. [Root Level Files](#root-level-files)
2. [Backend Structure](#backend-structure)
3. [Frontend Structure](#frontend-structure)
4. [Data & Configuration](#data--configuration)
5. [Documentation](#documentation)
6. [Test & Sample Projects](#test--sample-projects)

---

## Root Level Files

### `.env` & `.env.example`
- **Purpose**: Environment variables configuration
- **Key Variables**:
  - `GROQ_API_KEY`: API key for Groq LLM access (LLaMA models)
  - `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`: GitHub OAuth credentials
  - `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`: Alternative LLM providers
- **Security**: `.env` excluded from git, only `.env.example` committed

### `config.yaml`
- **Purpose**: Central configuration for scanners, models, and RAG settings
- **Contents**:
  - Scanner tool paths (Semgrep, Trivy, OWASP ZAP, Nuclei)
  - LLM model configurations per vulnerability type
  - Vector database settings
  - Compliance framework paths

### `requirements.txt`
- **Purpose**: Python dependencies for backend
- **Key Libraries**:
  - `fastapi`, `uvicorn`: REST API framework
  - `chromadb`: Vector database for RAG
  - `groq`: LLM API client
  - `beautifulsoup4`, `lxml`: HTML parsing
  - `pydantic`: Data validation
  - `python-multipart`: File upload handling

### Batch Scripts (`start_backend.bat`, `start_frontend.bat`)
- **Purpose**: Quick startup scripts for Windows development
- **Usage**: Double-click to start backend (port 8000) or frontend (port 5173)

---

## Backend Structure

### `backend/api/`
**Purpose**: FastAPI REST API endpoints and authentication

#### `main.py` (Main API Server)
- **Team Member**: ELGARCH (Orchestrator & API)
- **Key Endpoints**:
  - `POST /upload`: Upload SAST/SCA/DAST reports → trigger policy generation
  - `POST /scan-github`: GitHub repo scanning via OAuth
  - `POST /run-compliance-test`: Validate policies against reference baseline
  - `GET /health`: Health check endpoint
  - WebSocket `/ws`: Real-time progress updates
- **Key Classes**:
  - `ScanRequest`: Pydantic model for scan parameters
  - WebSocket manager for client connections
- **Integration**: Calls `PolicyGeneratorOrchestrator` from [backend/orchestrator/policy_generator.py](backend/orchestrator/policy_generator.py)

#### `github_oauth.py` (GitHub OAuth Handler)
- **Purpose**: GitHub authentication for repo scanning
- **Flow**:
  1. `/auth/github` - Redirect to GitHub OAuth
  2. `/auth/callback` - Handle OAuth callback with code
  3. Exchange code for access token
  4. Fetch user repositories
- **Integration**: Used by [backend/scanners/github_scanner.py](backend/scanners/github_scanner.py)

---

### `backend/orchestrator/`
**Purpose**: Central coordination of entire pipeline

#### `policy_generator.py` (Core Orchestrator)
- **Team Member**: ELGARCH
- **Main Class**: `PolicyGeneratorOrchestrator`
- **Initialization**:
  ```python
  def __init__(self, use_rag=True, llm_models=None, output_dir="./outputs"):
      self.sast_parser = SASTParser()       # TOUZANI's parser
      self.sca_parser = SCAParser()         # IBNOU-KADY's parser
      self.dast_parser = DASTParser()       # BAZZAOUI's parser
      self.retriever = ComplianceRetriever() # RAG system
      self.llm_clients = {
          'sast': GroqClient(model="llama-3.3-70b-versatile"),
          'sca': GroqClient(model="llama-3.3-70b-versatile"),
          'dast': GroqClient(model="llama-3.1-8b-instant")
      }
  ```
- **Three-Phase Pipeline**:
  1. **`parse_reports()`**: Delegates to SAST/SCA/DAST parsers
  2. **`generate_policies()`**: For each vulnerability:
     - Retrieve relevant compliance controls via RAG
     - Select appropriate LLM (3.3 70B for SAST/SCA, 3.1 8B for DAST)
     - Generate remediation policy with NIST CSF/ISO 27001 mapping
  3. **`save_results()`**: Export to JSON, TXT, HTML, PDF with matplotlib charts
- **WebSocket Integration**: Sends progress updates to frontend in real-time

---

### `backend/parsers/`
**Purpose**: Parse security scanner outputs into normalized data models

#### `sast_parser.py` (SAST Parser)
- **Team Member**: TOUZANI
- **Input**: Semgrep JSON report
- **Data Model**: `SASTVulnerability`
  - `check_id`: Rule ID (e.g., "python.django.security.sql-injection")
  - `severity`: "ERROR", "WARNING", "INFO"
  - `file_path`: Vulnerable file location
  - `line_number`: Exact line with issue
  - `code_snippet`: Vulnerable code excerpt
  - `message`: Detailed explanation
- **Key Method**: `parse(report_path)` → List of SASTVulnerability objects

#### `sca_parser.py` (SCA Parser)
- **Team Member**: IBNOU-KADY
- **Input**: Trivy JSON report (universal SCA scanner)
- **Data Model**: `SCAVulnerability`
  - `package_name`: Vulnerable dependency (e.g., "lodash")
  - `installed_version`: Current version (e.g., "4.17.15")
  - `fixed_version`: Patched version (e.g., "4.17.21")
  - `severity`: "CRITICAL", "HIGH", "MEDIUM", "LOW"
  - `cve_id`: CVE identifier (e.g., "CVE-2021-23337")
  - `description`: Vulnerability details
- **Key Method**: `parse(report_path)` → List of SCAVulnerability objects

#### `dast_parser.py` (DAST Parser)
- **Team Member**: BAZZAOUI
- **Input**: OWASP ZAP XML + Nuclei JSON reports
- **Data Model**: `DASTVulnerability`
  - `url`: Target URL
  - `endpoint`: Vulnerable endpoint (e.g., "/login")
  - `method`: HTTP method (GET, POST, etc.)
  - `issue_type`: Vulnerability class (e.g., "SQL Injection", "XSS")
  - `risk_level`: "High", "Medium", "Low", "Informational"
  - `description`: Detailed finding
  - `solution`: Recommended fix
- **Key Methods**:
  - `parse_zap_xml()`: Parse OWASP ZAP reports
  - `parse_nuclei_json()`: Parse Nuclei scan results
  - `parse()`: Unified parser combining both sources

---

### `backend/scanners/`
**Purpose**: Execute security scans and manage scanning tools

#### `github_scanner.py` (GitHub Repository Scanner)
- **Team Member**: BAZZAOUI (integration), ALL (scanner orchestration)
- **Purpose**: Clone GitHub repo → run SAST/SCA/DAST
- **Key Methods**:
  - `clone_repository(repo_url, access_token)`: Clone via HTTPS with OAuth
  - `run_sast_scan(repo_path)`: Execute Semgrep
  - `run_sca_scan(repo_path)`: Execute Trivy
  - `run_dast_scan(repo_path)`: Trigger SmartDASTScanner
  - `cleanup()`: Remove cloned repositories
- **Integration**: Called from [backend/api/main.py](backend/api/main.py) `/scan-github` endpoint

#### `smart_dast_scanner.py` (Intelligent DAST Scanner)
- **Team Member**: BAZZAOUI
- **Purpose**: 4-tier DAST scanning strategy with graceful fallback
- **Tier 1**: User-provided URL
  - If user supplies working URL, scan directly
- **Tier 2**: Auto-detect deployment
  - Check for GitHub Pages (`username.github.io/repo`)
  - Check for Vercel deployment (`repo.vercel.app`)
  - Check for Netlify deployment (`repo.netlify.app`)
- **Tier 3**: Docker-based local deployment
  - Build Docker container from Dockerfile
  - Run application on localhost
  - Scan local instance
- **Tier 4**: Sample data fallback
  - If all else fails, use [data/sample_reports/dast_sample.xml](data/sample_reports/dast_sample.xml)
  - Ensures pipeline never blocks on DAST failure
- **Key Methods**:
  - `detect_frontend_deployment()`: Auto-detect hosting
  - `deploy_with_docker()`: Containerized deployment
  - `run_scan()`: Execute ZAP/Nuclei scanners
  - `get_sample_report()`: Fallback mechanism

#### `zap_scanner.py` (OWASP ZAP Integration)
- **Purpose**: Automated web application security scanner
- **Key Methods**:
  - `start_zap()`: Launch OWASP ZAP daemon
  - `passive_scan(url)`: Spider + passive analysis
  - `active_scan(url)`: Deep vulnerability detection
  - `export_report()`: Generate XML report
- **Output**: ZAP XML format parsed by [backend/parsers/dast_parser.py](backend/parsers/dast_parser.py)

#### `nuclei_scanner.py` (Nuclei Integration)
- **Purpose**: Fast template-based vulnerability scanner
- **Key Features**:
  - 5000+ vulnerability templates
  - DNS, HTTP, TCP, SSL/TLS checks
  - CVE detection
- **Key Methods**:
  - `run_scan(url, templates=[])`: Execute Nuclei CLI
  - `parse_output()`: Convert JSON to vulnerability objects
- **Output**: Nuclei JSON format parsed by [backend/parsers/dast_parser.py](backend/parsers/dast_parser.py)

---

### `backend/rag/`
**Purpose**: Retrieval-Augmented Generation system for compliance-aware policies

#### `vector_store.py` (ChromaDB Manager)
- **Purpose**: Manage vector database for semantic search
- **Key Methods**:
  - `create_collection(name)`: Initialize new collection
  - `add_documents(docs, embeddings, metadata)`: Store compliance documents
  - `query(query_embedding, n_results=5)`: Semantic similarity search
- **Collections**:
  - `nist_csf`: NIST Cybersecurity Framework controls
  - `iso27001`: ISO 27001 Annex A controls

#### `document_loader.py` (Compliance Document Loader)
- **Purpose**: Load and chunk compliance frameworks
- **Input Files**:
  - [data/compliance_docs/nist_csf_summary.txt](data/compliance_docs/nist_csf_summary.txt): 108 NIST CSF controls
  - [data/compliance_docs/iso27001_annexa.txt](data/compliance_docs/iso27001_annexa.txt): 114 ISO 27001 controls
- **Key Methods**:
  - `load_text_file(path)`: Read compliance documents
  - `chunk_documents(text, chunk_size=500)`: Split into semantic chunks
  - `extract_metadata()`: Parse control IDs and categories

#### `retriever.py` (Compliance Retriever)
- **Purpose**: Find relevant compliance controls for vulnerabilities
- **Main Class**: `ComplianceRetriever`
- **Key Methods**:
  - `retrieve(vulnerability_description, top_k=3)`:
    1. Generate embedding for vulnerability
    2. Query ChromaDB for similar compliance controls
    3. Return top-k NIST CSF + ISO 27001 mappings
  - `format_for_prompt()`: Convert retrieved controls to LLM context
- **Integration**: Called by orchestrator for each vulnerability

#### `init_vectordb.py` (Database Initialization)
- **Purpose**: One-time setup script to populate ChromaDB
- **Usage**: Run once to embed compliance documents
- **Process**:
  1. Load NIST CSF and ISO 27001 documents
  2. Chunk into 500-token segments
  3. Generate embeddings using sentence-transformers
  4. Store in ChromaDB with metadata
- **Output**: `./vector_db/` directory with ChromaDB data

---

### `backend/llm_integrations/`
**Purpose**: LLM provider clients with unified interface

#### `llm_factory.py` (Factory Pattern)
- **Purpose**: Create LLM clients dynamically
- **Key Method**:
  ```python
  def create_llm(provider="groq", model="llama-3.3-70b-versatile"):
      if provider == "groq":
          return GroqClient(model)
      elif provider == "openai":
          return OpenAIClient(model)
      # ... other providers
  ```
- **Supported Providers**: Groq, OpenAI, DeepSeek, HuggingFace, OpenRouter

#### `groq_client.py` (Primary LLM Client)
- **Purpose**: Groq API integration for LLaMA models
- **Models Used**:
  - `llama-3.3-70b-versatile`: SAST/SCA policies (complex vulnerabilities)
  - `llama-3.1-8b-instant`: DAST policies (faster, web-focused)
- **Key Methods**:
  - `generate(prompt, context="")`: Send prompt to Groq API
  - `stream_generate()`: Streaming response support
- **Configuration**:
  - Temperature: 0.7
  - Max tokens: 2048
  - Top-p: 0.9

#### `openai_client.py` (OpenAI Fallback)
- **Purpose**: OpenAI GPT models as alternative
- **Models**: GPT-4, GPT-3.5-turbo
- **Use Case**: Comparison testing, fallback if Groq unavailable

#### `deepseek_client.py` (DeepSeek Integration)
- **Purpose**: DeepSeek Coder model for code-focused policies
- **Use Case**: Experimental alternative for SAST policies

#### `huggingface_client.py` (HuggingFace Hub)
- **Purpose**: Open-source model integration
- **Use Case**: Local deployment, offline scenarios

#### `openrouter_client.py` (OpenRouter Gateway)
- **Purpose**: Unified access to multiple LLM providers
- **Use Case**: A/B testing different models

---

### `backend/prompts/`
**Purpose**: LLM prompt templates for policy generation

#### `policy_templates.py`
- **Purpose**: Structured prompts for consistent policy generation
- **Templates**:
  - `SAST_POLICY_PROMPT`: Code vulnerability remediation template
  - `SCA_POLICY_PROMPT`: Dependency update template
  - `DAST_POLICY_PROMPT`: Web security hardening template
- **Structure**: Each template includes:
  - Vulnerability context placeholder
  - Compliance controls placeholder (from RAG)
  - Output format specification (JSON)
  - Required fields: summary, remediation_steps, nist_csf_mapping, iso27001_mapping, priority

---

### `backend/compliance/`
**Purpose**: Compliance validation and coverage analysis

#### `coverage_analyzer.py` (Coverage Metrics)
- **Purpose**: Analyze which compliance controls are addressed
- **Key Methods**:
  - `calculate_coverage(policies)`: Count unique NIST CSF + ISO 27001 controls
  - `generate_coverage_report()`: Export coverage percentages
  - `identify_gaps()`: List unaddressed controls
- **Metrics**:
  - NIST CSF coverage: X/108 controls
  - ISO 27001 coverage: Y/114 controls
- **Integration**: Results included in HTML/PDF reports

#### `reference_comparator.py` (Compliance Test)
- **Purpose**: Validate generated policies against manual baseline
- **Key Methods**:
  - `load_reference_policy(path)`: Load gold standard policy
  - `compare(generated_policy, reference_policy)`: Calculate similarity
  - `calculate_bleu_score()`: BLEU metric for text similarity
  - `calculate_rouge_scores()`: ROUGE-1, ROUGE-2, ROUGE-L metrics
- **Use Case**: Quality assurance, academic validation
- **Reference Files**: [data/reference_policies/sql_injection_reference.txt](data/reference_policies/sql_injection_reference.txt)

---

### `backend/evaluation/`
**Purpose**: Policy quality metrics

#### `metrics.py`
- **Purpose**: Calculate policy generation quality metrics
- **Metrics Implemented**:
  - **BLEU Score**: N-gram overlap with reference policies
  - **ROUGE Scores**: Recall-oriented evaluation
  - **Coverage Score**: % of compliance controls addressed
  - **Completeness**: All required fields present
- **Integration**: Called by [backend/compliance/reference_comparator.py](backend/compliance/reference_comparator.py)

---

### `backend/verification/`
**Purpose**: Policy validation before delivery

#### `compliance_checker.py`
- **Purpose**: Verify policies meet compliance requirements
- **Checks**:
  - NIST CSF mapping present and valid
  - ISO 27001 mapping present and valid
  - Remediation steps actionable
  - Priority level assigned
  - No hallucinated control IDs
- **Key Method**: `validate_policy(policy)` → True/False + error messages

---

### `backend/utils/`
**Purpose**: Shared utility functions

#### `utils.py`
- **Purpose**: Common helper functions
- **Functions**:
  - `generate_timestamp()`: Filename-safe timestamps
  - `ensure_directory(path)`: Create output directories
  - `sanitize_filename()`: Clean user input for file paths
  - `format_vulnerability()`: Normalize vulnerability objects

#### `pdf_enhancer.py` (Enhanced PDF Reports)
- **Purpose**: Generate professional PDF reports with charts
- **Key Methods**:
  - `create_pdf_with_charts(policies, output_path)`: Generate PDF
  - `add_matplotlib_chart()`: Embed severity distribution charts
  - `add_compliance_coverage_chart()`: Pie chart for coverage
  - `add_priority_breakdown()`: Bar chart for priorities
- **Libraries**: ReportLab, matplotlib

#### `pdf_parser.py` (PDF Parsing)
- **Purpose**: Extract text from uploaded PDF reports
- **Use Case**: If users upload reports in PDF format
- **Key Method**: `extract_text(pdf_path)` → Raw text

---

## Frontend Structure

### `frontend/src/`
**Purpose**: React-based single-page application

#### `frontend/src/App.jsx` (Main Application)
- **Purpose**: Root component with routing
- **Routes**:
  - `/`: Home page with upload interface
  - `/github`: GitHub OAuth flow
  - `/results`: Policy generation results
  - `/compliance-test`: Compliance validation page
  - `/workflow`: Visual workflow diagram

#### `frontend/src/components/`
**Purpose**: Reusable React components

##### `UploadForm.jsx`
- **Purpose**: File upload interface for SAST/SCA/DAST reports
- **Features**:
  - Drag-and-drop support
  - File type validation (JSON, XML)
  - Upload progress indicator
  - WebSocket connection for real-time updates
- **API Call**: `POST /upload`

##### `GitHubRepoSelector.jsx`
- **Purpose**: GitHub repository selection UI
- **Features**:
  - OAuth login button
  - Repository list with search
  - Branch selection dropdown
  - Scan trigger button
- **API Calls**:
  - `GET /auth/github` (OAuth)
  - `POST /scan-github`

##### `PolicyResultsDisplay.jsx`
- **Purpose**: Display generated policies with compliance mappings
- **Features**:
  - Vulnerability severity filtering
  - Compliance framework toggle (NIST CSF / ISO 27001)
  - Export buttons (JSON, PDF, HTML)
  - Remediation step checklist
- **Data Source**: WebSocket messages from backend

##### `ComplianceTestRunner.jsx`
- **Purpose**: Run compliance validation tests
- **Features**:
  - Upload reference policy
  - Upload generated policy
  - Display BLEU/ROUGE scores
  - Highlight differences
- **API Call**: `POST /run-compliance-test`

##### `workflow/WorkflowDiagram.jsx`
- **Purpose**: Interactive visual workflow
- **Features**:
  - Step-by-step pipeline visualization
  - Progress indicator per stage
  - Team member attribution per module
- **Libraries**: React Flow or Mermaid rendering

##### `Navbar.jsx`
- **Purpose**: Navigation bar with branding
- **Links**:
  - Home
  - GitHub Scan
  - Compliance Test
  - Documentation

##### `Footer.jsx`
- **Purpose**: Footer with team credits and university branding

---

### `frontend/src/utils/`
**Purpose**: Frontend utilities

#### `api.js` (API Client)
- **Purpose**: Centralized API calls with error handling
- **Functions**:
  - `uploadReports(files)`: Upload SAST/SCA/DAST reports
  - `scanGitHubRepo(repo_url, token)`: Trigger GitHub scan
  - `runComplianceTest(policy_data)`: Run validation
  - `connectWebSocket(onMessage)`: WebSocket connection
- **Base URL**: `http://localhost:8000`

#### `websocket.js` (WebSocket Manager)
- **Purpose**: Manage real-time communication
- **Events**:
  - `progress_update`: Pipeline stage updates
  - `parsing_complete`: Parsing done, N vulnerabilities found
  - `policy_generated`: New policy available
  - `generation_complete`: All policies done
  - `error`: Error occurred

---

### `frontend/public/`
**Purpose**: Static assets

#### `index.html`
- **Purpose**: HTML entry point
- **Customizations**:
  - Favicon
  - SEO meta tags
  - Google Fonts (Roboto, Inter)

#### `logo.svg`
- **Purpose**: SecurAI logo

#### `manifest.json`
- **Purpose**: PWA configuration

---

### `frontend/package.json`
- **Purpose**: Frontend dependencies
- **Key Libraries**:
  - `react`, `react-dom`: UI framework
  - `vite`: Build tool
  - `tailwindcss`: Utility-first CSS
  - `axios`: HTTP client
  - `react-router-dom`: Client-side routing
  - `lucide-react`: Icon library

---

## Data & Configuration

### `data/compliance_docs/`
**Purpose**: Compliance framework documents for RAG

#### `nist_csf_summary.txt`
- **Content**: 108 NIST Cybersecurity Framework controls
- **Structure**: 5 functions (Identify, Protect, Detect, Respond, Recover)
- **Format**: Control ID → Description
- **Example**:
  ```
  PR.AC-1: Identities and credentials are issued, managed, verified, revoked
  PR.DS-1: Data-at-rest is protected
  ```

#### `iso27001_annexa.txt`
- **Content**: 114 ISO 27001:2022 Annex A controls
- **Structure**: 4 themes (Organizational, People, Physical, Technological)
- **Format**: Control ID → Objective → Implementation guidance
- **Example**:
  ```
  A.8.3: Information security shall be addressed in project management
  ```

---

### `data/reference_policies/`
**Purpose**: Gold standard policies for compliance testing

#### `sql_injection_reference.txt`
- **Content**: Manually crafted SQL injection remediation policy
- **Use Case**: Baseline for BLEU/ROUGE comparison
- **Structure**:
  - Summary
  - Remediation steps (parameterized queries, input validation, WAF)
  - NIST CSF mapping (PR.DS-1, PR.DS-5)
  - ISO 27001 mapping (A.8.3, A.14.2)

---

### `data/sample_reports/`
**Purpose**: Sample scan outputs for testing

#### `sast_sample.json`
- **Content**: Semgrep sample output with SQL injection, XSS, CSRF vulnerabilities
- **Use Case**: Test SAST parser without running Semgrep

#### `sca_sample.json`
- **Content**: Trivy sample output with lodash, axios CVEs
- **Use Case**: Test SCA parser without running Trivy

#### `dast_sample.xml`
- **Content**: OWASP ZAP sample output with XSS, SQL injection, IDOR findings
- **Use Case**: Fallback for SmartDASTScanner Tier 4

---

### `vector_db/`
**Purpose**: ChromaDB persistent storage
- **Generated By**: [backend/rag/init_vectordb.py](backend/rag/init_vectordb.py)
- **Contents**: Embeddings of compliance documents
- **Size**: ~50MB (108 NIST + 114 ISO controls)

---

### `outputs/`
**Purpose**: Generated policy reports

#### Naming Convention
- `policy_generation_YYYYMMDD_HHMMSS.json`
- `security_policy_YYYYMMDD_HHMMSS.html`
- `security_policy_YYYYMMDD_HHMMSS.pdf`
- `security_policy_YYYYMMDD_HHMMSS.txt`

#### JSON Structure
```json
{
  "timestamp": "2025-11-07T14:30:00",
  "total_vulnerabilities": 47,
  "policies": [
    {
      "vulnerability": {
        "type": "sast",
        "severity": "high",
        "description": "SQL Injection in login.py:42"
      },
      "policy": {
        "summary": "...",
        "remediation_steps": ["...", "..."],
        "nist_csf_controls": ["PR.DS-1", "PR.DS-5"],
        "iso27001_controls": ["A.8.3", "A.14.2"],
        "priority": "critical"
      }
    }
  ],
  "compliance_coverage": {
    "nist_csf": "18/108 (16.7%)",
    "iso27001": "22/114 (19.3%)"
  }
}
```

---

## Documentation

### `docs/`
**Purpose**: Project documentation

#### `TEAM_TECHNICAL_REPORT.md`
- **Length**: 2825 lines
- **Content**: Complete implementation details with team contributions
- **Sections**:
  - System architecture
  - Module descriptions (SAST/SCA/DAST/Orchestrator/RAG)
  - LLM integration strategy
  - RAG implementation
  - API endpoints
  - Frontend features
  - Testing results

#### `COMPREHENSIVE_DIAGRAMS.md`
- **Content**: 40+ Mermaid diagrams
- **Categories**:
  - System architecture (global, 3-tier)
  - Component diagrams
  - Sequence diagrams (Upload Mode, GitHub Mode)
  - Class diagrams (with team attribution)
  - Activity diagrams (policy generation, RAG retrieval)
  - State diagrams (WebSocket, OAuth)
  - Deployment diagrams (local, Docker, AWS)
  - Data flow diagrams (Level 0-2)

#### `ADVANCED_FEATURES_REPORT.md`
- **Content**: Compliance test feature documentation
- **Features**:
  - BLEU/ROUGE metrics implementation
  - Enhanced PDF reports with charts
  - HTML reports with quality metrics

#### `COMPLETE_SETUP_GUIDE.md`
- **Content**: Installation and deployment guide
- **Sections**:
  - Prerequisites (Python 3.11, Node.js 18)
  - Backend setup (venv, dependencies, ChromaDB init)
  - Frontend setup (npm install, Vite config)
  - Scanner tool installation (Semgrep, Trivy, ZAP, Nuclei)
  - Environment variables configuration

#### `COMPLIANCE_FEATURES_COMPLETE.md`
- **Content**: Compliance validation implementation
- **Features**:
  - Coverage analyzer
  - Reference comparator
  - BLEU/ROUGE metrics

#### `GITHUB_OAUTH_DAST_SETUP.md`
- **Content**: GitHub OAuth + DAST integration guide
- **Sections**:
  - GitHub OAuth app registration
  - Callback URL configuration
  - Smart DAST scanner 4-tier strategy

#### `FRONTEND_IMPLEMENTATION_SUMMARY.md`
- **Content**: React frontend implementation details
- **Components**: UploadForm, GitHubRepoSelector, PolicyResultsDisplay

#### `QUICK_START_NEW_FEATURES.md`
- **Content**: Quick reference for new developers
- **Usage**: Fast onboarding guide

#### `TEST_INSTRUCTIONS.md`
- **Content**: Testing procedures
- **Sections**:
  - Unit tests
  - Integration tests
  - End-to-end testing with OWASP Juice Shop

---

## Test & Sample Projects

### `tests/juice-shop/`
**Purpose**: OWASP Juice Shop for realistic DAST testing
- **Description**: Intentionally vulnerable web application
- **Usage**: Full-stack test target for all scanners
- **Deployment**: Docker container on localhost:3000

### `test_scans/Vulnerable-Flask-App/`
**Purpose**: Python Flask vulnerable app for SAST/SCA testing
- **Vulnerabilities**: SQL injection, XSS, insecure deserialization
- **Usage**: Test SAST parser with real findings

### `test_real_scans/NodeGoat/`
**Purpose**: Node.js vulnerable app for SAST/SCA testing
- **Vulnerabilities**: NoSQL injection, CSRF, insecure dependencies
- **Usage**: Test SCA parser with npm audit

---

## GitHub Actions

### `.github/workflows/devsecops-pipeline.yml`
**Purpose**: CI/CD pipeline with security scanning
- **Trigger**: Push to main/test-actions branches
- **Jobs**:
  1. **SAST**: Run Semgrep on backend code
  2. **SCA**: Run Trivy on dependencies
  3. **DAST**: Deploy Juice Shop → run ZAP/Nuclei
  4. **Policy Generation**: Upload reports → generate policies
  5. **Compliance Check**: Validate policies
- **Artifacts**: Upload JSON/HTML/PDF reports

---

## Key File Relationships

### Policy Generation Flow
1. **Input**: User uploads reports OR triggers GitHub scan
2. **API Entry**: [backend/api/main.py](backend/api/main.py) receives request
3. **Orchestration**: [backend/orchestrator/policy_generator.py](backend/orchestrator/policy_generator.py) coordinates
4. **Parsing**: [backend/parsers/](backend/parsers/) normalize vulnerabilities
5. **RAG Retrieval**: [backend/rag/retriever.py](backend/rag/retriever.py) finds compliance controls
6. **LLM Call**: [backend/llm_integrations/groq_client.py](backend/llm_integrations/groq_client.py) generates policies
7. **Output**: [backend/orchestrator/policy_generator.py](backend/orchestrator/policy_generator.py) exports reports
8. **Display**: [frontend/src/components/PolicyResultsDisplay.jsx](frontend/src/components/PolicyResultsDisplay.jsx) shows results

### GitHub Scan Flow
1. **OAuth**: [frontend/src/components/GitHubRepoSelector.jsx](frontend/src/components/GitHubRepoSelector.jsx) → [backend/api/github_oauth.py](backend/api/github_oauth.py)
2. **Clone**: [backend/scanners/github_scanner.py](backend/scanners/github_scanner.py) clones repo
3. **SAST/SCA**: [backend/scanners/github_scanner.py](backend/scanners/github_scanner.py) runs Semgrep + Trivy
4. **DAST**: [backend/scanners/smart_dast_scanner.py](backend/scanners/smart_dast_scanner.py) 4-tier approach
5. **Continue**: Same as policy generation flow above

### Compliance Test Flow
1. **Upload**: [frontend/src/components/ComplianceTestRunner.jsx](frontend/src/components/ComplianceTestRunner.jsx) uploads reference + generated policies
2. **Comparison**: [backend/compliance/reference_comparator.py](backend/compliance/reference_comparator.py) calculates metrics
3. **Metrics**: [backend/evaluation/metrics.py](backend/evaluation/metrics.py) computes BLEU/ROUGE
4. **Results**: [frontend/src/components/ComplianceTestRunner.jsx](frontend/src/components/ComplianceTestRunner.jsx) displays scores

---

## Team Member Contributions

### TOUZANI (SAST Parser)
- [backend/parsers/sast_parser.py](backend/parsers/sast_parser.py)
- Semgrep integration
- Code vulnerability data model

### IBNOU-KADY (SCA Parser)
- [backend/parsers/sca_parser.py](backend/parsers/sca_parser.py)
- Trivy integration
- Dependency vulnerability data model

### BAZZAOUI (DAST Parser & Scanners)
- [backend/parsers/dast_parser.py](backend/parsers/dast_parser.py)
- [backend/scanners/smart_dast_scanner.py](backend/scanners/smart_dast_scanner.py)
- [backend/scanners/zap_scanner.py](backend/scanners/zap_scanner.py)
- [backend/scanners/nuclei_scanner.py](backend/scanners/nuclei_scanner.py)
- [backend/scanners/github_scanner.py](backend/scanners/github_scanner.py) (integration)

### ELGARCH (Orchestrator, RAG, API, Reports)
- [backend/orchestrator/policy_generator.py](backend/orchestrator/policy_generator.py)
- [backend/rag/](backend/rag/) (entire module)
- [backend/api/main.py](backend/api/main.py)
- [backend/utils/pdf_enhancer.py](backend/utils/pdf_enhancer.py)
- [backend/compliance/coverage_analyzer.py](backend/compliance/coverage_analyzer.py)
- [backend/compliance/reference_comparator.py](backend/compliance/reference_comparator.py)

---

## Summary Statistics

- **Total Backend Files**: 34 Python modules
- **Total Frontend Files**: 15+ React components
- **Lines of Code (Backend)**: ~8,500 lines
- **Lines of Code (Frontend)**: ~3,200 lines
- **Documentation**: 15+ comprehensive markdown files
- **Diagrams**: 40+ Mermaid diagrams
- **Test Projects**: 3 vulnerable applications
- **Compliance Controls**: 222 (108 NIST CSF + 114 ISO 27001)
- **LLM Models**: 2 primary (LLaMA 3.3 70B, LLaMA 3.1 8B)
- **Security Scanners**: 4 tools (Semgrep, Trivy, OWASP ZAP, Nuclei)

---

## Quick Navigation

**Want to understand a specific component?**
- **Policy Generation Logic**: [backend/orchestrator/policy_generator.py](backend/orchestrator/policy_generator.py)
- **RAG System**: [backend/rag/retriever.py](backend/rag/retriever.py)
- **SAST Parsing**: [backend/parsers/sast_parser.py](backend/parsers/sast_parser.py)
- **DAST Scanning**: [backend/scanners/smart_dast_scanner.py](backend/scanners/smart_dast_scanner.py)
- **API Endpoints**: [backend/api/main.py](backend/api/main.py)
- **Frontend Upload**: [frontend/src/components/UploadForm.jsx](frontend/src/components/UploadForm.jsx)
- **Compliance Testing**: [backend/compliance/reference_comparator.py](backend/compliance/reference_comparator.py)

---

**End of Project Structure Documentation**
