# Implementation Roadmap - AI Security Policy Generator Enhancements

## Overview
This document outlines all planned enhancements to add comprehensive features including detailed workflow visualization, compliance validation, and GitHub integration.

---

## Priority 0: Critical Fixes (MUST FIX NOW)

### Task 0.1: Fix SCA Parser Bug
**Status:** 🔴 **CRITICAL - BROKEN**
**Time Estimate:** 10 minutes
**Difficulty:** Easy

**Problem:**
```
Warning: Skipping malformed vulnerability: 'list' object has no attribute 'get'
Found 0 SCA vulnerabilities
```

**Root Cause:**
The npm audit format in `mock_sca_report.json` has vulnerabilities as arrays:
```json
{
  "vulnerabilities": {
    "lodash": [ {...} ],  // Array, not object
    "express": [ {...} ]
  }
}
```

The parser in `backend/parsers/sca_parser.py` expects direct objects.

**Solution:**
Update `_parse_npm_audit()` method to iterate through vulnerability arrays correctly.

**Files to Modify:**
- `backend/parsers/sca_parser.py` - Lines 70-120

**Acceptance Criteria:**
- [ ] SCA parser correctly processes all 11 vulnerabilities from mock report
- [ ] No "Skipping malformed vulnerability" warnings
- [ ] Frontend displays "SCA: 11" in parsing phase

---

## Priority 1: Enhanced Real-Time Workflow View

### Task 1.1: Backend - Enhanced WebSocket Messages
**Status:** 🟡 **Enhancement**
**Time Estimate:** 2 hours
**Difficulty:** Medium

**Goal:**
Send detailed, granular progress updates for each step of the pipeline.

**New WebSocket Message Types:**

#### Phase 1: Parsing
```json
{
  "phase": "parsing",
  "status": "in_progress",
  "message": "Parsing SAST report...",
  "data": {
    "current_parser": "SAST",
    "parser_status": "running",
    "file_name": "mock_sast_report.json"
  }
}

{
  "phase": "parsing",
  "status": "in_progress",
  "message": "SAST parsing complete",
  "data": {
    "current_parser": "SAST",
    "parser_status": "completed",
    "vulnerabilities_found": 8,
    "vulnerabilities": [
      {"title": "SQL Injection", "severity": "HIGH", "file": "UserController.js"},
      ...
    ]
  }
}

{
  "phase": "parsing",
  "status": "in_progress",
  "message": "Parsing SCA report...",
  "data": {
    "current_parser": "SCA",
    "parser_status": "running",
    "file_name": "mock_sca_report.json"
  }
}
```

#### Phase 2: RAG Retrieval
```json
{
  "phase": "rag",
  "status": "in_progress",
  "message": "Retrieving compliance contexts from vector database...",
  "data": {
    "rag_status": "fetching_nist",
    "standard": "NIST CSF"
  }
}

{
  "phase": "rag",
  "status": "in_progress",
  "message": "NIST CSF contexts retrieved",
  "data": {
    "rag_status": "nist_complete",
    "standard": "NIST CSF",
    "contexts_retrieved": 15,
    "controls": ["ID.RA-1", "PR.AC-4", "DE.CM-7", ...]
  }
}

{
  "phase": "rag",
  "status": "in_progress",
  "message": "Retrieving ISO 27001 contexts...",
  "data": {
    "rag_status": "fetching_iso",
    "standard": "ISO 27001"
  }
}

{
  "phase": "rag",
  "status": "completed",
  "message": "All compliance contexts retrieved",
  "data": {
    "total_contexts": 27,
    "standards": ["NIST CSF", "ISO 27001"],
    "nist_controls": 15,
    "iso_controls": 12
  }
}
```

#### Phase 3: LLM Generation (Most Detailed)
```json
{
  "phase": "llm_generation",
  "status": "in_progress",
  "message": "Starting AI policy generation for 27 vulnerabilities",
  "data": {
    "total_vulnerabilities": 27,
    "processed": 0,
    "llm_routing": {
      "SAST": "LLaMA 3.3 70B",
      "SCA": "LLaMA 3.3 70B",
      "DAST": "LLaMA 3.1 8B Instant"
    }
  }
}

{
  "phase": "llm_generation",
  "status": "in_progress",
  "message": "Generating policy for SQL Injection vulnerability",
  "data": {
    "processed": 1,
    "total": 27,
    "current_vuln": {
      "title": "SQL Injection",
      "severity": "HIGH",
      "type": "SAST",
      "cwe": "CWE-89",
      "file": "UserController.js:45"
    },
    "llm_model": "LLaMA 3.3 70B",
    "llm_status": "generating",
    "progress_percentage": 3.7
  }
}

{
  "phase": "llm_generation",
  "status": "in_progress",
  "message": "Policy generated for SQL Injection",
  "data": {
    "processed": 1,
    "total": 27,
    "current_vuln": {
      "title": "SQL Injection",
      "severity": "HIGH",
      "type": "SAST"
    },
    "llm_model": "LLaMA 3.3 70B",
    "llm_status": "completed",
    "policy_preview": "## POLICY IDENTIFIER SP-2024-001: SQL Injection Prevention Policy...",
    "compliance_mapped": ["NIST CSF: PR.AC-4", "ISO 27001: A.14.2.5"],
    "progress_percentage": 3.7
  }
}

// Repeat for each vulnerability...

{
  "phase": "llm_generation",
  "status": "completed",
  "message": "All policies generated successfully",
  "data": {
    "total_generated": 27,
    "llm_usage": {
      "llama_70b": 19,
      "llama_8b": 8
    }
  }
}
```

