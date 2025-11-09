# SecurAI - Complete Technical Documentation (PART 1)
## AI-Powered Security Policy Generator with Compliance Mapping

---

# 1. PROJECT OVERVIEW

## 1.1 Executive Summary
**Project Name**: SecurAI
**Type**: Academic Final Year Project (3rd Year Engineering)
**Domain**: DevSecOps, AI/ML, Cybersecurity
**Team**: TOUZANI (SAST), IBNOU-KADY (SCA), BAZZAOUI (DAST), ELGARCH (Orchestrator)

**Problem Statement**: Organizations struggle to translate vulnerability scan results into actionable, compliance-aligned security policies. Manual policy writing is time-consuming (10+ minutes per vulnerability) and inconsistent.

**Solution**: Automated policy generation using Large Language Models with:
- Multi-framework compliance mapping (NIST CSF, ISO 27001, OWASP, PCI DSS)
- Adaptive content based on user expertise (beginner/intermediate/advanced)
- Real-time generation with WebSocket updates
- Policy lifecycle tracking from generation to verification

---

# 2. SYSTEM ARCHITECTURE

## 2.1 Three-Tier Architecture

```
┌──────────────────────────────────────────────┐
│         PRESENTATION TIER                     │
│  React.js + Tailwind CSS + WebSocket         │
│  - Upload Mode  - GitHub Mode  - Tracking    │
└──────────────────────────────────────────────┘
                   ↕ HTTP/WS
┌──────────────────────────────────────────────┐
│         APPLICATION TIER (FastAPI)            │
│  Orchestrator → RAG → LLM → Evaluators       │
│  Parsers + Scanners + Adaptive Prompts       │
└──────────────────────────────────────────────┘
                   ↕ Vectors
┌──────────────────────────────────────────────┐
│         DATA TIER                             │
│  ChromaDB + JSON Storage + File System       │
└──────────────────────────────────────────────┘
```

## 2.2 Technology Stack

### Frontend
- React 18.3.1 with Vite (fast dev server)
- Tailwind CSS 3.4.1 (utility-first styling)
- Axios 1.7.7 (HTTP client)
- Lucide React (icons)
- WebSocket (real-time updates)

### Backend
- FastAPI 0.115.4 (async Python framework)
- Uvicorn (ASGI server)
- Python 3.11+

### AI/ML
- Groq Cloud API (LLM provider - Free tier)
- LLaMA 3.3 70B (SAST/SCA analysis)
- LLaMA 3.1 8B (DAST analysis - faster)
- ChromaDB 0.5.20 (vector database)
- Sentence Transformers (embeddings)

### Security Scanners
- Semgrep (SAST)
- Trivy (SCA - universal vulnerability scanner)
- OWASP ZAP (DAST)
- Nuclei (DAST - template-based)

### Evaluation
- NLTK (BLEU, ROUGE metrics)
- ReportLab (PDF generation)
- PyPDF2 (PDF parsing)

---

# 3. CORE COMPONENTS

## 3.1 Policy Generator Orchestrator
**File**: `backend/orchestrator/policy_generator.py`
**Owner**: ELGARCH
**Lines**: ~350

**Purpose**: Coordinates entire pipeline from parsing to generation

**Key Workflow**:
```python
1. Initialize RAG + LLM clients
2. Parse reports (SAST/SCA/DAST)
3. For each vulnerability:
   a. Retrieve compliance context from RAG
   b. Select prompt based on user expertise
   c. Generate policy via LLM
   d. Add to tracking system
4. Save results (JSON + HTML)
```

**LLM Selection Strategy**:
```python
self.llm_clients = {
    'sast': GroqClient(model="llama-3.3-70b-versatile"),  # Complex code
    'sca': GroqClient(model="llama-3.3-70b-versatile"),   # Dependency context
    'dast': GroqClient(model="llama-3.1-8b-instant")      # Runtime issues
}
```

**User Profile Integration** (NEW):
```python
def __init__(self, user_profile: UserProfile = None):
    self.user_profile = user_profile or UserProfile.default()

def generate_policy_for_vulnerability(self, vulnerability, vuln_type):
    if ADAPTIVE_PROMPTS_AVAILABLE:
        prompt = AdaptivePolicyPrompts.select_prompt(
            vulnerability_type=vuln_type,
            expertise_level=self.user_profile.expertise_level,
            vulnerability=vulnerability,
            compliance_context=compliance_context,
            user_profile=self.user_profile
        )
```

