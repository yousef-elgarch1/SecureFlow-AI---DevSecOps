# Implementation Plan: User Profiles & Policy Tracking

## Summary

We're adding 2 major features to make the platform more professional:

1. **Adaptive Policy Reports** - Personalized based on user expertise and certifications
2. **Policy Compliance Tracking** - Monitor which policies are implemented

---

## Feature 1: User Profile & Adaptive Policies

### What's Being Added

**User Profile includes**:
- Expertise Level: Beginner / Intermediate / Advanced
- Role: Junior Dev / Senior Dev / Security Engineer / DevOps / Manager / CISO
- Certifications: CISSP, CEH, Security+, OSCP, etc.
- Years of experience
- Preferences: Detail level, code examples, compliance focus

###Files Created**:
✅ `backend/models/user_profile.py` - User profile data model
✅ `backend/models/__init__.py` - Model exports

### Files to Modify:
- `backend/prompts/policy_templates.py` - Add adaptive prompts (3 levels × 3 types = 9 prompts)
- `backend/orchestrator/policy_generator.py` - Accept user_profile, select prompt
- `backend/api/main.py` - Add user_profile to API endpoints
- `frontend/src/components/UploadForm.jsx` - Add profile selection
- `frontend/src/components/GitHubRepoSelector.jsx` - Add profile selection

---

## Feature 2: Policy Compliance Tracking

### What's Being Added

**Policy Status Types**:
- Not Started ❌
- In Progress 🔄
- Under Review 🔍
- Fixed ✅
- Verified ✓✓
- Re-opened ⚠️ (regression detected)

**Dashboard Shows**:
- All generated policies in table
- Status, assigned to, due date, progress %
- Overall compliance percentage
- Timeline of status changes
- Filters by status/severity

### Files to Create:
- `backend/database/policy_tracker.py` - JSON storage for policy status
- `backend/models/policy_status.py` - Policy status data model
- `backend/api/tracking.py` - Policy tracking API endpoints
- `frontend/src/pages/ComplianceDashboard.jsx` - Dashboard page
- `frontend/src/components/PolicyStatusCard.jsx` - Status tracking card
- `frontend/src/components/PolicyTrackingTable.jsx` - Policy table

### Files to Modify:
- `backend/api/main.py` - Include tracking endpoints
- `frontend/src/App.jsx` - Add dashboard route
- `frontend/src/components/PolicyResultsDisplay.jsx` - Add "Track Status" button

---

## Implementation Order

### Phase 1: User Profiles (Day 1-2)
1. ✅ Create user profile model
2. Create 9 adaptive prompts (beginner/intermediate/advanced × SAST/SCA/DAST)
3. Modify orchestrator to use profiles
4. Add profile selection UI to frontend
5. Test with real data

### Phase 2: Policy Tracking (Day 3-4)
1. Create policy status model
2. Create JSON storage system
3. Create tracking API endpoints
4. Build compliance dashboard page
5. Add status tracking to results page
6. Test complete workflow

---

## Example: How Adaptive Prompts Work

### Beginner Prompt (Junior Developer):
```
Generate a security policy for a JUNIOR DEVELOPER with LIMITED security experience.

Requirements:
✓ Explain what SQL injection is in simple terms
✓ Provide before/after code examples with comments
✓ Include links to OWASP learning resources
✓ Use simple language, avoid jargon
✓ Explain WHY each step matters
✓ Add copy-paste code snippets

Format:
1. What is this vulnerability? (explain like I'm 5)
2. Why is it dangerous? (real-world example)
3. How to fix it? (code with comments)
4. How to test? (unit test examples)
5. Learn more: (OWASP links, tutorials)
```

### Advanced Prompt (Security Engineer):
```
Generate a security policy for a SECURITY ENGINEER with DEEP expertise.

Requirements:
✓ Detailed NIST CSF and ISO 27001 mapping with control descriptions
✓ CVSS v3.1 scoring and risk analysis
✓ Multiple remediation approaches with trade-offs
✓ Detection strategies (SIEM rules, WAF patterns, IDS signatures)
✓ Incident response procedures
✓ Threat modeling considerations
✓ Integration with security tools (SAST/DAST/SCA)

Skip: Basic vulnerability explanations (they know SQL injection)
```