#### Phase 4: Evaluation
```json
{
  "phase": "evaluation",
  "status": "in_progress",
  "message": "Calculating BLEU-4 scores...",
  "data": {
    "metric": "BLEU-4",
    "status": "calculating"
  }
}

{
  "phase": "evaluation",
  "status": "in_progress",
  "message": "BLEU-4 scores calculated",
  "data": {
    "metric": "BLEU-4",
    "status": "completed",
    "avg_score": 0.72,
    "scores": [0.68, 0.75, 0.71, ...]
  }
}

{
  "phase": "evaluation",
  "status": "completed",
  "message": "Quality evaluation complete",
  "data": {
    "bleu_avg": 0.72,
    "rouge_avg": 0.68,
    "quality_score": 87.5
  }
}
```

#### Phase 5: Compliance Validation (NEW!)
```json
{
  "phase": "compliance_validation",
  "status": "in_progress",
  "message": "Validating compliance coverage...",
  "data": {
    "validation_type": "coverage_analysis"
  }
}

{
  "phase": "compliance_validation",
  "status": "completed",
  "message": "Compliance validation complete",
  "data": {
    "validation_results": {
      "coverage_analysis": {
        "nist_csf": {
          "total_controls": 23,
          "covered_controls": 18,
          "coverage_percentage": 78.3,
          "gaps": ["RS.RP-1", "RC.RP-1", "RC.IM-1", "RC.IM-2", "RC.CO-3"]
        },
        "iso_27001": {
          "total_controls": 114,
          "covered_controls": 89,
          "coverage_percentage": 78.1,
          "gaps": ["A.16.1.1", "A.16.1.2", ...]
        },
        "overall_score": 78.2
      }
    }
  }
}
```

#### Phase 6: Saving
```json
{
  "phase": "saving",
  "status": "in_progress",
  "message": "Saving policy files...",
  "data": {
    "files_saving": ["TXT", "HTML", "JSON"]
  }
}

{
  "phase": "saving",
  "status": "completed",
  "message": "All files saved successfully",
  "data": {
    "files_saved": [
      "security_policy_20251031_161652.txt",
      "security_policy_20251031_161652.html",
      "policy_generation_20251031_161652.json"
    ],
    "output_directory": "outputs"
  }
}
```

#### Final Complete Message
```json
{
  "phase": "complete",
  "status": "completed",
  "message": "Policy generation complete!",
  "data": {
    "total_vulns": 27,
    "total_policies": 27,
    "output_file": "outputs/security_policy_20251031_161652.txt",
    "html_file": "outputs/security_policy_20251031_161652.html",
    "json_file": "outputs/policy_generation_20251031_161652.json",
    "evaluation": {
      "avg_bleu": 0.72,
      "avg_rouge": 0.68
    },
    "compliance": {
      "overall_score": 78.2,
      "nist_coverage": 78.3,
      "iso_coverage": 78.1
    }
  }
}
```

**Files to Modify:**
- `backend/api/main.py` - Update WebSocket message sending logic
- `backend/orchestrator/policy_generator.py` - Add detailed progress callbacks

**Acceptance Criteria:**
- [ ] WebSocket sends messages for each parser (SAST, SCA, DAST)
- [ ] WebSocket sends RAG retrieval details with control counts
- [ ] WebSocket sends per-vulnerability LLM generation updates
- [ ] WebSocket sends evaluation metrics
- [ ] WebSocket sends compliance validation results
- [ ] WebSocket sends file saving confirmation

---

### Task 1.2: Frontend - GitHub Actions Style Workflow Component
**Status:** 🟡 **Enhancement**
**Time Estimate:** 3-4 hours
**Difficulty:** Medium

**Goal:**
Create a collapsible, expandable workflow view similar to GitHub Actions with real-time updates.

