# 🧪 Quick Testing Guide - Compliance Features

## 🚀 Start the System

### Terminal 1 - Backend
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops
venv\Scripts\activate
uvicorn backend.api.main:app --reload --port 8000
```

**Expected:** Server starts on http://127.0.0.1:8000

### Terminal 2 - Frontend
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops\frontend
npm run dev
```

**Expected:** Dev server starts on http://localhost:3000

---

## ✅ Testing Checklist

### Step 1: Upload Files
- [ ] Open http://localhost:3000
- [ ] Backend shows "Backend Connected" (green dot)
- [ ] Upload `docs/test_reports/mock_sast_report.json`
- [ ] Upload `docs/test_reports/mock_sca_report.json`
- [ ] Upload `docs/test_reports/mock_dast_report.xml`
- [ ] Click "Generate Security Policies"

### Step 2: Watch Workflow (NEW!)
- [ ] Step 1 (Parse Reports) turns blue → green
- [ ] Step 2 (RAG Retrieval) turns blue → green
- [ ] Step 3 (AI Generation) turns blue → green
- [ ] Step 4 (Save Results) turns blue → green
- [ ] ✨ **Step 5 (Compliance Check) turns blue → green** ✨ **NEW!**

**Click Step 5 to see terminal logs:**
```
[HH:MM:SS] IN_PROGRESS Analyzing compliance coverage...
[HH:MM:SS] COMPLETED Compliance validation complete
    → NIST CSF: XX.X% coverage
    → ISO 27001: XX.X% coverage
    → Overall Score: XX.X%
```

### Step 3: Compliance Coverage Analysis (NEW!)
Scroll down to see **large colored header** with shield icon:

- [ ] Overall Score displayed (e.g., "68.7%")
- [ ] Letter grade shown (A/B/C/D/F)
- [ ] Progress bar animated
- [ ] **NIST CSF Section**:
  - [ ] Shows coverage percentage
  - [ ] Lists 5 functions (Identify, Protect, Detect, Respond, Recover)
  - [ ] Each function has mini progress bar
  - [ ] Green badges for covered controls
  - [ ] Red badges for gaps
- [ ] **ISO 27001 Section**:
  - [ ] Shows coverage percentage
  - [ ] Grid of 14 domains (A.5 through A.18)
  - [ ] Each domain shows percentage
  - [ ] Green badges for covered controls
  - [ ] Red badges for gaps
- [ ] **Recommendations Section**: Shows actionable suggestions

### Step 4: Compliance Checklist (NEW!)
Scroll further to see **purple header** with shield icon:

- [ ] Filter buttons visible: "All Controls", "Covered", "Gaps"
- [ ] Click "All Controls" - shows everything
- [ ] Click "Covered" - shows only green checkmarks
- [ ] Click "Gaps" - shows only red X marks
- [ ] **NIST CSF Checklist**:
  - [ ] Click "ID" (Identify) category - expands to show controls
  - [ ] Each control has ✓ or ✗ icon
  - [ ] Click any control with ✓ - shows which policies address it
  - [ ] Progress bar per function
- [ ] **ISO 27001 Checklist**:
  - [ ] Click "A.9" domain - expands to show controls
  - [ ] Each control has ✓ or ✗ icon
  - [ ] Click any control - shows policy details
  - [ ] Progress bar per domain

### Step 5: Check Console (Debug)

**Browser Console (F12):**
```
WebSocket message: {phase: 'compliance_validation', status: 'in_progress', ...}
WebSocket message: {phase: 'compliance_validation', status: 'completed', data: {...}}
```

**Backend Terminal:**
```
✅ Compliance validation complete
   NIST CSF: 75.0%
   ISO 27001: 62.3%
   Overall: 68.7%
```

---

## 🐛 Common Issues & Fixes

### Issue 1: Step 5 doesn't appear
**Fix:** Refresh page, try again. Check backend console for errors.

### Issue 2: Compliance sections are empty
**Fix:** Check browser console. Verify `results.compliance_analysis` exists in data.