## 3.2 RAG System (Retrieval-Augmented Generation)
**File**: `backend/rag/retriever.py`

**Purpose**: Enhance LLM with authoritative compliance knowledge

**Process Flow**:
```
1. Index compliance documents into ChromaDB
2. User query: "SQL Injection vulnerability"
3. Semantic search → Top 5 relevant chunks
4. Inject context into LLM prompt
5. LLM generates policy with accurate controls
```

**Indexed Documents**:
- NIST Cybersecurity Framework v2.0 (108 controls)
- ISO/IEC 27001:2022 Annex A (114 controls)
- OWASP Top 10
- PCI DSS v4.0

**Retrieval Method**:
```python
def retrieve_for_vulnerability(self, vulnerability, top_k=5):
    query = f"{title} {description} {severity}"
    results = self.collection.query(query_texts=[query], n_results=top_k)

    # Extract control IDs
    nist_controls = extract_nist_controls(results)
    iso_controls = extract_iso_controls(results)

    return {
        'formatted_context': "\n".join(results),
        'nist_csf_controls': nist_controls,
        'iso27001_controls': iso_controls
    }
```

## 3.3 Adaptive Prompt System (INNOVATION)
**File**: `backend/prompts/adaptive_templates.py` (1000+ lines)

**Key Innovation**: Same vulnerability → Different policies per expertise

**9 Prompt Templates**:
```
Beginner × SAST    | Intermediate × SAST    | Advanced × SAST
Beginner × SCA     | Intermediate × SCA     | Advanced × SCA
Beginner × DAST    | Intermediate × DAST    | Advanced × DAST
```

**Selection Logic**:
```python
@staticmethod
def select_prompt(vulnerability_type, expertise_level, vulnerability,
                 compliance_context, user_profile):
    prompt_map = {
        ('sast', ExpertiseLevel.BEGINNER): get_beginner_sast_prompt,
        ('sast', ExpertiseLevel.ADVANCED): get_advanced_sast_prompt,
        # ... 7 more
    }
    return prompt_map[(vulnerability_type, expertise_level)](...)
```

**Content Comparison**:

| Feature | Beginner | Advanced |
|---------|----------|----------|
| Tone | Educational | Technical |
| Length | 800 words | 5000 words |
| Explanations | "What is XSS?" | No basics |
| Code | Heavily commented | Minimal |
| Compliance | 2-3 controls | 8-10 controls |
| Detection | Manual steps | SIEM rules (Splunk) |
| Extra | OWASP tutorials | CVSS calculation |

**Beginner Example**:
```markdown
## 📚 Understanding SQL Injection
SQL injection happens when...

## 💻 How to Fix It
### Before (Vulnerable):
# BAD: User input directly in query
query = f"SELECT * FROM users WHERE id={user_id}"

### After (Secure):
# GOOD: Use parameterized queries
query = "SELECT * FROM users WHERE id=?"
cursor.execute(query, (user_id,))

## 🎓 Learn More
- OWASP SQL Injection Guide
- SQLi Tutorial Video
```

**Advanced Example**:
```markdown
## Security Policy: SQL Injection (CWE-89)

### CVSS v3.1 Analysis
Vector: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Base Score: 9.8 (CRITICAL)

### SIEM Detection Rule (Splunk)
index=web_logs sourcetype=access_combined
| rex field=_raw "(?<sql_keywords>UNION|SELECT|INSERT)"
| where isnotnull(sql_keywords)
| stats count by src_ip, uri

### ModSecurity WAF Rule
SecRule ARGS "@rx (\bunion\b.*\bselect\b|\bselect\b.*\bunion\b)"
  "id:942100,phase:2,deny,status:403"

### ISO 27001 Controls
A.8.16 - Secure coding practices
A.12.6.1 - Technical vulnerability management
```

## 3.4 Policy Tracking System (NEW)
**Files**:
- `backend/models/policy_status.py`
- `backend/database/policy_tracker.py`

