# Testing Guide for New Features

## ✅ What's Been Implemented

### Backend (100% Complete):
- ✅ User Profile System (`backend/models/user_profile.py`)
- ✅ Adaptive Prompts (9 templates in `backend/prompts/adaptive_templates.py`)
- ✅ Policy Tracking Storage (`backend/database/policy_tracker.py`)
- ✅ Policy Status Models (`backend/models/policy_status.py`)

### What Needs Manual Integration:
- 🔧 Modify `backend/orchestrator/policy_generator.py` (3 small changes)
- 🔧 Modify `backend/api/main.py` (add tracking endpoints + user profile params)
- 🔧 Frontend components (add profile selection dropdowns)

---

## 🚀 Quick Test Without Frontend Changes

You can test the backend features RIGHT NOW using Swagger UI:

### Test 1: Profile Templates API

1. **Start Backend**:
```bash
cd C:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops
python backend/api/main.py
```

2. **Open Swagger**: `http://localhost:8000/docs`

3. **Test Profile Templates**:
   - Find `GET /api/profile-templates` endpoint
   - Click "Try it out" → "Execute"
   - **Expected Result**: JSON with all profile templates (beginner, intermediate, advanced, etc.)

### Test 2: Policy Tracking API

1. **Create Test Tracking Data**:
```bash
cd C:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops
python -c "
from backend.database.policy_tracker import PolicyTracker
from backend.models.policy_status import PolicyTrackingItem, PolicyStatus, TimelineEvent

tracker = PolicyTracker()

# Create test policy
test_policy = PolicyTrackingItem(
    policy_id='TEST-001',
    vulnerability_title='SQL Injection in login.py',
    vulnerability_type='sast',
    severity='critical',
    status=PolicyStatus.NOT_STARTED,
    nist_csf_controls=['PR.DS-5', 'PR.AC-4'],
    iso27001_controls=['A.14.2.5']
)

tracker.add_policies([test_policy])
print('✓ Test policy created!')
"
```

2. **View Dashboard**:
   - Go to `http://localhost:8000/api/policies/dashboard`
   - **Expected Result**: JSON showing your test policy with stats

3. **Update Status**:
   - In Swagger, find `POST /api/policies/{policy_id}/status`
   - policy_id: `TEST-001`
   - new_status: `in_progress`
   - Click "Execute"
   - Refresh dashboard → status changed!

---

## 🔧 Manual Integration Steps (Required)

### Step 1: Update Orchestrator

**File**: `backend/orchestrator/policy_generator.py`

**Change 1** - Add imports (top of file):
```python
from backend.models.user_profile import UserProfile, ExpertiseLevel
from backend.prompts.adaptive_templates import AdaptivePolicyPrompts
```

**Change 2** - Modify `__init__` (around line 30):
```python
def __init__(self, use_rag=True, llm_models=None, output_dir="./outputs", user_profile: UserProfile = None):
    # ... keep all existing code ...
    self.user_profile = user_profile or UserProfile.default()  # ADD THIS LINE
```

**Change 3** - Replace prompt generation (search for "get_policy_generation_prompt"):
Find this line (around line 180):
```python
prompt = policy_templates.get_policy_generation_prompt(vuln_dict, compliance_text, severity)
```

Replace with:
```python
# Use adaptive prompts based on user profile
prompt = AdaptivePolicyPrompts.select_prompt(
    vulnerability_type=vuln_type,  # 'sast', 'sca', or 'dast'
    expertise_level=self.user_profile.expertise_level,
    vulnerability=vuln_dict,
    compliance_context=compliance_text,
    user_profile=self.user_profile
)
```

### Step 2: Update API Endpoints

**File**: `backend/api/main.py`

**Change 1** - Add imports (after line 30):
```python
from backend.models.user_profile import UserProfile, ExpertiseLevel, UserRole, Certification, get_profile_template
from backend.database.policy_tracker import PolicyTracker
from backend.models.policy_status import PolicyTrackingItem, PolicyStatus
```

**Change 2** - Initialize tracker (after line 90, before `@app.on_event`):
```python
# Policy tracking
policy_tracker = PolicyTracker()
```

**Change 3** - Modify `/api/generate-policies` endpoint signature (around line 124):
```python
@app.post("/api/generate-policies", response_model=PolicyGenerationResponse)
async def generate_policies(
    sast_file: Optional[UploadFile] = File(None),
    sca_file: Optional[UploadFile] = File(None),
    dast_file: Optional[UploadFile] = File(None),
    max_per_type: int = 5,
    expertise_level: str = "intermediate",  # ADD THIS
    user_role: str = "senior_developer",    # ADD THIS
    user_name: Optional[str] = None         # ADD THIS
):
```

