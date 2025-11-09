# WebSocket Fix Testing Guide

## Problem Identified

The **root cause** was that the frontend was using the HTTP POST endpoint (`/api/generate-policies`) which didn't send any WebSocket messages. The WebSocket endpoint existed but was never used during the policy generation process.

## Solution Implemented

1. **Added `broadcast_progress()` function** to send messages to ALL connected WebSocket clients
2. **Created `broadcast_realtime_generation()` function** that broadcasts progress during policy generation
3. **Modified `/api/generate-policies` endpoint** to call `broadcast_realtime_generation()`
4. **Updated WebSocket endpoint** to simply maintain connections (no action handling needed)

## How It Works Now

```
Frontend                    Backend
   |                           |
   |--- Connect WebSocket ---> |  (Connection stored in active_connections[])
   |                           |
   |--- POST /generate----- -> |  (Upload files)
   |                           |
   |                           |-- Parse files
   |                           |
   |<-- WebSocket Update ------| broadcast_progress() to ALL clients
   |                           |
   |<-- WebSocket Update ------| (Real-time parsing updates)
   |                           |
   |<-- WebSocket Update ------| (RAG retrieval updates)
   |                           |
   |<-- WebSocket Update ------| (LLM generation progress)
   |                           |
   |<-- WebSocket Update ------| (Saving results)
   |                           |
   |<-- HTTP 200 Response -----|
```

## Testing Steps

### 1. Start Backend
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops
venv\Scripts\activate
uvicorn backend.api.main:app --reload --port 8000
```

**Expected Output:**
```
✅ Orchestrator initialized successfully
✅ RAG system: Enabled
✅ LLM clients: {...}
INFO:     Application startup complete.
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Open Browser Console
- Open: http://localhost:3000
- Press F12 to open Developer Console
- Go to "Console" tab

### 4. Upload Reports
- Upload the 3 test reports
- Click "Generate Security Policies"

### 5. What You Should See

**Backend Console:**
```
✅ WebSocket client connected. Total connections: 1
INFO:     127.0.0.1:xxxxx - "POST /api/generate-policies HTTP/1.1" 200 OK
❌ WebSocket client disconnected. Remaining connections: 0
```

**Frontend Console:**
```
WebSocket connected
WebSocket message: {phase: 'parsing', status: 'in_progress', message: 'Starting...'}
WebSocket message: {phase: 'parsing', status: 'in_progress', message: 'Parsing SAST...'}
WebSocket message: {phase: 'parsing', status: 'in_progress', message: 'SAST complete - 8 vulnerabilities'}
WebSocket message: {phase: 'parsing', status: 'in_progress', message: 'Parsing SCA...'}
WebSocket message: {phase: 'rag', status: 'in_progress', message: 'Retrieving...'}
WebSocket message: {phase: 'llm_generation', status: 'in_progress', message: 'Generating...'}
...
```

**Workflow UI:**
- Step 1 (Parse Reports) should turn BLUE immediately
- Terminal should show real-time logs
- Step 1 turns GREEN when parsing completes
- Step 2 (RAG Retrieval) turns BLUE
- Step 2 turns GREEN when RAG completes
- Step 3 (AI Generation) turns BLUE
- Terminal shows each vulnerability being processed
- Step 3 turns GREEN when all policies generated
- Step 4 (Save Results) turns BLUE then GREEN
- Updates counter increases with each message

## Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to WebSocket (check console)
- [ ] Backend shows "WebSocket client connected"
- [ ] Step 1 turns blue when generation starts
- [ ] Terminal logs appear when clicking Step 1
- [ ] Updates counter increases (bottom of workflow view)
- [ ] Steps change color in real-time (gray → blue → green)
- [ ] Terminal shows detailed logs (parser names, vulnerability counts)
- [ ] All 4 steps complete successfully
- [ ] Statistics cards appear with vulnerability counts

## Troubleshooting

### Issue: No WebSocket messages in console
**Solution:** Check that WebSocket connects BEFORE clicking "Generate"
- Look for "WebSocket connected" in console
- If missing, refresh page and wait 2 seconds before clicking Generate