**Purpose**: Monitor policy implementation lifecycle

**6 Status States**:
```python
class PolicyStatus(Enum):
    NOT_STARTED = "not_started"   # Generated, not assigned
    IN_PROGRESS = "in_progress"   # Developer working
    UNDER_REVIEW = "under_review" # Code review
    FIXED = "fixed"               # Merged to main
    VERIFIED = "verified"         # Security team confirmed
    REOPENED = "reopened"         # Issue found
```

**Automatic Due Dates**:
```python
severity_days = {
    'critical': 2,   # 2 days
    'high': 7,       # 1 week
    'medium': 30,    # 1 month
    'low': 90        # 3 months
}
```

**Timeline Events** (Event Sourcing):
```python
class TimelineEvent:
    event_type: str      # created, assigned, status_changed
    timestamp: str
    user: str
    from_status: str
    to_status: str
```

**Storage**: JSON file (`outputs/policy_tracking.json`)
```json
{
  "policies": [{
    "policy_id": "POL-2025-001",
    "vulnerability_title": "SQL Injection in login.py",
    "severity": "critical",
    "status": "in_progress",
    "due_date": "2025-11-10T12:00:00",
    "timeline": [
      {"event_type": "created", "timestamp": "2025-11-08T10:00:00"},
      {"event_type": "assigned", "user": "John Doe"},
      {"event_type": "status_changed", "to_status": "in_progress"}
    ]
  }],
  "stats": {
    "total_policies": 12,
    "compliance_percentage": 25.0
  }
}
```

---

# 4. PARSERS (Multi-Scanner Support)

## 4.1 SAST Parser - Semgrep
**File**: `backend/parsers/sast_parser.py`
**Owner**: TOUZANI

**Input**: Semgrep JSON
```json
{
  "results": [{
    "check_id": "python.lang.security.sql-injection",
    "path": "app/database.py",
    "start": {"line": 42},
    "extra": {
      "message": "SQL injection vulnerability",
      "severity": "ERROR",
      "metadata": {"cwe": ["CWE-89"]}
    }
  }]
}
```

**Output**: Normalized vulnerabilities
```python
{
  'title': 'SQL Injection',
  'severity': 'HIGH',
  'file_path': 'app/database.py',
  'line_number': 42,
  'cwe': ['CWE-89']
}
```

## 4.2 SCA Parser - Trivy
**File**: `backend/parsers/sca_parser.py`
**Owner**: IBNOU-KADY

**Why Trivy over npm audit?**
- Universal (npm, pip, Maven, Go, Rust)
- Better CVE accuracy
- Active maintenance (Aqua Security)
- JSON output more structured

**Input**: Trivy JSON
```json
{
  "Results": [{
    "Vulnerabilities": [{
      "VulnerabilityID": "CVE-2024-1234",
      "PkgName": "lodash",
      "InstalledVersion": "4.17.19",
      "FixedVersion": "4.17.21",
      "Severity": "CRITICAL"
    }]
  }]
}
```

## 4.3 DAST Parser - OWASP ZAP
**File**: `backend/parsers/dast_parser.py`
**Owner**: BAZZAOUI

**Input**: ZAP XML
```xml
<OWASPZAPReport>
  <site>
    <alerts>
      <alertitem>
        <alert>Cross Site Scripting</alert>
        <riskcode>3</riskcode>
        <uri>http://target.com/search?q=</uri>
        <cweid>79</cweid>
      </alertitem>
    </alerts>
  </site>
</OWASPZAPReport>
```

**Risk Mapping**:
- 3 (High) → HIGH
- 2 (Medium) → MEDIUM
- 1 (Low) → LOW
- 0 (Info) → INFO

---

# 5. TWO OPERATING MODES

## 5.1 Upload Mode (File-Based)

**User Journey**:
```
1. User uploads SAST/SCA/DAST reports (JSON/XML)
2. Files sent via multipart/form-data to backend
3. Backend saves to temp directory
4. Orchestrator identifies file types
5. Calls appropriate parsers
6. For each vulnerability:
   - RAG retrieves compliance context
   - LLM generates policy
   - Policy tracked in JSON
7. Results returned + files saved
```