### Issue 3: Colors not showing correctly
**Fix:** Clear browser cache, restart frontend dev server.

### Issue 4: Checklist won't expand
**Fix:** Click directly on category name or chevron icon.

---

## ✨ What's New?

### 1. Workflow Step 5 (5th Box)
```
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌──────────┐
│  1  │→ │  2  │→ │  3  │→ │  4  │→ │    5     │
│Parse│  │ RAG │  │ AI  │  │Save │  │Compliance│
│  ✓  │  │  ✓  │  │  ✓  │  │  ✓  │  │    ✓     │
└─────┘  └─────┘  └─────┘  └─────┘  └──────────┘
```

### 2. Compliance Coverage Analysis
- Overall score with color-coded design
- NIST CSF breakdown (5 functions)
- ISO 27001 breakdown (14 domains)
- Lists of covered controls & gaps
- Dynamic recommendations

### 3. Compliance Checklist
- Interactive expandable categories
- Filter by All/Covered/Gaps
- Click controls to see which policies address them
- Progress bars per category
- 222 total controls (108 NIST + 114 ISO)

---

## 📊 Expected Results

### Coverage Scores (Approximate)
- **Overall**: 50-70% (Satisfactory to Good)
- **NIST CSF**: 60-80%
  - Identify: 60-80%
  - Protect: 70-85%
  - Detect: 70-85%
  - Respond: 30-50% (lower - incident response not in mock data)
  - Recover: 30-50% (lower - recovery not in mock data)
- **ISO 27001**: 40-60%
  - A.9 (Access): 60-80%
  - A.12 (Operations): 70-85%
  - A.14 (Development): 85-95% (highest)
  - A.16 (Incidents): 20-40% (lower)
  - A.17 (Continuity): 20-40% (lower)

### Controls Covered (Approximate)
- **Total**: 100-140 out of 222 controls
- **Covered**: ~50-60%
- **Gaps**: ~40-50%

---

## 🎯 Success Indicators

### ✅ Everything Works If:
1. Step 5 appears in workflow and completes
2. Compliance Coverage Analysis section displays
3. Overall score is 40-80%
4. NIST CSF shows 5 functions with percentages
5. ISO 27001 shows 14 domains with percentages
6. Checklist displays all 222 controls
7. Filters work (All/Covered/Gaps)
8. Categories expand/collapse
9. Clicking controls shows policy details
10. No errors in console

### ❌ Something's Wrong If:
- Step 5 never appears
- Compliance sections are empty
- Scores show 0%
- Checklist shows 0 controls
- Console has errors
- Backend shows Python errors

---

## 📞 If Issues Occur

### Check These:
1. **Backend running?** Should show "Backend Connected" green dot
2. **Frontend running?** Should be on http://localhost:3000
3. **Files uploaded?** All 3 files should show in upload area
4. **WebSocket connected?** Check browser console for "WebSocket connected"
5. **Policies generated?** Should see "Policy generation complete!" message

### Restart If Needed:
```bash
# Stop both servers (Ctrl+C)
# Restart backend
uvicorn backend.api.main:app --reload --port 8000

# Restart frontend
cd frontend && npm run dev

# Refresh browser (Ctrl+Shift+R - hard refresh)
```

---

## 📸 Screenshots to Verify

### 1. Workflow with Step 5
All 5 boxes should be visible, connected with arrows

### 2. Compliance Coverage Analysis
Large colored header + overall score + NIST/ISO sections

### 3. Compliance Checklist
Purple header + filter buttons + expandable categories

---

## ⏭️ After Testing

### If Everything Works:
✅ All compliance features are working perfectly!
✅ Ready to proceed to GitHub OAuth integration (if desired)

### If Something Doesn't Work:
❌ Take screenshots of:
1. Browser console errors
2. Backend terminal errors
3. What's displayed on screen
4. Which step fails

Then I can help debug!

---

**Testing Time:** ~10-15 minutes
**What You're Testing:** 3 new compliance features + real-time updates
**Expected Result:** Beautiful compliance analysis with interactive checklist
