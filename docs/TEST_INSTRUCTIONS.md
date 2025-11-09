# Testing the New GitHub Actions-Style Workflow

## What Changed

### NEW Features:
1. **Visual Workflow Graph** - 4 connected boxes showing the pipeline
2. **Click to Explore** - Click any step to see real-time logs
3. **Terminal-Style Logs** - Black console showing live updates
4. **Connected Steps** - Arrows showing flow between phases
5. **Auto-Updates** - Steps change color as they run (gray → blue → green)

## How to Test

### 1. Start Backend
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops
venv\Scripts\activate
uvicorn backend.api.main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops\frontend
npm run dev
```

### 3. Open Browser
Navigate to: http://localhost:3000

### 4. Upload Reports
Upload these 3 files:
- `docs/test_reports/mock_sast_report.json`
- `docs/test_reports/mock_sca_report.json`
- `docs/test_reports/mock_dast_report.xml`

### 5. Click "Generate Security Policies"

## What You Should See

### Workflow Graph (Top)
```
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│    1    │ ───> │    2    │ ───> │    3    │ ───> │    4    │
│ Parse   │      │  RAG    │      │   AI    │      │  Save   │
│ Reports │      │Retrieval│      │Generate │      │Results  │
│  [⏳]   │      │  [⏸️]   │      │  [⏸️]   │      │  [⏸️]   │
│ Running │      │ Waiting │      │ Waiting │      │ Waiting │
└─────────┘      └─────────┘      └─────────┘      └─────────┘
```

**Colors:**
- **Gray** = Waiting/Pending
- **Blue** (with spinner) = Currently Running
- **Green** (with checkmark) = Completed
- **Red** (with X) = Error

**Current Step:** Has a blue ring around it

### Terminal Logs (Bottom - When You Click a Step)
```
[14:30:45] IN_PROGRESS Parsing SAST report (Semgrep)...
    → Parser: SAST
    → 8 vulnerabilities found

[14:30:46] IN_PROGRESS Parsing SCA report (npm audit/Trivy)...
    → Parser: SCA
    → 10 vulnerabilities found

[14:30:47] IN_PROGRESS Parsing DAST report (OWASP ZAP)...
    → Parser: DAST
    → 8 vulnerabilities found

[14:30:48] COMPLETED Parsing complete - 26 total vulnerabilities found
```

### Real-Time Behavior

**Step 1 - Parsing (Auto-selected)**
- Box turns BLUE with spinner
- Terminal shows each parser running
- Arrow to Step 2 stays gray
- When done: Box turns GREEN with checkmark, arrow turns green

**Step 2 - RAG** (Click to select)
- Box turns BLUE
- Terminal shows NIST CSF retrieval
- Terminal shows ISO 27001 retrieval
- When done: Box GREEN, arrow green

**Step 3 - LLM Generation** (Click to select)
- Box BLUE
- Terminal shows each vulnerability:
  ```
  → Processing: SQL Injection [HIGH]
  → Model: LLaMA 3.3 70B
  → Progress: 3.8% (1/26)
  ```
- Updates in real-time for all 26 vulnerabilities
- When done: Box GREEN

**Step 4 - Saving** (Click to select)
- Box BLUE
- Terminal shows files being saved
- When done: Box GREEN

## Troubleshooting

### If Nothing Updates:

**Check Browser Console (F12)**
Look for:
```
Progress update: {phase: 'parsing', status: 'in_progress', ...}
```

If you see this, React is receiving updates ✅

**Check Updates Counter**
Bottom of page should show:
```
Updates received: 45 | Current phase: llm_generation
```

If counter increases, data is coming through ✅

### If Boxes Don't Change Color:

The status detection looks for:
- `status: 'in_progress'` → BLUE (running)
- `status: 'completed'` → GREEN (done)
- `status: 'error'` → RED (failed)
- No updates → GRAY (pending)

### If Logs Don't Show:

1. Make sure you **clicked a step box**
2. Check if `progress` array has data (see counter)
3. Open console and check for errors

## Expected Console Output

```javascript
Progress update: {
  phase: 'parsing',
  status: 'in_progress',
  message: 'Parsing SAST report (Semgrep)...',
  data: {
    current_parser: 'SAST',
    parser_status: 'running',
    file_name: 'mock_sast_report.json'
  }
}

Progress update: {
  phase: 'parsing',
  status: 'in_progress',
  message: 'SAST parsing complete - 8 vulnerabilities found',
  data: {
    current_parser: 'SAST',
    parser_status: 'completed',
    vulnerabilities_found: 8,
    sast_count: 8,
    vulnerabilities: [...]
  }
}

// ... many more updates ...

Updates received: 73
```

## What Makes This Different from Before?

### OLD (What wasn't working):
- Updates but nothing changed visually
- No clear workflow visualization
- Hard to see what's happening

### NEW (What's fixed):
- ✅ Visual workflow graph shows current step
- ✅ Steps change color in real-time
- ✅ Click step to see terminal logs
- ✅ Progress updates appear as they happen
- ✅ GitHub Actions-style connected boxes
- ✅ Auto-selects current step
- ✅ Shows data like parser names, vulnerability counts, LLM models

## Features Tested

- [ ] Workflow graph renders
- [ ] Step 1 starts as BLUE (running)
- [ ] Can click steps to select them
- [ ] Terminal logs appear when step selected
- [ ] Updates counter increases
- [ ] Current phase updates
- [ ] Steps turn GREEN when complete
- [ ] Arrows turn GREEN when step completes
- [ ] Statistics cards show (SAST: 8, SCA: 10, DAST: 8)
- [ ] All 4 steps eventually complete
- [ ] Can click between steps to see different logs

---

**If it still doesn't work, please:**
1. Screenshot the browser console (F12)
2. Screenshot the workflow view
3. Copy the "Updates received" count
4. Let me know and I'll debug further!