**API**: `POST /api/generate-policies`

**Parameters**:
```python
sast_file: UploadFile (optional)
sca_file: UploadFile (optional)
dast_file: UploadFile (optional)
max_per_type: int = 5
expertise_level: str = "intermediate"
user_role: str = "senior_developer"
user_name: str (optional)
```

**WebSocket Updates** (Real-Time):
```json
{"phase": "parsing", "status": "in_progress", "message": "Parsing SAST report..."}
{"phase": "rag", "status": "in_progress", "message": "Retrieving compliance context..."}
{"phase": "generation", "status": "in_progress", "message": "Generating policies..."}
{"phase": "complete", "status": "success", "data": {...}}
```

## 5.2 GitHub Mode (Repository Scanning)

**User Journey**:
```
1. User provides GitHub URL + branch
2. Backend clones repo to /tmp
3. Run scanners in parallel:
   - Semgrep → SAST report
   - Trivy → SCA report
   - (Optional) ZAP → DAST report
4. Parse reports
5. Generate policies (same as Upload Mode)
6. Cleanup temp directory
```

**API**: `POST /api/scan-github`

**Request**:
```json
{
  "repo_url": "https://github.com/user/repo",
  "branch": "main",
  "scan_types": {"sast": true, "sca": true, "dast": false},
  "token": "ghp_xxxxx"  // For private repos
}
```

**Scanner Commands**:
```bash
# SAST
semgrep scan --config=auto --json --output=sast.json /tmp/repo

# SCA
trivy fs --format=json --output=sca.json /tmp/repo

# DAST (if URL provided)
zap-baseline.py -t https://staging.com -J dast.json
```

**Security**:
- Isolated temp directories
- Auto cleanup after processing
- GitHub token validation
- Resource limits (timeout, size)

---

# 6. USER INTERFACE (React)

## 6.1 Three Main Views

### 1. Upload Mode
**Components**:
- File upload dropzones (3 types)
- User profile selector (NEW)
- Generate button

**User Profile UI** (NEW):
```jsx
<div className="profile-section">
  <select name="expertise">
    <option value="beginner">🎓 Beginner - Learning focused</option>
    <option value="intermediate">💼 Intermediate - Balanced</option>
    <option value="advanced">🔬 Advanced - Technical</option>
  </select>

  <select name="role">
    <option>Junior Developer</option>
    <option>Senior Developer</option>
    <option>Security Engineer</option>
    <option>DevOps Engineer</option>
    <option>Compliance Officer</option>
    <option>Manager/CISO</option>
  </select>

  <input name="user_name" placeholder="Your name (optional)"/>
</div>
```

### 2. GitHub Mode
**Components**:
- Repository URL input
- Branch selector
- Scan type checkboxes (SAST/SCA/DAST)
- GitHub OAuth integration

### 3. Policy Tracking Dashboard (NEW)
**Components**:
- Stats cards (Total, In Progress, Verified, Compliance %)
- Policy list with filters
- Status badges
- Timeline view

**Stats Display**:
```jsx
<div className="stats-grid">
  <StatCard title="Total" value={12} icon={Users}/>
  <StatCard title="In Progress" value={4} icon={Clock}/>
  <StatCard title="Verified" value={3} icon={CheckCircle}/>
  <StatCard title="Compliance" value="25.0%" icon={TrendingUp}/>
</div>
```

## 6.2 Real-Time Progress Display
**Component**: `WorkflowView.jsx`

**Phases Shown**:
```
Phase 1: Parsing ━━━━━━━━━━━━━━━━━━ 100% ✓
  ├─ SAST: 8 vulnerabilities found
  ├─ SCA: 12 dependencies scanned
  └─ DAST: 5 runtime issues detected

Phase 2: RAG Retrieval ━━━━━━━━━━ 100% ✓
  └─ Retrieved compliance context for 25 vulns

Phase 3: Policy Generation ━━━━━━ 80%
  ├─ Generated 20/25 policies
  └─ Current: SQL Injection policy...

Phase 4: Evaluation ━━━━━━━━━━━━━ 0%
  └─ Calculating BLEU/ROUGE scores...
```

---

**(See PART 2 for API Details, Challenges, Testing, and Deployment)**
