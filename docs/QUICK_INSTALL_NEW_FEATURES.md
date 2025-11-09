# Quick Installation Guide for New Features

## 🚀 Install New Dependencies

### Step 1: Install Python Packages
```bash
cd c:\Users\lenovo\OneDrive\Bureau\GL_Projects\3A_GL\AI_Devsecops

# Install new dependencies
pip install PyPDF2==3.0.1 matplotlib==3.8.2 Pillow==10.2.0
```

### Step 2: Verify Installation
```bash
# Test PDF parser
python -c "import PyPDF2; print('PyPDF2:', PyPDF2.__version__)"

# Test matplotlib
python -c "import matplotlib; print('matplotlib:', matplotlib.__version__)"

# Test Pillow
python -c "import PIL; print('Pillow:', PIL.__version__)"
```

---

## ✅ Test the New Features

### Test 1: Enhanced PDF Reports

1. Start the backend:
```bash
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Generate policies and download PDF
   - Should contain colorful charts
   - Should have metrics tables
   - Should have professional layout

### Test 2: Compliance Test Feature

1. Open SecurAI in browser: `http://localhost:3000`

2. Generate policies (upload reports or scan GitHub)

3. Scroll to "Compliance Test" section

4. Upload a PDF file (can use the generated PDF or any security policy PDF)

5. View comparison results:
   - Grade (A-F)
   - BLEU-4 score
   - ROUGE-L score
   - Key terms coverage
   - Detailed report

---

## 📝 Create Test PDF (Optional)

If you need a test PDF for comparison, create this file:

**File: test_policy.txt**
```text
SECURITY POLICY FOR SQL INJECTION PREVENTION

Executive Summary:
This policy addresses SQL injection vulnerabilities through secure coding practices.

Risk Assessment:
SQL injection attacks can lead to data breaches and unauthorized access.

Security Controls:
- Use parameterized queries with prepared statements
- Implement input validation and sanitization
- Apply principle of least privilege
- Enable security monitoring and logging

Implementation:
All developers must use parameterized queries. Code reviews required.

Compliance:
Maps to NIST CSF PR.AC-4 and ISO 27001 A.14.2.5.

Monitoring:
Security team monitors for SQL injection using WAF.
```

Then convert to PDF:
- Open in Microsoft Word
- Save As → PDF
- Upload this PDF in Compliance Test

---

## 🎯 Expected Results

### PDF Report Should Contain:
- ✅ Executive summary table
- ✅ Severity distribution bar chart (colorful)
- ✅ Scan type pie chart
- ✅ Compliance coverage chart
- ✅ Quality metrics table
- ✅ Individual policies with styling

### Compliance Test Should Show:
- ✅ Drag-and-drop upload area
- ✅ Loading animation during processing
- ✅ Grade card with color coding
- ✅ Three metric cards (BLEU, ROUGE, Key Terms)
- ✅ Document statistics comparison
- ✅ Detailed text report

### HTML Report Should Contain:
- ✅ Quality Metrics section (pink/red gradient)
- ✅ Compliance Coverage section (purple gradient)
- ✅ Tips to use compliance test feature

---

## 🐛 Common Issues

### Issue: "Module not found: PyPDF2"
```bash
pip install PyPDF2==3.0.1
```

### Issue: "No module named 'matplotlib'"
```bash
pip install matplotlib==3.8.2 Pillow==10.2.0
```

### Issue: Charts not appearing in PDF
```bash
# Reinstall matplotlib with specific backend
pip uninstall matplotlib
pip install matplotlib==3.8.2 --no-cache-dir
```

### Issue: PDF extraction fails
```bash
# Try alternative PDF library
pip install pdfplumber==0.10.3
```

---

## 📸 Screenshots to Collect

For your presentation, take screenshots of:

1. ✅ Compliance Test upload interface
2. ✅ Comparison results with Grade A
3. ✅ BLEU-4 and ROUGE-L metric cards
4. ✅ PDF report with charts visible
5. ✅ HTML report quality metrics section
6. ✅ Detailed comparison report text

---

## ✨ Demo Flow for Teacher

1. **Show Original Problem**
   - "Teacher asked us to add policy comparison feature"
   - "Also wanted enhanced reports with visualizations"

2. **Show PDF Upload**
   - Drag and drop manual policy PDF
   - "System extracts text automatically"

3. **Show Metrics**
   - "BLEU-4 measures text similarity using n-grams"
   - "ROUGE-L measures content overlap"
   - "We get Grade B with 82% similarity"

4. **Show Enhanced PDF**
   - "Professional charts showing severity distribution"
   - "Compliance coverage visualization"
   - "Metrics tables with BLEU and ROUGE scores"

5. **Explain Academic Value**
   - "Uses industry-standard NLP metrics"
   - "Quantifiable evaluation"
   - "Meets research requirements"

---

**Ready to Test!** 🎉

All features are implemented and ready for testing.