**New Component: `WorkflowView.jsx`**

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────┐
│  🔄 AI Security Policy Generation Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ▼ Phase 1: Parsing Security Reports                       ✓    │
│     ├─ 📄 SAST Parser (Semgrep)                           ✓    │
│     │   Found 8 vulnerabilities in mock_sast_report.json        │
│     │   • SQL Injection (HIGH) - UserController.js:45           │
│     │   • XSS (MEDIUM) - profile.mustache:23                    │
│     │   • Path Traversal (HIGH) - files.js:67                   │
│     │   ... [View All 8]                                        │
│     │                                                            │
│     ├─ 📦 SCA Parser (npm audit)                          ✓    │
│     │   Found 11 vulnerabilities in dependencies                │
│     │   • lodash: Prototype Pollution (HIGH)                    │
│     │   • minimist: Prototype Pollution (CRITICAL)              │
│     │   ... [View All 11]                                       │
│     │                                                            │
│     └─ 🌐 DAST Parser (OWASP ZAP)                         ✓    │
│         Found 8 vulnerabilities in runtime testing               │
│         • SQL Injection (HIGH) - /api/users/search              │
│         • Reflected XSS (HIGH) - /search?q=                     │
│         ... [View All 8]                                        │
│                                                                  │
│  ▼ Phase 2: RAG Compliance Retrieval                       ✓    │
│     ├─ 🗂️  Fetching NIST CSF contexts...                  ✓    │
│     │   Retrieved 15 controls: ID.RA-1, PR.AC-4, DE.CM-7...    │
│     │                                                            │
│     └─ 🗂️  Fetching ISO 27001 contexts...                 ✓    │
│         Retrieved 12 controls: A.9.4.1, A.12.6.1, A.14.2.5...  │
│                                                                  │
│  ▶ Phase 3: LLM Policy Generation                         ⏳    │
│     ├─ 🤖 [1/27] SQL Injection (SAST)                     ✓    │
│     │   Model: LLaMA 3.3 70B (Groq)                             │
│     │   Compliance: PR.AC-4, A.14.2.5                           │
│     │   Policy: ## POLICY IDENTIFIER SP-2024-001...            │
│     │                                                            │
│     ├─ 🤖 [2/27] XSS (SAST)                               ✓    │
│     │   Model: LLaMA 3.3 70B (Groq)                             │
│     │   Compliance: PR.DS-5, A.14.1.2                           │
│     │                                                            │
│     ├─ 🤖 [3/27] lodash Prototype Pollution (SCA)         🔄    │
│     │   Model: LLaMA 3.3 70B (Groq)                             │
│     │   Status: Generating policy...                            │
│     │   [████████░░░░░░░░░░░░] 11%                             │
│     │                                                            │
│     └─ ... [24 more]                                            │
│                                                                  │
│  ⏸️  Phase 4: Quality Evaluation                          ⏸️     │
│     └─ Waiting for policy generation to complete...            │
│                                                                  │
│  ⏸️  Phase 5: Compliance Validation                       ⏸️     │
│     └─ Waiting for evaluation to complete...                   │
│                                                                  │
│  ⏸️  Phase 6: Saving Results                              ⏸️     │
│     └─ Waiting for validation to complete...                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Component Structure:**
```jsx
<WorkflowView
  progress={progressUpdates}
  onPhaseExpand={handleExpand}
/>
  └─ <PhaseSection
       phase="parsing"
       status="completed"
       expanded={true}
     />
       └─ <ParserStep
            parser="SAST"
            vulnerabilities={[...]}
          />
       └─ <ParserStep parser="SCA" />
       └─ <ParserStep parser="DAST" />

  └─ <PhaseSection phase="rag" />
       └─ <RAGStep standard="NIST CSF" />
       └─ <RAGStep standard="ISO 27001" />

  └─ <PhaseSection phase="llm_generation" />
       └─ <LLMGenerationStep vuln={...} index={1} />
       └─ <LLMGenerationStep vuln={...} index={2} />
       └─ ... (27 total)

  └─ <PhaseSection phase="evaluation" />
  └─ <PhaseSection phase="compliance_validation" />
  └─ <PhaseSection phase="saving" />
```

**Features:**
- Collapsible/expandable sections
- Real-time status icons (⏸️ ⏳ ✓ ❌)
- Progress bars for long operations
- Color-coded severity badges
- Auto-scroll to current phase
- Expand all / Collapse all buttons
- Download logs button

**Files to Create:**
- `frontend/src/components/WorkflowView.jsx` (main component)
- `frontend/src/components/workflow/PhaseSection.jsx`
- `frontend/src/components/workflow/ParserStep.jsx`
- `frontend/src/components/workflow/RAGStep.jsx`
- `frontend/src/components/workflow/LLMGenerationStep.jsx`
- `frontend/src/components/workflow/EvaluationStep.jsx`
- `frontend/src/components/workflow/ComplianceStep.jsx`