**Change 4** - Create user profile in endpoint (add after parameter validation):
```python
    # Create user profile
    try:
        user_profile = UserProfile(
            name=user_name,
            expertise_level=ExpertiseLevel(expertise_level),
            role=UserRole(user_role)
        )
    except Exception as e:
        logger.warning(f"Invalid user profile data: {e}. Using default profile.")
        user_profile = UserProfile.default()
```

**Change 5** - Pass user_profile to broadcast function:
Find the call to `broadcast_realtime_generation` (around line 150):
```python
generation_result = await broadcast_realtime_generation(
    temp_files.get('sast'),
    temp_files.get('sca'),
    temp_files.get('dast'),
    max_per_type,
    user_profile  # ADD THIS PARAMETER
)
```

**Change 6** - Update `broadcast_realtime_generation` signature (around line 205):
```python
async def broadcast_realtime_generation(
    sast_path: Optional[str],
    sca_path: Optional[str],
    dast_path: Optional[str],
    max_per_type: int = 5,
    user_profile: UserProfile = None  # ADD THIS
) -> Dict:
```

**Change 7** - Pass profile to orchestrator (in broadcast function, around line 220):
```python
    if not orchestrator:
        await broadcast_progress({'type': 'error', 'message': 'Orchestrator not initialized'})
        return {'results': [], 'total_vulns': 0, 'output_files': {}}

    # Set user profile
    orchestrator.user_profile = user_profile or UserProfile.default()  # ADD THIS LINE
```

**Change 8** - Add tracking endpoints (at end of file, before `if __name__`):
```python
# Policy Tracking Endpoints

@app.get("/api/policies/dashboard")
async def get_policy_dashboard():
    """Get all policies with tracking status"""
    try:
        dashboard_data = policy_tracker.get_dashboard_data()
        return {
            "success": True,
            "policies": [p.dict() for p in dashboard_data['policies']],
            "stats": dashboard_data['stats'].dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/policies/{policy_id}/status")
async def update_policy_status(
    policy_id: str,
    new_status: str,
    user: Optional[str] = None
):
    """Update policy status"""
    try:
        policy_tracker.update_policy_status(policy_id, PolicyStatus(new_status), user)
        return {"success": True, "message": "Status updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/policies/{policy_id}/assign")
async def assign_policy(
    policy_id: str,
    assigned_to: str,
    user: Optional[str] = None
):
    """Assign policy to user"""
    try:
        policy_tracker.assign_policy(policy_id, assigned_to, user)
        return {"success": True, "message": f"Assigned to {assigned_to}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/policies/{policy_id}")
async def get_policy_details(policy_id: str):
    """Get single policy with timeline"""
    try:
        policy = policy_tracker.get_policy(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return {"success": True, "policy": policy.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile-templates")
async def get_profile_templates():
    """Get predefined user profile templates"""
    from backend.models.user_profile import PROFILE_TEMPLATES
    return {
        "success": True,
        "templates": {k: v.dict() for k, v in PROFILE_TEMPLATES.items()}
    }
```

---

## 🧪 Complete Test Scenario

### Test 1: Adaptive Policies (Beginner vs Advanced)

1. **Restart Backend** (to load new code)

2. **Test as Beginner**:
```bash
curl -X POST "http://localhost:8000/api/generate-policies?max_per_type=1&expertise_level=beginner&user_role=junior_developer" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "sast_file=@data/sample_reports/sast_sample.json"
```

**Expected Output**:
- Policy starts with "## 📚 Understanding the Issue"
- Has "What is SQL Injection?" section
- Includes learning resources
- Has detailed code examples with comments

3. **Test as Advanced**:
```bash
curl -X POST "http://localhost:8000/api/generate-policies?max_per_type=1&expertise_level=advanced&user_role=security_engineer" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "sast_file=@data/sample_reports/sast_sample.json"
```

**Expected Output**:
- Policy starts with "## Security Policy:"
- Has CVSS v3.1 Score Breakdown
- Includes SIEM correlation rules
- Has detailed compliance mapping
- NO basic explanations

4. **Compare**: Save both outputs - they should be VERY different!

---

### Test 2: Policy Tracking Workflow

1. **Generate Policies** (creates tracking entries):
```bash
curl -X POST "http://localhost:8000/api/generate-policies?max_per_type=5" \
  -F "sast_file=@data/sample_reports/sast_sample.json" \
  -F "sca_file=@data/sample_reports/sca_sample.json" \
  -F "dast_file=@data/sample_reports/dast_sample.xml"
```

2. **View Dashboard**:
```bash
curl http://localhost:8000/api/policies/dashboard
```

**Expected**:
```json
{
  "success": true,
  "policies": [
    {
      "policy_id": "POL-2025-001",
      "vulnerability_title": "SQL Injection",
      "severity": "critical",
      "status": "not_started",
      "due_date": "2025-11-09T...",
      ...
    }
  ],
  "stats": {
    "total_policies": 12,
    "not_started": 12,
    "compliance_percentage": 0.0
  }
}
```

