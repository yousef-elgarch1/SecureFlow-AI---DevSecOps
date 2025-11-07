# Complete Setup Guide - AI Security Policy Generator with Frontend

This guide will help you set up and run the complete AI Security Policy Generator system with the professional React frontend.

## System Architecture

```
┌─────────────────────┐
│   React Frontend    │ (Port 3000)
│   - Upload UI       │
│   - Real-time View  │
│   - Results Charts  │
└──────────┬──────────┘
           │ HTTP/WebSocket
           ▼
┌─────────────────────┐
│   FastAPI Backend   │ (Port 8000)
│   - REST Endpoints  │
│   - WebSocket       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Python Backend     │
│  - Parsers          │
│  - RAG (ChromaDB)   │
│  - LLM (Groq)       │
│  - Orchestrator     │
└─────────────────────┘
```

## Prerequisites

### Required Software
- Python 3.9+
- Node.js 16+
- npm or yarn
- Git

### Required API Keys
- Groq API Key (get from https://console.groq.com)

## Part 1: Backend Setup

### Step 1: Clone and Navigate to Project
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops
```

### Step 2: Create and Activate Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Step 5: Initialize RAG Vector Database
```bash
# Create vector database from compliance documents
python -c "
from backend.rag.vector_store import ComplianceVectorStore
store = ComplianceVectorStore()
print('RAG vector database initialized!')
"
```

### Step 6: Start the FastAPI Backend
```bash
# Install uvicorn if not already installed
pip install uvicorn

# Start the backend API server
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Keep this terminal open and running!

## Part 2: Frontend Setup

### Step 1: Open New Terminal
Open a new terminal window (keep the backend running in the first terminal).

Navigate to the frontend directory:
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops\frontend
```

### Step 2: Install Node.js Dependencies
```bash
npm install
```

This will install:
- React 18
- Vite
- Tailwind CSS
- Recharts
- Lucide React
- Axios

### Step 3: Start the Frontend Development Server
```bash
npm run dev
```

You should see:
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### Step 4: Open in Browser
Open your browser and navigate to:
```
http://localhost:3000
```

## Part 3: Testing the Complete System

### Test 1: Backend Health Check
1. In the frontend, you should see "Backend Connected" indicator in green
2. If you see "Backend Offline", check:
   - Is the FastAPI server running?
   - Is it accessible at http://localhost:8000?
   - Check the backend terminal for errors

### Test 2: Upload and Generate Policies

#### Option 1: Use Existing Test Reports
If you have test reports in the project:
```bash
# Check for test reports
ls test_real_scans/
```

#### Option 2: Generate Test Reports from OWASP Juice Shop
```bash
# Clone Juice Shop
git clone https://github.com/juice-shop/juice-shop.git test-juice-shop

# Run SAST scan
semgrep --config=auto --json --output=sast_report.json test-juice-shop/

# Run SCA scan with Trivy
trivy fs --format json --scanners vuln --output sca_report.json test-juice-shop/
```

#### Upload Reports in Frontend
1. Click "Choose File" for each report type (SAST, SCA, DAST)
2. Or drag and drop files onto the upload areas
3. Click "Generate Security Policies"

### Test 3: Watch Real-Time Processing
You should see 4 phases in real-time:

1. **Phase 1: Parsing Reports**
   - Shows vulnerability counts for SAST, SCA, DAST

2. **Phase 2: RAG Retrieval**
   - Shows compliance contexts retrieved from vector DB

3. **Phase 3: AI Policy Generation**
   - Shows current vulnerability being processed
   - Displays which LLM model is being used
   - Progress bar showing X/Y vulnerabilities processed

4. **Phase 4: Saving Results**
   - Shows files saved (TXT, HTML, JSON)

### Test 4: View Results
After processing completes:
1. View statistics cards (total policies, severity distribution)
2. Explore interactive charts (bar chart, pie chart)
3. Expand individual policies to see:
   - Vulnerability details
   - Generated policy text
   - Compliance mappings (NIST CSF, ISO 27001)
   - BLEU-4 and ROUGE-L quality scores

### Test 5: Download Policies
Click the download buttons:
- **TXT**: Plain text policy file
- **HTML**: Formatted HTML report

## Part 4: GitHub Actions Integration

### Running the Complete Pipeline
The GitHub Actions workflow is already configured to run the complete pipeline.

To trigger it:
```bash
git add .
git commit -m "Add professional frontend with real-time updates"
git push origin main
```

The pipeline will:
1. Run SAST scan on OWASP Juice Shop
2. Run SCA scan with Trivy
3. Run DAST scan (sample data)
4. Parse all reports
5. Initialize RAG vector database
6. Generate policies with LLM
7. Evaluate policy quality
8. Upload artifacts (TXT and HTML policies)

## Troubleshooting

### Backend Issues

#### Port 8000 Already in Use
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uvicorn backend.api.main:app --reload --port 8001
```

#### Import Errors
```bash
# Ensure venv is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Groq API Errors
- Check your API key in `.env`
- Verify you have API credits at https://console.groq.com
- Check rate limits (wait and retry)

### Frontend Issues

#### Port 3000 Already in Use
Vite will automatically try the next available port (3001, 3002, etc.)

#### npm install Fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### WebSocket Connection Errors
- Ensure backend is running on port 8000
- Check browser console for detailed errors
- Verify CORS settings in backend allow localhost:3000

### Common Errors

#### "Backend Offline"
1. Check backend terminal - is it running?
2. Test: `curl http://localhost:8000/api/health`
3. Check firewall settings

#### "Failed to generate policies"
1. Check backend terminal for Python errors
2. Verify Groq API key is set
3. Ensure RAG vector database is initialized
4. Check uploaded files are valid JSON/XML

#### Charts Not Displaying
1. Check browser console for errors
2. Ensure recharts is installed: `npm list recharts`
3. Verify results data structure matches expected format

## Project File Structure

```
AI_Devsecops/
├── backend/
│   ├── api/
│   │   └── main.py                 # FastAPI server with WebSocket
│   ├── parsers/
│   │   ├── sast_parser.py
│   │   ├── sca_parser.py
│   │   └── dast_parser.py
│   ├── llm_integrations/
│   │   └── groq_client.py
│   ├── rag/
│   │   ├── vector_store.py
│   │   └── retriever.py
│   ├── orchestrator/
│   │   └── policy_generator.py
│   └── evaluation/
│       └── metrics.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadMode.jsx
│   │   │   ├── RealTimeDashboard.jsx
│   │   │   ├── ResultsView.jsx
│   │   │   └── StatsCard.jsx
│   │   ├── utils/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── .github/
│   └── workflows/
│       └── devsecops-pipeline.yml
├── requirements.txt
├── .env
└── README.md
```

## Next Steps

1. **Customize Prompts**: Edit `backend/prompts/policy_templates.py`
2. **Add More Compliance Standards**: Add documents to `backend/rag/compliance_docs/`
3. **Adjust LLM Routing**: Modify `backend/orchestrator/policy_generator.py`
4. **Style Frontend**: Customize `frontend/tailwind.config.js`
5. **Add GitHub Scanner**: Implement repository scanning feature
6. **Deploy to Production**: Set up Docker containers

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review component READMEs in `frontend/` and `backend/`
3. Check GitHub Actions logs for pipeline issues
4. Review browser console for frontend errors
5. Check backend terminal for API errors