**Files to Modify:**
- `frontend/src/App.jsx` - Replace `RealTimeDashboard` with `WorkflowView`

**Acceptance Criteria:**
- [ ] All 6 phases displayed with collapsible sections
- [ ] Real-time updates from WebSocket reflected in UI
- [ ] Auto-scroll to active phase
- [ ] Each vulnerability shows LLM model used
- [ ] Progress bars for LLM generation
- [ ] Expand/collapse all functionality
- [ ] Mobile responsive design

---

## Priority 2: Compliance Validation System

### Task 2.1: Option A - Automated Coverage Analysis
**Status:** 🟢 **High Value**
**Time Estimate:** 2 hours
**Difficulty:** Medium

**Goal:**
Automatically analyze which NIST CSF and ISO 27001 controls are covered by generated policies.

**Implementation:**

**Backend - New Module: `backend/compliance/coverage_analyzer.py`**

```python
class ComplianceCoverageAnalyzer:
    """
    Analyzes compliance control coverage in generated policies
    """

    def __init__(self):
        self.nist_csf_controls = {
            "ID.RA": ["ID.RA-1", "ID.RA-2", "ID.RA-3", "ID.RA-4", "ID.RA-5", "ID.RA-6"],
            "PR.AC": ["PR.AC-1", "PR.AC-2", "PR.AC-3", "PR.AC-4", "PR.AC-5", "PR.AC-6", "PR.AC-7"],
            "PR.DS": ["PR.DS-1", "PR.DS-2", "PR.DS-3", "PR.DS-4", "PR.DS-5", "PR.DS-6", "PR.DS-7"],
            "DE.CM": ["DE.CM-1", "DE.CM-2", "DE.CM-3", "DE.CM-4", "DE.CM-5", "DE.CM-6", "DE.CM-7", "DE.CM-8"],
            "RS.RP": ["RS.RP-1"],
            "RS.CO": ["RS.CO-1", "RS.CO-2", "RS.CO-3", "RS.CO-4", "RS.CO-5"],
            "RC.RP": ["RC.RP-1"],
            "RC.IM": ["RC.IM-1", "RC.IM-2"],
            "RC.CO": ["RC.CO-1", "RC.CO-2", "RC.CO-3"]
            # ... all controls
        }

        self.iso_27001_controls = {
            "A.9": ["A.9.1.1", "A.9.1.2", "A.9.2.1", ...],
            "A.12": ["A.12.1.1", "A.12.2.1", ...],
            "A.14": ["A.14.1.1", "A.14.1.2", "A.14.2.1", ...],
            "A.16": ["A.16.1.1", "A.16.1.2", ...],
            # ... all controls
        }

    def analyze_coverage(self, policies: List[Dict]) -> Dict:
        """
        Analyzes compliance coverage from generated policies
        """
        nist_covered = set()
        iso_covered = set()

        for policy in policies:
            if "compliance_mapping" in policy:
                mappings = policy["compliance_mapping"]

                # Extract NIST controls
                if "NIST CSF" in mappings:
                    nist_covered.update(mappings["NIST CSF"])

                # Extract ISO controls
                if "ISO 27001" in mappings:
                    iso_covered.update(mappings["ISO 27001"])

        # Calculate coverage
        all_nist = self._get_all_nist_controls()
        all_iso = self._get_all_iso_controls()

        nist_gaps = set(all_nist) - nist_covered
        iso_gaps = set(all_iso) - iso_covered

        return {
            "nist_csf": {
                "total_controls": len(all_nist),
                "covered_controls": len(nist_covered),
                "coverage_percentage": (len(nist_covered) / len(all_nist)) * 100,
                "covered": sorted(list(nist_covered)),
                "gaps": sorted(list(nist_gaps))
            },
            "iso_27001": {
                "total_controls": len(all_iso),
                "covered_controls": len(iso_covered),
                "coverage_percentage": (len(iso_covered) / len(all_iso)) * 100,
                "covered": sorted(list(iso_covered)),
                "gaps": sorted(list(iso_gaps))
            },
            "overall_score": ((len(nist_covered) / len(all_nist)) +
                            (len(iso_covered) / len(all_iso))) / 2 * 100
        }
```

**Frontend - New Component: `ComplianceValidation.jsx`**

Shows coverage analysis with visual indicators:
- Progress circles for NIST CSF and ISO 27001
- List of covered controls (green checkmarks)
- List of gaps (red warnings)
- Overall compliance score

**Files to Create:**
- `backend/compliance/__init__.py`
- `backend/compliance/coverage_analyzer.py`
- `frontend/src/components/ComplianceValidation.jsx`