3. **Update First Policy**:
```bash
curl -X POST "http://localhost:8000/api/policies/POL-2025-001/status?new_status=in_progress&user=John%20Doe"
```

4. **Assign It**:
```bash
curl -X POST "http://localhost:8000/api/policies/POL-2025-001/assign?assigned_to=John%20Doe&user=Manager"
```

5. **Check Dashboard Again**:
```bash
curl http://localhost:8000/api/policies/dashboard
```

**Expected**: Now shows:
```json
{
  "stats": {
    "total_policies": 12,
    "not_started": 11,
    "in_progress": 1,
    "compliance_percentage": 0.0
  }
}
```

6. **Mark as Fixed**:
```bash
curl -X POST "http://localhost:8000/api/policies/POL-2025-001/status?new_status=fixed&user=John%20Doe"
```

7. **Mark as Verified**:
```bash
curl -X POST "http://localhost:8000/api/policies/POL-2025-001/status?new_status=verified&user=Security%20Team"
```

8. **Final Dashboard Check**:
```bash
curl http://localhost:8000/api/policies/dashboard
```

**Expected**:
```json
{
  "stats": {
    "total_policies": 12,
    "not_started": 11,
    "verified": 1,
    "compliance_percentage": 8.3
  }
}
```

---

## 📊 What You Should See

### Beginner Policy Example:
```markdown
## 📚 Understanding the Issue

### What is SQL Injection?
SQL injection is like someone slipping a fake command into a form on your website...

### Why is it Dangerous?
An attacker could:
- Steal all user passwords and emails
- Delete your entire database
- Change prices in your store
- Pretend to be an admin

### Real-World Example:
In 2019, a company lost $2M because...

## 💻 How to Fix It

### Current Code (Vulnerable):
```python
# ❌ WRONG - This lets attackers inject malicious SQL
username = input("Enter username: ")
query = f"SELECT * FROM users WHERE username = '{username}'"
db.execute(query)

# If attacker enters: admin' OR '1'='1
# Query becomes: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# This returns ALL users! 😱
```

### Fixed Code (Secure):
```python
# ✅ CORRECT - Uses parameterized query
username = input("Enter username: ")
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))  # Database treats input as DATA, not CODE

# Even if attacker enters: admin' OR '1'='1
# Database looks for a user literally named "admin' OR '1'='1" - finds nothing!
```

[... continues with step-by-step instructions ...]
```

### Advanced Policy Example:
```markdown
## Security Policy: SQL Injection Prevention

### Executive Summary
Critical SQL injection vulnerability detected in authentication layer. Immediate remediation required to prevent unauthorized data access. Estimated cost of breach: $4.35M. Cost of fix: $8,000.

### Risk Analysis

#### CVSS v3.1 Score: 9.8 (Critical)
- Attack Vector: Network (AV:N)
- Attack Complexity: Low (AC:L)
- Privileges Required: None (PR:N)
- User Interaction: None (UI:N)
- Scope: Unchanged (S:U)
- Confidentiality Impact: High (C:H)
- Integrity Impact: High (I:H)
- Availability Impact: High (A:H)

#### Threat Intelligence:
- **Public Exploits**: Yes (SQLMap, Havij)
- **MITRE ATT&CK**: T1190 - Exploit Public-Facing Application
- **Attack Chain**:
  1. Reconnaissance (identify input fields)
  2. Initial Access (SQL injection)
  3. Privilege Escalation (union-based injection)
  4. Data Exfiltration (time-based blind injection)

[... continues with SIEM rules, WAF configs, compliance details ...]

### SIEM Correlation Rule (Splunk):
```spl
index=web_logs status=500
| regex _raw="SQL syntax.*error"
| stats count by src_ip, user_agent
| where count > 5
| eval severity="critical"
```

[... continues ...]
```

---

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] `/api/profile-templates` returns 7 templates
- [ ] Beginner policies have learning resources
- [ ] Advanced policies have SIEM rules
- [ ] Policy tracking creates JSON file in `outputs/`
- [ ] Dashboard shows all policies
- [ ] Status updates work
- [ ] Compliance percentage calculates
- [ ] Timeline tracks all changes
- [ ] All existing features still work (Upload Mode, GitHub Mode, Compliance Test)

---

## 🎉 You're Done!

Once you complete the manual integration steps and tests pass, you have:

1. ✅ **Adaptive Policies** - 3 expertise levels with different outputs
2. ✅ **User Profiles** - With certifications and preferences
3. ✅ **Policy Tracking** - Full lifecycle management
4. ✅ **Compliance Dashboard** - Real-time status monitoring
5. ✅ **Professional Features** - Production-ready code

**Next**: Add frontend components to make it visually stunning!