---

## Example: Policy Tracking Workflow

1. **Generate Policies** → 10 policies created
2. **Navigate to Dashboard** → See all 10 policies with status "Not Started"
3. **Assign Policy** → Assign SQL injection fix to "John Doe"
4. **Update Status** → John marks as "In Progress"
5. **Complete Work** → John marks as "Fixed"
6. **Verify** → Security team marks as "Verified"
7. **Dashboard Updates** → 1/10 = 10% compliance
8. **Automatic Re-scan** (Optional) → Weekly scan checks if fix still in place

---

## Database Schema (JSON Files)

### `outputs/policy_tracking.json`:
```json
{
  "policies": [
    {
      "policy_id": "POL-2025-001",
      "vulnerability_title": "SQL Injection in login.py",
      "severity": "critical",
      "status": "in_progress",
      "assigned_to": "John Doe",
      "created_at": "2025-11-07T14:30:00",
      "updated_at": "2025-11-07T16:45:00",
      "due_date": "2025-11-09T14:30:00",
      "timeline": [
        {"event": "created", "timestamp": "2025-11-07T14:30:00", "user": "system"},
        {"event": "assigned", "timestamp": "2025-11-07T15:00:00", "user": "admin", "details": "Assigned to John Doe"},
        {"event": "status_changed", "timestamp": "2025-11-07T16:45:00", "user": "John Doe", "from": "not_started", "to": "in_progress"}
      ],
      "nist_csf_controls": ["PR.DS-5", "PR.AC-4"],
      "iso27001_controls": ["A.14.2.5", "A.8.22"]
    }
  ],
  "stats": {
    "total_policies": 10,
    "not_started": 5,
    "in_progress": 3,
    "fixed": 1,
    "verified": 1,
    "compliance_percentage": 20.0
  }
}
```

---

## API Endpoints to Add

### User Profile:
- `POST /api/user-profile` - Save user profile
- `GET /api/user-profile` - Get current profile
- `GET /api/profile-templates` - Get predefined templates

### Policy Tracking:
- `GET /api/policies/dashboard` - Get all policies with status
- `POST /api/policies/{id}/status` - Update policy status
- `POST /api/policies/{id}/assign` - Assign policy to user
- `GET /api/policies/{id}/timeline` - Get status change history
- `GET /api/policies/stats` - Get compliance statistics

---

## Frontend Routes to Add

- `/profile` - User profile setup page
- `/compliance-dashboard` - Policy tracking dashboard
- `/policy/{id}` - Individual policy detail page with timeline

---

## Testing Plan

### Test 1: Adaptive Prompts
1. Generate policies as "Beginner" → Check for explanations and learning links
2. Generate same policies as "Advanced" → Check for compliance details and SIEM rules
3. Compare outputs → Verify they're different

### Test 2: Policy Tracking
1. Generate 10 policies
2. Navigate to dashboard → See all 10 as "Not Started"
3. Assign 3 policies to team members
4. Update status to "In Progress"
5. Mark 1 as "Fixed"
6. Check dashboard shows 10% compliance
7. View timeline → See all status changes

---

## Success Criteria

✅ User can select expertise level before generating policies
✅ Generated policies adapt to user's level (visible difference in output)
✅ User profile includes certifications (CISSP, CEH, etc.)
✅ Dashboard shows all generated policies in organized table
✅ Can update policy status and assign to team members
✅ Timeline tracks all status changes
✅ Overall compliance percentage calculated correctly
✅ All existing features still work (Upload Mode, GitHub Mode, Compliance Test)
✅ No breaking changes to current functionality

---

## Time Estimate

- User Profiles: 2 days
- Policy Tracking: 2-3 days
- Testing & Polish: 1 day
- **Total: 5-6 days**

---

## Next Steps

1. Create adaptive prompts (9 templates)
2. Modify orchestrator to accept user profile
3. Add profile selection UI
4. Create policy tracking system
5. Build dashboard
6. Test everything

Ready to implement! 🚀