**Files to Modify:**
- `backend/orchestrator/policy_generator.py` - Add coverage analysis step
- `backend/api/main.py` - Include compliance in results
- `frontend/src/components/ResultsView.jsx` - Add compliance section

**Acceptance Criteria:**
- [ ] Identifies all NIST CSF controls mentioned in policies
- [ ] Identifies all ISO 27001 controls mentioned in policies
- [ ] Calculates coverage percentage
- [ ] Lists gaps (missing controls)
- [ ] Displays overall compliance score
- [ ] Shows control-by-control breakdown

---

### Task 2.2: Option B - Reference Policy Comparison
**Status:** 🟢 **High Value**
**Time Estimate:** 2 hours
**Difficulty:** Medium

**Goal:**
Allow users to upload a "golden" reference policy and compare generated policies against it.

**Implementation:**

**Upload Interface:**
- New upload zone: "Upload Reference Policy (Optional)"
- Accepts .txt or .md files
- Stores in temp location

**Comparison Metrics:**
1. **BLEU Score** - Similarity to reference (already have this)
2. **ROUGE Score** - Overlap in content (already have this)
3. **Key Term Coverage** - Check if critical security terms present
4. **Structural Similarity** - Compare section structure

**Backend - New Module: `backend/compliance/reference_comparator.py`**

```python
class ReferencePolicyComparator:
    """
    Compares generated policies against a reference/golden policy
    """

    def compare(self, generated_policy: str, reference_policy: str) -> Dict:
        """
        Performs detailed comparison
        """
        return {
            "bleu_score": self._calculate_bleu(generated, reference),
            "rouge_score": self._calculate_rouge(generated, reference),
            "key_terms_coverage": self._check_key_terms(generated, reference),
            "structural_similarity": self._compare_structure(generated, reference),
            "overall_similarity": self._calculate_overall(...)
        }

    def _check_key_terms(self, generated: str, reference: str) -> Dict:
        """
        Extracts key security terms from reference and checks coverage
        """
        reference_terms = self._extract_security_terms(reference)
        generated_terms = self._extract_security_terms(generated)

        overlap = set(reference_terms) & set(generated_terms)

        return {
            "reference_terms": len(reference_terms),
            "generated_terms": len(generated_terms),
            "overlap": len(overlap),
            "coverage_percentage": (len(overlap) / len(reference_terms)) * 100,
            "missing_terms": list(set(reference_terms) - set(generated_terms))
        }
```

**Files to Create:**
- `backend/compliance/reference_comparator.py`
- `frontend/src/components/ReferenceUpload.jsx`

**Files to Modify:**
- `backend/api/main.py` - Add reference_file parameter
- `frontend/src/components/UploadMode.jsx` - Add reference upload zone

**Acceptance Criteria:**
- [ ] Users can upload reference policy
- [ ] System calculates BLEU/ROUGE against reference
- [ ] Key term coverage analyzed
- [ ] Structural similarity calculated
- [ ] Results displayed with recommendations

---

### Task 2.3: Option C - Control Checklist Validation
**Status:** 🟢 **High Value**
**Time Estimate:** 1.5 hours
**Difficulty:** Easy-Medium

**Goal:**
Provide a comprehensive checklist showing which controls are addressed.

**Implementation:**

**Frontend Component: `ComplianceChecklist.jsx`**

```jsx
NIST CSF Checklist:
├─ Identify (ID)
│  ├─ ✅ ID.RA-1: Asset vulnerabilities are identified (3 policies)
│  ├─ ✅ ID.RA-2: Cyber threat intelligence received (1 policy)
│  ├─ ❌ ID.RA-3: Threats are identified
│  └─ ✅ ID.RA-5: Threats and vulnerabilities communicated (8 policies)
│
├─ Protect (PR)
│  ├─ ✅ PR.AC-1: Identities managed (2 policies)
│  ├─ ✅ PR.AC-4: Access permissions managed (5 policies)
│  ├─ ❌ PR.AC-7: Users authenticated
│  └─ ✅ PR.DS-5: Protection against data leaks (4 policies)
│
├─ Detect (DE)
│  └─ ✅ DE.CM-1: Network monitored (2 policies)
│
├─ Respond (RS)
│  └─ ❌ RS.RP-1: Response plan executed
│
└─ Recover (RC)
   └─ ❌ RC.RP-1: Recovery plan executed

ISO 27001 Checklist:
├─ A.9: Access Control
│  ├─ ✅ A.9.1.1: Access control policy (3 policies)
│  └─ ✅ A.9.4.1: Information access restriction (5 policies)
│
├─ A.12: Operations Security
│  ├─ ✅ A.12.6.1: Management of technical vulnerabilities (11 policies)
│  └─ ✅ A.12.2.1: Controls against malware (2 policies)
│
├─ A.14: System Acquisition & Development
│  ├─ ✅ A.14.2.1: Secure development policy (8 policies)
│  └─ ✅ A.14.2.5: Secure system principles (7 policies)
│
└─ A.16: Incident Management
   └─ ❌ A.16.1.1: Responsibilities and procedures
```