### Issue: Steps stay gray
**Solution:** Check backend console for errors
- Look for "WebSocket client connected" message
- If missing, check CORS settings in backend

### Issue: "Updates received: 0"
**Solution:** The broadcast function isn't being called
- Check backend logs for exceptions
- Verify `broadcast_realtime_generation()` is being called

## Expected Real-Time Behavior

### Phase 1: Parsing (5-10 seconds)
- Step 1 turns blue with spinner
- Terminal shows:
  ```
  [HH:MM:SS] IN_PROGRESS Starting vulnerability report parsing...
  [HH:MM:SS] IN_PROGRESS Parsing SAST report (Semgrep)...
    → Parser: SAST
    → 8 vulnerabilities found
  [HH:MM:SS] IN_PROGRESS Parsing SCA report (npm audit/Trivy)...
    → Parser: SCA
    → 10 vulnerabilities found
  [HH:MM:SS] COMPLETED Parsing complete - 26 total vulnerabilities
  ```
- Statistics cards appear showing SAST: 8, SCA: 10, DAST: 8
- Step 1 turns green with checkmark
- Arrow 1→2 turns green

### Phase 2: RAG Retrieval (2-3 seconds)
- Step 2 turns blue with spinner
- Terminal shows:
  ```
  [HH:MM:SS] IN_PROGRESS Retrieving compliance contexts...
  [HH:MM:SS] IN_PROGRESS Fetching NIST CSF compliance contexts...
  [HH:MM:SS] IN_PROGRESS NIST CSF contexts retrieved successfully
    → Retrieved: 15 compliance contexts
  [HH:MM:SS] COMPLETED All compliance contexts retrieved
  ```
- Step 2 turns green
- Arrow 2→3 turns green

### Phase 3: LLM Generation (30-60 seconds)
- Step 3 turns blue with spinner
- Terminal shows EACH vulnerability:
  ```
  [HH:MM:SS] IN_PROGRESS Starting AI policy generation for 15 vulnerabilities
    → Model: LLaMA 3.3 70B
  [HH:MM:SS] IN_PROGRESS Generating policy for Node Sqli...
    → Processing: Node Sqli [HIGH]
    → Model: LLaMA 3.3 70B
    → Progress: 6.7% (1/15)
  [HH:MM:SS] IN_PROGRESS Policy generated for Node Sqli
  ...
  [HH:MM:SS] COMPLETED All 15 policies generated successfully
  ```
- Step 3 turns green
- Arrow 3→4 turns green

### Phase 4: Saving (1-2 seconds)
- Step 4 turns blue with spinner
- Terminal shows:
  ```
  [HH:MM:SS] IN_PROGRESS Saving policy documents...
  [HH:MM:SS] COMPLETED All files saved successfully
  ```
- Step 4 turns green

## Key Changes Made

### File: `backend/api/main.py`

1. **Added broadcast function** (line 60-72):
```python
async def broadcast_progress(data: Dict):
    """Broadcast progress update to all connected WebSocket clients"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            disconnected.append(connection)
    for connection in disconnected:
        active_connections.remove(connection)
```

2. **Updated generate_policies endpoint** (line 132-138):
```python
# Broadcast real-time updates via WebSocket
await broadcast_realtime_generation(
    temp_files.get('sast'),
    temp_files.get('sca'),
    temp_files.get('dast'),
    max_per_type
)
```

3. **Renamed and updated generation function** (line 191):
```python
async def broadcast_realtime_generation(...):
    # All websocket.send_json() replaced with broadcast_progress()
```

4. **Simplified WebSocket endpoint** (line 166-189):
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Just maintains connection, broadcasts happen from HTTP endpoint
```

## Success Indicators

✅ Backend console shows "WebSocket client connected"
✅ Frontend console shows "WebSocket message: ..." repeatedly
✅ Workflow boxes change color in real-time
✅ Terminal logs update as you watch
✅ Updates counter increases from 0 to ~50+
✅ All 4 steps turn green
✅ Processing completes successfully

If ALL of the above happen, the fix is working correctly!