**Interactive Features:**
- Filter by covered/uncovered
- Export checklist as PDF
- Click control to see which policies address it

**Files to Create:**
- `frontend/src/components/ComplianceChecklist.jsx`
- `backend/compliance/checklist_generator.py`

**Acceptance Criteria:**
- [ ] All NIST CSF controls listed with status
- [ ] All ISO 27001 controls listed with status
- [ ] Shows which policies address each control
- [ ] Filter and export functionality
- [ ] Visual progress indicators

---

## Priority 3: GitHub OAuth Integration & Repository Scanner

### Task 3.1: GitHub OAuth Setup
**Status:** 🟡 **Complex**
**Time Estimate:** 2 hours
**Difficulty:** Medium-Hard

**Prerequisites:**
1. Create GitHub OAuth App at https://github.com/settings/developers
2. Get Client ID and Client Secret
3. Set callback URL: `http://localhost:8000/api/github/oauth/callback`

**Environment Variables:**
```env
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/github/oauth/callback
```

**Backend - New Module: `backend/integrations/github_oauth.py`**

```python
class GitHubOAuthClient:
    """
    Handles GitHub OAuth authentication flow
    """

    def __init__(self):
        self.client_id = os.getenv("GITHUB_CLIENT_ID")
        self.client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GITHUB_REDIRECT_URI")

    def get_authorization_url(self, state: str) -> str:
        """
        Returns GitHub OAuth authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "repo,read:user",
            "state": state
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Exchanges authorization code for access token
        """
        # POST to https://github.com/login/oauth/access_token
        # Returns access token

    async def get_user_info(self, access_token: str) -> Dict:
        """
        Gets authenticated user information
        """
        # GET https://api.github.com/user
```

**New API Endpoints:**

```python
# backend/api/main.py

@app.get("/api/github/oauth/login")
async def github_oauth_login():
    """
    Initiates GitHub OAuth flow
    """
    state = secrets.token_urlsafe(32)
    # Store state in session/cache
    auth_url = github_client.get_authorization_url(state)
    return {"auth_url": auth_url, "state": state}

@app.get("/api/github/oauth/callback")
async def github_oauth_callback(code: str, state: str):
    """
    Handles GitHub OAuth callback
    """
    # Verify state
    # Exchange code for token
    access_token = await github_client.exchange_code_for_token(code)
    user_info = await github_client.get_user_info(access_token)

    # Store token securely (in-memory cache for now)
    # Return success and redirect to frontend
    return RedirectResponse(url=f"http://localhost:3000?github_auth=success&token={...}")
```

**Files to Create:**
- `backend/integrations/__init__.py`
- `backend/integrations/github_oauth.py`

**Files to Modify:**
- `backend/api/main.py` - Add OAuth endpoints
- `.env` - Add GitHub credentials

**Acceptance Criteria:**
- [ ] OAuth flow initiates from frontend
- [ ] User redirected to GitHub for authorization
- [ ] Callback handled successfully
- [ ] Access token stored securely
- [ ] User info retrieved

---

### Task 3.2: Repository Listing & Selection
**Status:** 🟡 **Medium**
**Time Estimate:** 2 hours
**Difficulty:** Medium

**Backend - Extend GitHubOAuthClient:**

```python
async def list_repositories(self, access_token: str, page: int = 1, per_page: int = 30) -> List[Dict]:
    """
    Lists user's repositories
    """
    # GET https://api.github.com/user/repos
    # Returns list of repos with metadata

async def get_repository_branches(self, access_token: str, owner: str, repo: str) -> List[str]:
    """
    Gets branches for a repository
    """
    # GET https://api.github.com/repos/{owner}/{repo}/branches
```

**New API Endpoints:**

```python
@app.get("/api/github/repos")
async def list_github_repos(token: str, page: int = 1):
    """
    Lists user's GitHub repositories
    """
    repos = await github_client.list_repositories(token, page)
    return {"repositories": repos}

@app.get("/api/github/repos/{owner}/{repo}/branches")
async def list_repo_branches(owner: str, repo: str, token: str):
    """
    Lists branches for a repository
    """
    branches = await github_client.get_repository_branches(token, owner, repo)
    return {"branches": branches}
```

**Frontend - New Component: `GitHubScanMode.jsx`**

```jsx
<GitHubScanMode>
  {!authenticated ? (
    <button onClick={handleGitHubLogin}>
      Connect to GitHub
    </button>
  ) : (
    <>
      <RepositorySelector
        repositories={repos}
        onSelect={setSelectedRepo}
      />

      <BranchSelector
        branches={branches}
        onSelect={setSelectedBranch}
      />

      <ScanOptions>
        <checkbox> Run SAST (Semgrep)
        <checkbox> Run SCA (Trivy)
      </ScanOptions>

      <button onClick={handleScan}>
        Scan Repository
      </button>
    </>
  )}
</GitHubScanMode>
```

**Files to Create:**
- `frontend/src/components/GitHubScanMode.jsx`
- `frontend/src/components/github/RepositorySelector.jsx`
- `frontend/src/components/github/BranchSelector.jsx`

**Files to Modify:**
- `frontend/src/App.jsx` - Add mode toggle (Upload vs GitHub)

**Acceptance Criteria:**
- [ ] User can authenticate with GitHub
- [ ] User sees list of their repositories
- [ ] User can select repository
- [ ] User can select branch
- [ ] User can choose scan types

---

### Task 3.3: Repository Clone & Scan
**Status:** 🟡 **Complex**
**Time Estimate:** 3-4 hours
**Difficulty:** Hard

**Backend - New Module: `backend/scanners/github_scanner.py`**

```python
class GitHubRepositoryScanner:
    """
    Clones and scans GitHub repositories
    """

    async def clone_repository(self, repo_url: str, branch: str, access_token: str) -> str:
        """
        Clones repository to temporary directory
        """
        temp_dir = tempfile.mkdtemp(prefix="scan_")

        # Clone with token authentication
        auth_url = repo_url.replace("https://", f"https://{access_token}@")

        subprocess.run([
            "git", "clone",
            "--depth", "1",
            "--branch", branch,
            auth_url,
            temp_dir
        ])

        return temp_dir

    async def run_sast_scan(self, repo_path: str) -> Dict:
        """
        Runs Semgrep SAST scan
        """
        output_file = f"{repo_path}/sast_report.json"

        subprocess.run([
            "semgrep",
            "--config=auto",
            "--json",
            f"--output={output_file}",
            repo_path
        ])

        return self._read_json(output_file)

    async def run_sca_scan(self, repo_path: str) -> Dict:
        """
        Runs Trivy SCA scan
        """
        output_file = f"{repo_path}/sca_report.json"

        subprocess.run([
            "trivy", "fs",
            "--format", "json",
            "--scanners", "vuln",
            f"--output={output_file}",
            repo_path
        ])

        return self._read_json(output_file)

    def cleanup(self, repo_path: str):
        """
        Removes temporary clone directory
        """
        shutil.rmtree(repo_path)
```

**New API Endpoint:**

```python
@app.post("/api/github/scan")
async def scan_github_repository(
    repo_owner: str,
    repo_name: str,
    branch: str,
    token: str,
    run_sast: bool = True,
    run_sca: bool = True
):
    """
    Clones and scans GitHub repository
    """
    scanner = GitHubRepositoryScanner()

    try:
        # Clone repository
        repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"
        repo_path = await scanner.clone_repository(repo_url, branch, token)

        # Send progress via WebSocket
        await websocket.send_json({
            "phase": "github_scan",
            "status": "in_progress",
            "message": f"Cloned repository: {repo_name}"
        })

        # Run scans
        sast_results = None
        sca_results = None

        if run_sast:
            await websocket.send_json({
                "phase": "github_scan",
                "message": "Running SAST scan with Semgrep..."
            })
            sast_results = await scanner.run_sast_scan(repo_path)

        if run_sca:
            await websocket.send_json({
                "phase": "github_scan",
                "message": "Running SCA scan with Trivy..."
            })
            sca_results = await scanner.run_sca_scan(repo_path)

        # Generate policies from scan results
        # ... (use existing orchestrator)

        # Cleanup
        scanner.cleanup(repo_path)

        return {"status": "success", "results": ...}

    except Exception as e:
        scanner.cleanup(repo_path)
        raise HTTPException(status_code=500, detail=str(e))
```

**Files to Create:**
- `backend/scanners/__init__.py`
- `backend/scanners/github_scanner.py`

**Files to Modify:**
- `backend/api/main.py` - Add scan endpoint

**Acceptance Criteria:**
- [ ] Repository cloned successfully to temp directory
- [ ] SAST scan runs with Semgrep
- [ ] SCA scan runs with Trivy
- [ ] Results parsed correctly
- [ ] Policies generated from scan results
- [ ] Temp directory cleaned up
- [ ] Progress updates sent via WebSocket

---

### Task 3.4: Frontend GitHub Integration UI
**Status:** 🟡 **Medium**
**Time Estimate:** 2 hours
**Difficulty:** Medium

**Main App Updates:**

```jsx
// App.jsx

const [mode, setMode] = useState('upload'); // 'upload' or 'github'
const [githubAuth, setGitHubAuth] = useState(null);

return (
  <div>
    {/* Mode Toggle */}
    <div className="mode-selector">
      <button
        onClick={() => setMode('upload')}
        className={mode === 'upload' ? 'active' : ''}
      >
        Upload Reports
      </button>
      <button
        onClick={() => setMode('github')}
        className={mode === 'github' ? 'active' : ''}
      >
        Scan GitHub Repository
      </button>
    </div>

    {/* Render appropriate mode */}
    {mode === 'upload' ? (
      <UploadMode ... />
    ) : (
      <GitHubScanMode
        auth={githubAuth}
        onAuthChange={setGitHubAuth}
      />
    )}
  </div>
);
```

**Files to Modify:**
- `frontend/src/App.jsx` - Add mode toggle and GitHub mode

**Acceptance Criteria:**
- [ ] Mode toggle between Upload and GitHub
- [ ] GitHub mode shows authentication flow
- [ ] Repository selection works
- [ ] Scan initiates correctly
- [ ] Progress shown in WorkflowView
- [ ] Results displayed same as upload mode

---

## Implementation Order

### Week 1: Critical Fixes + Enhanced Workflow
**Day 1:**
- [ ] Task 0.1: Fix SCA parser (10 min)
- [ ] Task 1.1: Enhanced WebSocket messages (2 hrs)

**Day 2:**
- [ ] Task 1.2: WorkflowView component (4 hrs)

**Day 3:**
- [ ] Complete WorkflowView sub-components
- [ ] Testing and refinement

### Week 2: Compliance Validation
**Day 4:**
- [ ] Task 2.1: Coverage analysis (2 hrs)

**Day 5:**
- [ ] Task 2.2: Reference comparison (2 hrs)
- [ ] Task 2.3: Control checklist (1.5 hrs)

**Day 6:**
- [ ] Compliance validation frontend components
- [ ] Integration and testing

### Week 3: GitHub Integration
**Day 7:**
- [ ] Task 3.1: GitHub OAuth setup (2 hrs)

**Day 8:**
- [ ] Task 3.2: Repository listing (2 hrs)

**Day 9:**
- [ ] Task 3.3: Repository scanning (4 hrs)

**Day 10:**
- [ ] Task 3.4: GitHub frontend UI (2 hrs)
- [ ] End-to-end testing

---

## Testing Checklist

### Enhanced Workflow Testing
- [ ] All 6 phases display correctly
- [ ] Collapsible sections work
- [ ] Real-time updates appear instantly
- [ ] Auto-scroll to active phase
- [ ] Each vulnerability shows correct LLM model
- [ ] Progress bars animate smoothly
- [ ] Mobile responsive

### Compliance Validation Testing
- [ ] Coverage analysis shows correct percentages
- [ ] Reference comparison works with uploaded policy
- [ ] Control checklist displays all controls
- [ ] Gaps identified correctly
- [ ] Export functionality works

### GitHub Integration Testing
- [ ] OAuth flow completes successfully
- [ ] Repository list loads
- [ ] Branch selection works
- [ ] SAST scan runs on real repo
- [ ] SCA scan runs on real repo
- [ ] Results processed correctly
- [ ] Temp directories cleaned up

---

## Success Metrics

### Performance
- WebSocket latency < 50ms
- UI updates < 100ms after backend event
- GitHub clone + scan < 5 minutes
- Compliance analysis < 2 seconds

### User Experience
- All phases visible in workflow view
- No manual refresh needed
- Clear progress indication
- Actionable compliance gaps

### Accuracy
- 100% of vulnerabilities displayed
- Correct LLM routing shown
- Accurate compliance coverage
- Proper GitHub authentication

---

## Future Enhancements (Post-Implementation)

### Phase 2 Ideas:
1. **Webhook Integration** - Auto-scan on git push
2. **Multi-Repository Support** - Scan multiple repos at once
3. **Historical Tracking** - Track compliance over time
4. **Custom Compliance Frameworks** - Add CIS, PCI-DSS, SOC 2
5. **Policy Templates** - Pre-built policy templates
6. **Team Collaboration** - Share reports with team
7. **Scheduled Scans** - Cron-based automated scanning
8. **Slack/Email Notifications** - Alert on scan completion
9. **PDF Reports** - Export professional PDF reports
10. **Dark Mode** - UI theme toggle

---

## Notes

- All implementations should maintain backward compatibility
- WebSocket messages should be versioned for future changes
- GitHub token should be stored securely (consider Redis for production)
- Rate limiting should be implemented for GitHub API calls
- Error handling must be comprehensive
- All new features need unit tests
- Documentation should be updated with each task

---

**Last Updated:** 2024-10-31
**Status:** Ready for implementation
**Estimated Total Time:** 30-35 hours
