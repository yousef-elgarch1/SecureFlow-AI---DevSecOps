# COMPLETE IMPLEMENTATION TASKS - PLAN B (Cloud APIs)

This document contains all detailed tasks to fully implement the AI-Driven Security Policy Generator.

---

## PHASE 0: Setup (Days 1-2)

### Task 0.1: Environment Setup ⚙️

**Subtasks:**
1. Create virtual environment
   ```bash
   cd AI_Devsecops
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```

3. Create `.env` file
   ```bash
   copy .env.example .env
   # Edit .env and add your API keys
   ```

4. Get API Keys:
   - **Groq**: Sign up at https://console.groq.com → Get API key
   - **DeepSeek**: Sign up at https://platform.deepseek.com → Get API key
   - **OpenAI**: Sign up at https://platform.openai.com → Get API key

5. Test API connections:
   ```bash
   python -c "from groq import Groq; print('Groq OK')"
   python -c "import openai; print('OpenAI OK')"
   ```

**Expected Output:** All imports successful, no errors

**Time Estimate:** 1 hour

---

### Task 0.2: Download Sample Reports 📊

**Option A: Use Pre-made Samples (Faster)**

Create sample files manually based on realistic formats:

1. **SAST Report** (`data/sample_reports/sast_sample.json`):
   - Download NodeGoat: https://github.com/OWASP/NodeGoat
   - Install Semgrep: `pip install semgrep`
   - Run: `semgrep --config=auto --json . > data/sample_reports/sast_sample.json`

2. **SCA Report** (`data/sample_reports/sca_sample.json`):
   - In NodeGoat directory: `npm audit --json > data/sample_reports/sca_sample.json`

3. **DAST Report** (`data/sample_reports/dast_sample.xml`):
   - Download OWASP ZAP: https://www.zaproxy.org/download/
   - Scan localhost application
   - Export as XML to `data/sample_reports/dast_sample.xml`

**Option B: Use Minimal Mock Data** (if tools fail)

I can provide you with minimal but realistic sample reports if needed.

**Time Estimate:** 2-3 hours (or 30 min with mock data)

---

### Task 0.3: Download Compliance Documents 📚

**Subtasks:**

1. **NIST Cybersecurity Framework**
   - URL: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
   - Download to: `data/compliance_docs/nist_csf.pdf`

2. **ISO 27001 Annex A** (Alternative sources):
   - Option 1: Purchase from https://www.iso.org/standard/27001
   - Option 2: Use free summary: https://www.isms.online/iso-27001/annex-a/
   - Option 3: Create text file with all 93 controls listed

3. Create `data/compliance_docs/iso27001_annexa.txt` with structure:
   ```
   A.5.1 Policies for information security
   Management direction for information security
   ...

   A.8.1 User endpoint devices
   Information on user endpoint devices
   ...
   ```

**Time Estimate:** 1-2 hours

---

## PHASE 1: Build Parsers & LLM Integration (Days 3-5)

### Task 1.1: Build SAST Parser 🔍

**File:** `backend/parsers/sast_parser.py`

**Requirements:**
- Parse JSON from Semgrep/SonarQube
- Extract: vulnerability type, severity, file path, line number, CWE, description
- Normalize severity to: CRITICAL, HIGH, MEDIUM, LOW
- Group by category (Injection, XSS, etc.)

**Implementation Steps:**

1. Define data structures:
```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SASTVulnerability:
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # SQL Injection, XSS, etc.
    file_path: str
    line_number: int
    cwe_id: Optional[str]
    description: str
    recommendation: str
```

2. Implement parser class:
```python
class SASTParser:
    def parse(self, report_content: str) -> List[SASTVulnerability]:
        # Parse JSON
        # Extract vulnerabilities
        # Normalize data
        # Return structured list
```

3. Handle different SAST tool formats:
   - Semgrep: `results` array
   - SonarQube: `issues` array
   - Auto-detect format

4. Add error handling:
   - Malformed JSON
   - Missing required fields
   - Empty reports

5. Create summary statistics:
   - Count by severity
   - Count by category
   - Most affected files

**Test:**
```python
parser = SASTParser()
vulns = parser.parse(open('data/sample_reports/sast_sample.json').read())
print(f"Found {len(vulns)} vulnerabilities")
print(f"Critical: {len([v for v in vulns if v.severity == 'CRITICAL'])}")
```

**Time Estimate:** 4-5 hours

---

### Task 1.2: Build SCA Parser 📦

**File:** `backend/parsers/sca_parser.py`

**Requirements:**
- Parse JSON from npm audit/pip-audit
- Extract: package name, version, CVE, severity, fix available
- Handle nested dependencies

**Implementation Steps:**

1. Define data structures:
```python
@dataclass
class SCAVulnerability:
    package_name: str
    current_version: str
    vulnerable_versions: str
    patched_version: Optional[str]
    cve_id: str
    severity: str
    description: str
    exploitability: Optional[str]
```

2. Implement parser:
```python
class SCAParser:
    def parse(self, report_content: str) -> List[SCAVulnerability]:
        # Parse npm audit JSON format
        # Extract advisories
        # Map to vulnerability objects
```

3. Handle npm audit specific format:
   - `vulnerabilities` object
   - Nested dependency chains
   - Fix recommendations

**Test:**
```python
parser = SCAParser()
vulns = parser.parse(open('data/sample_reports/sca_sample.json').read())
print(f"Found {len(vulns)} vulnerable dependencies")
```

**Time Estimate:** 3-4 hours

---

### Task 1.3: Build DAST Parser 🌐

**File:** `backend/parsers/dast_parser.py`

**Requirements:**
- Parse XML from OWASP ZAP
- Extract: URL, issue type, risk level, description, solution
- Handle different alert types

**Implementation Steps:**

1. Define data structures:
```python
@dataclass
class DASTVulnerability:
    url: str
    endpoint: str
    method: str  # GET, POST, etc.
    issue_type: str  # SQL Injection, XSS, etc.
    risk_level: str
    confidence: str
    description: str
    solution: str
    cwe_id: Optional[str]
```

2. Implement XML parser:
```python
from bs4 import BeautifulSoup

class DASTParser:
    def parse(self, report_content: str) -> List[DASTVulnerability]:
        # Parse XML with BeautifulSoup
        # Extract alerts
        # Map to vulnerability objects
```

3. Handle ZAP report structure:
   - `<site>` → `<alerts>` → `<alertitem>`
   - Multiple instances per alert
   - Risk codes to severity mapping

**Test:**
```python
parser = DASTParser()
vulns = parser.parse(open('data/sample_reports/dast_sample.xml').read())
print(f"Found {len(vulns)} runtime issues")
```

**Time Estimate:** 3-4 hours

---

### Task 1.4: Build LLM Clients 🤖

#### Subtask 1.4.1: Groq Client

**File:** `backend/llm_integrations/groq_client.py`

**Implementation:**

```python
from groq import Groq
import os
from typing import Optional

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def generate(self, prompt: str, temperature: float = 0.3,
                 max_tokens: int = 2000) -> str:
        """Generate text using Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional security policy writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            raise
```

**Test:**
```python
client = GroqClient()
result = client.generate("Write a 2-sentence security policy about SQL injection.")
print(result)
```

**Time Estimate:** 1 hour

---

#### Subtask 1.4.2: DeepSeek Client

**File:** `backend/llm_integrations/deepseek_client.py`

**Implementation:**

```python
import requests
import os

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"

    def generate(self, prompt: str, temperature: float = 0.3,
                 max_tokens: int = 2000) -> str:
        """Generate text using DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a security policy expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"DeepSeek API Error: {response.text}")
```

**Test:**
```python
client = DeepSeekClient()
result = client.generate("Explain runtime security in 2 sentences.")
print(result)
```

**Time Estimate:** 1 hour

---

#### Subtask 1.4.3: OpenAI Client

**File:** `backend/llm_integrations/openai_client.py`

**Implementation:**

```python
from openai import OpenAI
import os

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def generate(self, prompt: str, temperature: float = 0.3,
                 max_tokens: int = 4000) -> str:
        """Generate text using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert security policy writer specializing in compliance frameworks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            raise
```

**Test:**
```python
client = OpenAIClient()
result = client.generate("Write an executive summary about cybersecurity.")
print(result)
```

**Time Estimate:** 30 minutes

---

#### Subtask 1.4.4: LLM Factory

**File:** `backend/llm_integrations/llm_factory.py`

**Implementation:**

```python
from typing import Literal
from .groq_client import GroqClient
from .deepseek_client import DeepSeekClient
from .openai_client import OpenAIClient

LLMProvider = Literal["groq", "deepseek", "openai"]

class LLMFactory:
    @staticmethod
    def get_client(provider: LLMProvider):
        """Factory method to get LLM client"""
        if provider == "groq":
            return GroqClient()
        elif provider == "deepseek":
            return DeepSeekClient()
        elif provider == "openai":
            return OpenAIClient()
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

**Test:**
```python
factory = LLMFactory()
groq = factory.get_client("groq")
openai = factory.get_client("openai")
```

**Time Estimate:** 30 minutes

---

## PHASE 2: Build RAG System (Days 6-8)

### Task 2.1: Document Loader 📄

**File:** `backend/rag/document_loader.py`

**Implementation:**

```python
import pypdf
from typing import List, Dict
import os

class DocumentLoader:
    def load_nist_csf(self, pdf_path: str) -> List[Dict]:
        """Load and chunk NIST CSF document"""
        chunks = []

        # Read PDF
        with open(pdf_path, 'rb') as f:
            pdf = pypdf.PdfReader(f)

            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()

                # Extract functions and categories
                # Split into meaningful chunks
                chunks.append({
                    "text": text,
                    "source": "NIST CSF",
                    "page": page_num + 1
                })

        return chunks

    def load_iso27001(self, txt_path: str) -> List[Dict]:
        """Load ISO 27001 Annex A controls"""
        chunks = []

        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Split by control (e.g., "A.5.1", "A.8.2", etc.)
            controls = self._parse_iso_controls(content)

            for control in controls:
                chunks.append({
                    "text": control["description"],
                    "source": "ISO 27001",
                    "control_id": control["id"],
                    "control_name": control["name"]
                })

        return chunks

    def _parse_iso_controls(self, content: str) -> List[Dict]:
        """Parse ISO 27001 controls from text"""
        # Implementation depends on your text format
        # Return list of {id, name, description}
        pass
```

**Time Estimate:** 3-4 hours

---

### Task 2.2: Vector Store Setup 🗄️

**File:** `backend/rag/vector_store.py`

**Implementation:**

```python
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import os

class VectorStore:
    def __init__(self, persist_directory: str = "./vector_db"):
        """Initialize ChromaDB"""
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Use sentence transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="compliance_docs",
            embedding_function=self.embedding_fn,
            metadata={"description": "NIST CSF and ISO 27001 compliance documents"}
        )

    def add_documents(self, documents: List[Dict]) -> None:
        """Add documents to vector store"""
        texts = [doc["text"] for doc in documents]
        metadatas = [{k: v for k, v in doc.items() if k != "text"} for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(documents)} documents to vector store")

    def search(self, query: str, top_k: int = 10) -> Dict:
        """Search for relevant documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }

    def reset(self) -> None:
        """Clear all documents"""
        self.client.delete_collection("compliance_docs")
        print("Vector store cleared")
```

**Time Estimate:** 2-3 hours

---

### Task 2.3: Initialize Vector Database 🚀

**File:** `backend/rag/init_vectordb.py` (Helper script)

**Implementation:**

```python
from document_loader import DocumentLoader
from vector_store import VectorStore
import os

def initialize_database():
    """Initialize vector database with compliance documents"""

    # Load documents
    loader = DocumentLoader()

    nist_path = "data/compliance_docs/nist_csf.pdf"
    iso_path = "data/compliance_docs/iso27001_annexa.txt"

    print("Loading NIST CSF...")
    nist_chunks = loader.load_nist_csf(nist_path)

    print("Loading ISO 27001...")
    iso_chunks = loader.load_iso27001(iso_path)

    all_docs = nist_chunks + iso_chunks
    print(f"Total chunks: {len(all_docs)}")

    # Initialize vector store
    print("Initializing vector store...")
    vector_store = VectorStore()

    # Clear existing data
    vector_store.reset()

    # Add documents
    print("Adding documents...")
    vector_store.add_documents(all_docs)

    print("✅ Vector database initialized successfully!")

    # Test search
    print("\nTesting search...")
    results = vector_store.search("SQL injection vulnerability", top_k=3)
    print(f"Found {len(results['documents'])} relevant sections")

if __name__ == "__main__":
    initialize_database()
```

**Run:**
```bash
cd backend/rag
python init_vectordb.py
```

**Time Estimate:** 1 hour (including debugging)

---

### Task 2.4: Compliance Retriever 🔎

**File:** `backend/rag/retriever.py`

**Implementation:**

```python
from typing import List, Dict
from .vector_store import VectorStore

class ComplianceRetriever:
    def __init__(self):
        self.vector_store = VectorStore()

    def retrieve_for_vulnerabilities(self, vulnerabilities: List[Dict],
                                     top_k: int = 10) -> str:
        """
        Retrieve relevant compliance sections for given vulnerabilities

        Args:
            vulnerabilities: List of vulnerability dictionaries
            top_k: Number of results to retrieve

        Returns:
            Formatted string of relevant compliance requirements
        """
        # Create query from vulnerability descriptions
        query_parts = []

        for vuln in vulnerabilities[:5]:  # Use top 5 most critical
            query_parts.append(f"{vuln.get('category', '')} {vuln.get('description', '')}")

        query = " ".join(query_parts)

        # Search vector database
        results = self.vector_store.search(query, top_k=top_k)

        # Format results
        compliance_context = self._format_results(results)

        return compliance_context

    def _format_results(self, results: Dict) -> str:
        """Format search results into readable text"""
        formatted = "## Relevant Compliance Requirements\n\n"

        for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
            source = metadata.get("source", "Unknown")

            if source == "NIST CSF":
                formatted += f"### NIST CSF (Page {metadata.get('page', 'N/A')})\n"
            elif source == "ISO 27001":
                control_id = metadata.get("control_id", "")
                formatted += f"### ISO 27001 {control_id}\n"

            formatted += f"{doc}\n\n"

        return formatted
```

**Test:**
```python
retriever = ComplianceRetriever()
mock_vulns = [
    {"category": "SQL Injection", "description": "User input not sanitized"}
]
context = retriever.retrieve_for_vulnerabilities(mock_vulns)
print(context)
```

**Time Estimate:** 2 hours

---

## PHASE 3: Main Orchestrator (Days 9-11)

### Task 3.1: Prompt Templates 📝

**File:** `backend/orchestrator/prompts.py`

**Implementation:**

```python
SAST_SNIPPET_PROMPT = """You are a security policy writer. Based on the following code-level security vulnerabilities, write a concise policy section (2-3 paragraphs) about secure coding practices.

## Vulnerabilities Found:
{vulnerabilities}

## Requirements:
- Use professional policy language suitable for executives
- Reference specific vulnerability categories (CWE codes if applicable)
- Provide actionable guidance for developers
- Keep it concise (maximum 300 words)
- Focus on preventive controls

Policy Section:"""

SCA_SNIPPET_PROMPT = """You are a security policy writer. Based on the following dependency vulnerabilities, write a concise policy section (2-3 paragraphs) about software supply chain security and dependency management.

## Dependency Issues Found:
{vulnerabilities}

## Requirements:
- Address third-party library risks
- Mention patch management procedures
- Reference version control best practices
- Use professional policy language
- Keep it concise (maximum 300 words)

Policy Section:"""

DAST_SNIPPET_PROMPT = """You are a security policy writer. Based on the following runtime security issues, write a concise policy section (2-3 paragraphs) about application deployment and runtime security.

## Runtime Issues Found:
{vulnerabilities}

## Requirements:
- Address configuration security
- Mention authentication and authorization
- Cover network security controls
- Use professional policy language
- Keep it concise (maximum 300 words)

Policy Section:"""

ORCHESTRATOR_PROMPT = """You are an expert security policy writer tasked with creating a comprehensive security policy document.

## Context:
{user_context}

## Identified Security Issues:

### Code Security Issues:
{sast_snippet}

### Dependency Security Issues:
{sca_snippet}

### Runtime Security Issues:
{dast_snippet}

## Relevant Compliance Requirements:
{compliance_context}

## Task:
Create a complete, professional security policy document with the following sections:

1. **Executive Summary**: High-level overview (2-3 paragraphs)
2. **Risk Assessment**: Detailed analysis of identified risks
3. **Security Controls**: Specific controls mapped to ISO 27001 and NIST CSF
4. **Implementation Plan**: Phased approach with priorities
5. **Roles & Responsibilities**: Who is accountable
6. **Monitoring & Review**: How to track compliance

## Requirements:
- Professional language suitable for executives and auditors
- Specific references to ISO 27001 Annex A controls
- Map controls to all 5 NIST CSF functions (Identify, Protect, Detect, Respond, Recover)
- Actionable and practical recommendations
- Consider the organization's context provided above
- Minimum 2000 words, maximum 4000 words

Security Policy Document:"""
```

**Time Estimate:** 1 hour

---

### Task 3.2: Policy Generator Main Class 🎯

**File:** `backend/orchestrator/policy_generator.py`

**Implementation:**

```python
import sys
sys.path.append('..')

from parsers import SASTParser, SCAParser, DASTParser
from llm_integrations import LLMFactory
from rag import ComplianceRetriever
from .prompts import (SAST_SNIPPET_PROMPT, SCA_SNIPPET_PROMPT,
                      DAST_SNIPPET_PROMPT, ORCHESTRATOR_PROMPT)
import yaml
from typing import Dict
import time

class PolicyGenerator:
    def __init__(self, config_path: str = "../../config.yaml"):
        """Initialize policy generator with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize parsers
        self.sast_parser = SASTParser()
        self.sca_parser = SCAParser()
        self.dast_parser = DASTParser()

        # Initialize LLM clients
        self.llm_factory = LLMFactory()
        cloud_config = self.config['llm']['cloud']

        self.sast_llm = self.llm_factory.get_client(cloud_config['sast']['provider'])
        self.sca_llm = self.llm_factory.get_client(cloud_config['sca']['provider'])
        self.dast_llm = self.llm_factory.get_client(cloud_config['dast']['provider'])
        self.orchestrator_llm = self.llm_factory.get_client(cloud_config['orchestrator']['provider'])

        # Initialize retriever
        self.retriever = ComplianceRetriever()

    def generate_policy(self, sast_report: str, sca_report: str,
                       dast_report: str, user_prompt: str) -> Dict:
        """
        Main pipeline to generate security policy

        Returns:
            Dict with policy text, metadata, and timing info
        """
        start_time = time.time()

        print("🔍 Step 1: Parsing security reports...")
        # Parse reports
        sast_vulns = self.sast_parser.parse(sast_report)
        sca_vulns = self.sca_parser.parse(sca_report)
        dast_vulns = self.dast_parser.parse(dast_report)

        print(f"   - SAST: {len(sast_vulns)} vulnerabilities")
        print(f"   - SCA: {len(sca_vulns)} vulnerabilities")
        print(f"   - DAST: {len(dast_vulns)} vulnerabilities")

        print("\n🤖 Step 2: Generating policy snippets...")
        # Generate individual snippets
        sast_snippet = self._generate_sast_snippet(sast_vulns)
        print("   - SAST snippet generated")

        sca_snippet = self._generate_sca_snippet(sca_vulns)
        print("   - SCA snippet generated")

        dast_snippet = self._generate_dast_snippet(dast_vulns)
        print("   - DAST snippet generated")

        print("\n📚 Step 3: Retrieving compliance context...")
        # Retrieve compliance context
        all_vulns = [v.__dict__ for v in sast_vulns + sca_vulns + dast_vulns]
        compliance_context = self.retriever.retrieve_for_vulnerabilities(all_vulns)
        print(f"   - Retrieved relevant compliance sections")

        print("\n📝 Step 4: Orchestrating final policy...")
        # Generate final policy
        final_policy = self._orchestrate_policy(
            sast_snippet, sca_snippet, dast_snippet,
            user_prompt, compliance_context
        )

        end_time = time.time()

        print(f"\n✅ Policy generated successfully in {end_time - start_time:.2f} seconds!")

        return {
            "policy": final_policy,
            "metadata": {
                "sast_vulns": len(sast_vulns),
                "sca_vulns": len(sca_vulns),
                "dast_vulns": len(dast_vulns),
                "generation_time": end_time - start_time
            },
            "snippets": {
                "sast": sast_snippet,
                "sca": sca_snippet,
                "dast": dast_snippet
            }
        }

    def _generate_sast_snippet(self, vulnerabilities: list) -> str:
        """Generate SAST policy snippet"""
        # Format vulnerabilities for prompt
        vuln_text = self._format_vulnerabilities(vulnerabilities)

        prompt = SAST_SNIPPET_PROMPT.format(vulnerabilities=vuln_text)

        return self.sast_llm.generate(prompt, temperature=0.3, max_tokens=800)

    def _generate_sca_snippet(self, vulnerabilities: list) -> str:
        """Generate SCA policy snippet"""
        vuln_text = self._format_vulnerabilities(vulnerabilities)

        prompt = SCA_SNIPPET_PROMPT.format(vulnerabilities=vuln_text)

        return self.sca_llm.generate(prompt, temperature=0.3, max_tokens=800)

    def _generate_dast_snippet(self, vulnerabilities: list) -> str:
        """Generate DAST policy snippet"""
        vuln_text = self._format_vulnerabilities(vulnerabilities)

        prompt = DAST_SNIPPET_PROMPT.format(vulnerabilities=vuln_text)

        return self.dast_llm.generate(prompt, temperature=0.3, max_tokens=800)

    def _orchestrate_policy(self, sast_snippet: str, sca_snippet: str,
                           dast_snippet: str, user_context: str,
                           compliance_context: str) -> str:
        """Generate final comprehensive policy"""
        prompt = ORCHESTRATOR_PROMPT.format(
            user_context=user_context,
            sast_snippet=sast_snippet,
            sca_snippet=sca_snippet,
            dast_snippet=dast_snippet,
            compliance_context=compliance_context
        )

        return self.orchestrator_llm.generate(prompt, temperature=0.3, max_tokens=4000)

    def _format_vulnerabilities(self, vulnerabilities: list) -> str:
        """Format vulnerability list for LLM prompt"""
        formatted = []

        for vuln in vulnerabilities[:10]:  # Limit to top 10
            if hasattr(vuln, '__dict__'):
                v = vuln.__dict__
            else:
                v = vuln

            formatted.append(f"- {v.get('severity', 'UNKNOWN')}: {v.get('title', v.get('category', 'Unknown'))}")
            formatted.append(f"  Description: {v.get('description', 'No description')[:200]}")

        return "\n".join(formatted)
```

**Time Estimate:** 4-5 hours

---

### Task 3.3: Test End-to-End Pipeline 🧪

**File:** `backend/orchestrator/test_generator.py`

**Implementation:**

```python
from policy_generator import PolicyGenerator

def test_policy_generation():
    """Test the complete policy generation pipeline"""

    # Load sample reports
    with open('../../data/sample_reports/sast_sample.json', 'r') as f:
        sast_report = f.read()

    with open('../../data/sample_reports/sca_sample.json', 'r') as f:
        sca_report = f.read()

    with open('../../data/sample_reports/dast_sample.xml', 'r') as f:
        dast_report = f.read()

    # User context
    user_prompt = """
    We are an e-commerce platform with 50 employees handling customer payment data.
    We must comply with PCI-DSS and ISO 27001.
    Focus on web application security and data protection.
    Our development team has 20 developers with varying security expertise.
    """

    # Generate policy
    generator = PolicyGenerator()
    result = generator.generate_policy(
        sast_report, sca_report, dast_report, user_prompt
    )

    # Save output
    with open('../../outputs/generated_policies/test_policy.txt', 'w') as f:
        f.write(result['policy'])

    print("\n" + "="*60)
    print("POLICY GENERATED")
    print("="*60)
    print(f"\nGeneration time: {result['metadata']['generation_time']:.2f} seconds")
    print(f"Total vulnerabilities: {sum([result['metadata'][k] for k in ['sast_vulns', 'sca_vulns', 'dast_vulns']])}")
    print(f"\nPolicy saved to: outputs/generated_policies/test_policy.txt")
    print(f"Policy length: {len(result['policy'])} characters")

if __name__ == "__main__":
    test_policy_generation()
```

**Run:**
```bash
cd backend/orchestrator
python test_generator.py
```

**Time Estimate:** 2 hours (including debugging)

---

## PHASE 4: Compliance & Evaluation (Days 12-14)

### Task 4.1: Compliance Checker ✅

**File:** `backend/verification/compliance_checker.py`

**Implementation:**

```python
import re
from typing import Dict, List

class ComplianceChecker:
    """Verify generated policies against compliance frameworks"""

    NIST_FUNCTIONS = ["Identify", "Protect", "Detect", "Respond", "Recover"]

    ISO_CONTROL_PATTERN = r'A\.\d+\.\d+\.\d+'  # Matches A.8.1.1, A.14.2.5, etc.

    def verify_policy(self, policy_text: str) -> Dict:
        """
        Comprehensive compliance verification

        Returns:
            Dict with coverage scores and missing elements
        """
        results = {
            "nist_csf": self._check_nist(policy_text),
            "iso_27001": self._check_iso(policy_text),
            "structure": self._check_structure(policy_text),
            "overall_score": 0,
            "grade": ""
        }

        # Calculate overall score
        nist_score = results["nist_csf"]["percentage"]
        iso_score = min(results["iso_27001"]["controls_found"] / 10 * 100, 100)
        structure_score = results["structure"]["percentage"]

        results["overall_score"] = (nist_score * 0.4 + iso_score * 0.4 + structure_score * 0.2)
        results["grade"] = self._calculate_grade(results["overall_score"])

        return results

    def _check_nist(self, text: str) -> Dict:
        """Check NIST CSF function coverage"""
        found_functions = []

        for function in self.NIST_FUNCTIONS:
            # Check for explicit mentions
            if function.lower() in text.lower():
                found_functions.append(function)

        missing = list(set(self.NIST_FUNCTIONS) - set(found_functions))

        return {
            "functions_found": found_functions,
            "functions_missing": missing,
            "percentage": len(found_functions) / len(self.NIST_FUNCTIONS) * 100
        }

    def _check_iso(self, text: str) -> Dict:
        """Check ISO 27001 control references"""
        # Find all control references (e.g., A.8.1, A.14.2.5)
        controls_found = re.findall(self.ISO_CONTROL_PATTERN, text)
        unique_controls = list(set(controls_found))

        return {
            "controls_found": len(unique_controls),
            "control_ids": unique_controls,
            "meets_minimum": len(unique_controls) >= 10
        }

    def _check_structure(self, text: str) -> Dict:
        """Check if policy has required sections"""
        required_sections = [
            "Executive Summary",
            "Risk Assessment",
            "Security Controls",
            "Implementation",
            "Roles and Responsibilities",
            "Monitoring"
        ]

        found_sections = []

        for section in required_sections:
            # Flexible matching (case-insensitive, partial match)
            pattern = section.lower().replace(" ", ".*")
            if re.search(pattern, text.lower()):
                found_sections.append(section)

        missing = list(set(required_sections) - set(found_sections))

        return {
            "sections_found": found_sections,
            "sections_missing": missing,
            "percentage": len(found_sections) / len(required_sections) * 100
        }

    def _calculate_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A (Excellent)"
        elif score >= 80:
            return "B (Good)"
        elif score >= 70:
            return "C (Satisfactory)"
        elif score >= 60:
            return "D (Needs Improvement)"
        else:
            return "F (Insufficient)"

    def generate_report(self, verification_results: Dict) -> str:
        """Generate human-readable verification report"""
        report = "="*60 + "\n"
        report += "COMPLIANCE VERIFICATION REPORT\n"
        report += "="*60 + "\n\n"

        # Overall score
        report += f"Overall Score: {verification_results['overall_score']:.1f}%\n"
        report += f"Grade: {verification_results['grade']}\n\n"

        # NIST CSF
        nist = verification_results['nist_csf']
        report += "NIST CSF Coverage:\n"
        report += f"  ✓ Found: {', '.join(nist['functions_found'])}\n"
        if nist['functions_missing']:
            report += f"  ✗ Missing: {', '.join(nist['functions_missing'])}\n"
        report += f"  Score: {nist['percentage']:.1f}%\n\n"

        # ISO 27001
        iso = verification_results['iso_27001']
        report += "ISO 27001 Coverage:\n"
        report += f"  Controls referenced: {iso['controls_found']}\n"
        report += f"  Meets minimum (10): {'Yes' if iso['meets_minimum'] else 'No'}\n"
        if iso['control_ids']:
            report += f"  Examples: {', '.join(iso['control_ids'][:5])}\n"
        report += "\n"

        # Structure
        structure = verification_results['structure']
        report += "Document Structure:\n"
        report += f"  ✓ Sections found: {', '.join(structure['sections_found'])}\n"
        if structure['sections_missing']:
            report += f"  ✗ Missing: {', '.join(structure['sections_missing'])}\n"
        report += f"  Score: {structure['percentage']:.1f}%\n\n"

        return report
```

**Test:**
```python
checker = ComplianceChecker()
with open('../../outputs/generated_policies/test_policy.txt', 'r') as f:
    policy = f.read()

results = checker.verify_policy(policy)
print(checker.generate_report(results))
```

**Time Estimate:** 3-4 hours

---

### Task 4.2: Evaluation Metrics 📊

**File:** `backend/evaluation/metrics.py`

**Implementation:**

```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from typing import Dict
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class PolicyEvaluator:
    """Evaluate AI-generated policy against manual baseline"""

    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        self.smoothing = SmoothingFunction()

    def evaluate(self, generated_policy: str, reference_policy: str) -> Dict:
        """
        Comprehensive evaluation

        Args:
            generated_policy: AI-generated policy text
            reference_policy: Manual baseline policy text

        Returns:
            Dict with all evaluation metrics
        """
        # Tokenize
        gen_tokens = generated_policy.split()
        ref_tokens = reference_policy.split()

        # BLEU Score
        bleu_score = sentence_bleu(
            [ref_tokens],
            gen_tokens,
            smoothing_function=self.smoothing.method1
        )

        # ROUGE Scores
        rouge_scores = self.rouge_scorer.score(reference_policy, generated_policy)

        # Length analysis
        length_ratio = len(gen_tokens) / len(ref_tokens) if len(ref_tokens) > 0 else 0

        # Readability (basic)
        avg_sentence_length = self._avg_sentence_length(generated_policy)

        return {
            "bleu_score": round(bleu_score, 3),
            "rouge_1": round(rouge_scores['rouge1'].fmeasure, 3),
            "rouge_2": round(rouge_scores['rouge2'].fmeasure, 3),
            "rouge_l": round(rouge_scores['rougeL'].fmeasure, 3),
            "length_ratio": round(length_ratio, 2),
            "gen_word_count": len(gen_tokens),
            "ref_word_count": len(ref_tokens),
            "avg_sentence_length": avg_sentence_length,
            "quality_assessment": self._assess_quality(bleu_score, rouge_scores)
        }

    def _avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0

        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)

    def _assess_quality(self, bleu: float, rouge_scores: Dict) -> str:
        """Provide qualitative assessment"""
        rouge_l = rouge_scores['rougeL'].fmeasure

        if bleu >= 0.70 and rouge_l >= 0.65:
            return "Excellent - Meets all targets"
        elif bleu >= 0.60 and rouge_l >= 0.55:
            return "Good - Close to targets"
        elif bleu >= 0.50 and rouge_l >= 0.45:
            return "Satisfactory - Needs improvement"
        else:
            return "Poor - Significant improvements needed"

    def generate_report(self, metrics: Dict, compliance: Dict) -> str:
        """Generate comprehensive evaluation report"""
        report = "="*60 + "\n"
        report += "POLICY EVALUATION REPORT\n"
        report += "="*60 + "\n\n"

        # Quality Metrics
        report += "Quality Metrics:\n"
        report += f"  BLEU Score: {metrics['bleu_score']:.3f} (Target: ≥0.70)\n"
        report += f"  ROUGE-L: {metrics['rouge_l']:.3f} (Target: ≥0.65)\n"
        report += f"  ROUGE-1: {metrics['rouge_1']:.3f}\n"
        report += f"  ROUGE-2: {metrics['rouge_2']:.3f}\n"
        report += f"  Assessment: {metrics['quality_assessment']}\n\n"

        # Length Analysis
        report += "Length Analysis:\n"
        report += f"  Generated: {metrics['gen_word_count']} words\n"
        report += f"  Reference: {metrics['ref_word_count']} words\n"
        report += f"  Ratio: {metrics['length_ratio']:.2f}\n"
        report += f"  Avg sentence length: {metrics['avg_sentence_length']:.1f} words\n\n"

        # Compliance
        report += "Compliance Score:\n"
        report += f"  Overall: {compliance['overall_score']:.1f}%\n"
        report += f"  Grade: {compliance['grade']}\n\n"

        # Target Achievement
        bleu_pass = "✓" if metrics['bleu_score'] >= 0.70 else "✗"
        rouge_pass = "✓" if metrics['rouge_l'] >= 0.65 else "✗"
        comp_pass = "✓" if compliance['overall_score'] >= 85 else "✗"

        report += "Target Achievement:\n"
        report += f"  {bleu_pass} BLEU ≥0.70\n"
        report += f"  {rouge_pass} ROUGE-L ≥0.65\n"
        report += f"  {comp_pass} Compliance ≥85%\n\n"

        return report
```

**Time Estimate:** 3 hours

---

### Task 4.3: Create Manual Baseline Policy 📄

**File:** `data/manual_baseline/baseline_policy.txt`

**What to do:**

1. Select 8-10 representative vulnerabilities from your sample reports
2. Manually write a 8-12 page security policy addressing them
3. Include all required sections:
   - Executive Summary
   - Risk Assessment
   - Security Controls with ISO 27001 mapping
   - NIST CSF alignment
   - Implementation plan
   - Roles & responsibilities

4. Use professional policy language
5. Reference specific controls (e.g., A.14.2.5, PR.DS-5)
6. Make it realistic and comprehensive

**Alternative:** If you don't have time, use a simplified 3-page baseline focusing on the most critical elements.

**Time Estimate:** 8-10 hours (or 2 hours for simplified version)

---

## PHASE 5: API & Frontend (Days 15-17)

### Task 5.1: FastAPI Backend 🚀

**File:** `backend/api/main.py`

**Implementation:**

```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append('..')

from orchestrator.policy_generator import PolicyGenerator
from verification.compliance_checker import ComplianceChecker
from evaluation.metrics import PolicyEvaluator
import json
from datetime import datetime

app = FastAPI(
    title="SecPolicy AI API",
    description="AI-Driven Security Policy Generator",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
policy_generator = PolicyGenerator()
compliance_checker = ComplianceChecker()
policy_evaluator = PolicyEvaluator()

# Request/Response models
class PolicyRequest(BaseModel):
    user_prompt: str

class PolicyResponse(BaseModel):
    policy: str
    compliance: dict
    metadata: dict
    timestamp: str

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "SecPolicy AI",
        "version": "1.0.0"
    }

@app.post("/generate-policy", response_model=PolicyResponse)
async def generate_policy(
    sast_report: UploadFile = File(..., description="SAST report (JSON)"),
    sca_report: UploadFile = File(..., description="SCA report (JSON)"),
    dast_report: UploadFile = File(..., description="DAST report (XML or JSON)"),
    user_prompt: str = Form(..., description="Organization context and requirements")
):
    """
    Generate security policy from vulnerability reports

    - **sast_report**: Static analysis report (JSON format)
    - **sca_report**: Dependency scan report (JSON format)
    - **dast_report**: Dynamic scan report (XML or JSON format)
    - **user_prompt**: Your organization's context (industry, size, compliance needs)
    """
    try:
        # Validate file types
        if not sast_report.filename.endswith('.json'):
            raise HTTPException(400, "SAST report must be JSON")
        if not sca_report.filename.endswith('.json'):
            raise HTTPException(400, "SCA report must be JSON")
        if not (dast_report.filename.endswith('.xml') or dast_report.filename.endswith('.json')):
            raise HTTPException(400, "DAST report must be XML or JSON")

        # Read file contents
        sast_content = (await sast_report.read()).decode('utf-8')
        sca_content = (await sca_report.read()).decode('utf-8')
        dast_content = (await dast_report.read()).decode('utf-8')

        # Generate policy
        print("📝 Generating policy...")
        result = policy_generator.generate_policy(
            sast_content, sca_content, dast_content, user_prompt
        )

        # Verify compliance
        print("✅ Verifying compliance...")
        compliance_results = compliance_checker.verify_policy(result['policy'])

        # Save generated policy
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"../../outputs/generated_policies/policy_{timestamp}.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['policy'])

        return PolicyResponse(
            policy=result['policy'],
            compliance=compliance_results,
            metadata=result['metadata'],
            timestamp=timestamp
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(500, f"Policy generation failed: {str(e)}")

@app.post("/evaluate-policy")
async def evaluate_policy(
    generated_policy: UploadFile = File(...),
    reference_policy: UploadFile = File(...)
):
    """
    Evaluate AI-generated policy against manual baseline

    - **generated_policy**: AI-generated policy text file
    - **reference_policy**: Manual baseline policy text file
    """
    try:
        gen_content = (await generated_policy.read()).decode('utf-8')
        ref_content = (await reference_policy.read()).decode('utf-8')

        # Evaluate
        metrics = policy_evaluator.evaluate(gen_content, ref_content)

        # Also check compliance
        compliance = compliance_checker.verify_policy(gen_content)

        # Generate report
        report = policy_evaluator.generate_report(metrics, compliance)

        return {
            "metrics": metrics,
            "compliance": compliance,
            "report": report
        }

    except Exception as e:
        raise HTTPException(500, f"Evaluation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "policy_generator": "ok",
            "compliance_checker": "ok",
            "evaluator": "ok"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

**Run:**
```bash
cd backend/api
python main.py
# Or: uvicorn main:app --reload --port 8000
```

**Test:**
Open http://localhost:8000/docs for Swagger UI

**Time Estimate:** 4-5 hours

---

### Task 5.2: Frontend Interface 🎨

**File:** `frontend/index.html`

**Implementation:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecPolicy AI - Security Policy Generator</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ SecPolicy AI</h1>
            <p class="tagline">AI-Driven Security Policy Generator</p>
            <p class="subtitle">Transform vulnerability reports into compliance-ready policies in minutes</p>
        </header>

        <div class="main-content">
            <!-- Upload Form -->
            <div class="upload-section" id="uploadSection">
                <h2>1. Upload Security Reports</h2>

                <div class="file-upload-group">
                    <label for="sastReport">
                        <span class="label-icon">📝</span>
                        <span class="label-text">SAST Report (JSON)</span>
                    </label>
                    <input type="file" id="sastReport" accept=".json" required>
                    <span class="file-name" id="sastFileName">No file chosen</span>
                </div>

                <div class="file-upload-group">
                    <label for="scaReport">
                        <span class="label-icon">📦</span>
                        <span class="label-text">SCA Report (JSON)</span>
                    </label>
                    <input type="file" id="scaReport" accept=".json" required>
                    <span class="file-name" id="scaFileName">No file chosen</span>
                </div>

                <div class="file-upload-group">
                    <label for="dastReport">
                        <span class="label-icon">🌐</span>
                        <span class="label-text">DAST Report (XML/JSON)</span>
                    </label>
                    <input type="file" id="dastReport" accept=".xml,.json" required>
                    <span class="file-name" id="dastFileName">No file chosen</span>
                </div>

                <h2>2. Provide Context</h2>
                <div class="prompt-section">
                    <label for="userPrompt">Organization Context & Requirements:</label>
                    <textarea
                        id="userPrompt"
                        rows="6"
                        placeholder="Example:&#10;&#10;We are a healthcare SaaS platform with 100 employees. We handle PHI (Protected Health Information) and must comply with HIPAA and ISO 27001. Our main concerns are:&#10;- Data encryption and access controls&#10;- Secure development practices&#10;- Third-party vendor management&#10;&#10;Our team includes 30 developers with basic security training."
                    ></textarea>
                </div>

                <button id="generateBtn" class="btn-primary">
                    <span id="btnText">🚀 Generate Policy</span>
                    <span id="btnLoader" class="loader" style="display:none;"></span>
                </button>

                <div id="statusMessage" class="status-message"></div>
            </div>

            <!-- Results Section -->
            <div class="results-section" id="resultsSection" style="display:none;">
                <h2>📄 Generated Security Policy</h2>

                <div class="tabs">
                    <button class="tab-btn active" onclick="showTab('policy')">Policy Document</button>
                    <button class="tab-btn" onclick="showTab('compliance')">Compliance Check</button>
                    <button class="tab-btn" onclick="showTab('metadata')">Metadata</button>
                </div>

                <div id="policyTab" class="tab-content active">
                    <div class="policy-content" id="policyContent"></div>
                    <button class="btn-secondary" onclick="downloadPolicy()">
                        ⬇️ Download as TXT
                    </button>
                </div>

                <div id="complianceTab" class="tab-content">
                    <div id="complianceContent"></div>
                </div>

                <div id="metadataTab" class="tab-content">
                    <div id="metadataContent"></div>
                </div>

                <button class="btn-secondary" onclick="resetForm()">
                    🔄 Generate Another Policy
                </button>
            </div>
        </div>

        <footer>
            <p>Built with ❤️ using Groq, DeepSeek, and OpenAI | <a href="https://github.com" target="_blank">View on GitHub</a></p>
        </footer>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

**Time Estimate:** 2 hours

---

**File:** `frontend/styles.css`

**Implementation:** (Due to length, I'll provide essential styles)

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

header {
    text-align: center;
    color: white;
    margin-bottom: 40px;
}

header h1 {
    font-size: 3em;
    margin-bottom: 10px;
}

.tagline {
    font-size: 1.5em;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 1.1em;
    opacity: 0.9;
}

.main-content {
    background: white;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.file-upload-group {
    margin-bottom: 20px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 2px dashed #cbd5e0;
    transition: all 0.3s;
}

.file-upload-group:hover {
    border-color: #667eea;
    background: #eef2ff;
}

.file-upload-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 10px;
    color: #2d3748;
}

.label-icon {
    font-size: 1.5em;
    margin-right: 10px;
}

input[type="file"] {
    display: block;
    width: 100%;
    padding: 10px;
    margin-top: 10px;
}

.file-name {
    display: block;
    margin-top: 5px;
    font-size: 0.9em;
    color: #718096;
    font-style: italic;
}

.prompt-section {
    margin: 30px 0;
}

.prompt-section label {
    display: block;
    font-weight: 600;
    margin-bottom: 10px;
    color: #2d3748;
}

textarea {
    width: 100%;
    padding: 15px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1em;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.3s;
}

textarea:focus {
    outline: none;
    border-color: #667eea;
}

.btn-primary {
    width: 100%;
    padding: 18px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1.2em;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-top: 20px;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.loader {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-left: 10px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.status-message {
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    display: none;
}

.status-message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
    display: block;
}

.status-message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
    display: block;
}

.results-section {
    margin-top: 40px;
    padding-top: 40px;
    border-top: 2px solid #e2e8f0;
}

.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.tab-btn {
    padding: 12px 24px;
    background: #e2e8f0;
    border: none;
    border-radius: 8px 8px 0 0;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.3s;
}

.tab-btn.active {
    background: #667eea;
    color: white;
}

.tab-content {
    display: none;
    padding: 30px;
    background: #f8f9fa;
    border-radius: 0 8px 8px 8px;
    min-height: 400px;
}

.tab-content.active {
    display: block;
}

.policy-content {
    background: white;
    padding: 30px;
    border-radius: 8px;
    white-space: pre-wrap;
    font-family: 'Georgia', serif;
    line-height: 1.8;
    max-height: 600px;
    overflow-y: auto;
}

.btn-secondary {
    margin-top: 20px;
    padding: 12px 24px;
    background: #4a5568;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.3s;
}

.btn-secondary:hover {
    background: #2d3748;
}

footer {
    text-align: center;
    color: white;
    margin-top: 40px;
    padding: 20px;
}

footer a {
    color: white;
    text-decoration: underline;
}
```

**Time Estimate:** 2 hours

---

**File:** `frontend/app.js`

**Implementation:**

```javascript
const API_URL = 'http://localhost:8000';

let currentPolicy = null;
let currentCompliance = null;
let currentMetadata = null;

// File input handlers
document.getElementById('sastReport').addEventListener('change', (e) => {
    document.getElementById('sastFileName').textContent = e.target.files[0]?.name || 'No file chosen';
});

document.getElementById('scaReport').addEventListener('change', (e) => {
    document.getElementById('scaFileName').textContent = e.target.files[0]?.name || 'No file chosen';
});

document.getElementById('dastReport').addEventListener('change', (e) => {
    document.getElementById('dastFileName').textContent = e.target.files[0]?.name || 'No file chosen';
});

// Generate policy
document.getElementById('generateBtn').addEventListener('click', async () => {
    const sastFile = document.getElementById('sastReport').files[0];
    const scaFile = document.getElementById('scaReport').files[0];
    const dastFile = document.getElementById('dastReport').files[0];
    const userPrompt = document.getElementById('userPrompt').value;

    // Validation
    if (!sastFile || !scaFile || !dastFile) {
        showStatus('Please upload all three security reports', 'error');
        return;
    }

    if (!userPrompt.trim()) {
        showStatus('Please provide organization context', 'error');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('sast_report', sastFile);
    formData.append('sca_report', scaFile);
    formData.append('dast_report', dastFile);
    formData.append('user_prompt', userPrompt);

    // Show loading
    const btn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');

    btn.disabled = true;
    btnText.textContent = 'Generating Policy...';
    btnLoader.style.display = 'inline-block';

    showStatus('Generating policy... This may take 30-60 seconds.', 'success');

    try {
        const response = await fetch(`${API_URL}/generate-policy`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const result = await response.json();

        // Store results
        currentPolicy = result.policy;
        currentCompliance = result.compliance;
        currentMetadata = result.metadata;

        // Display results
        displayResults(result);

        showStatus('✅ Policy generated successfully!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btnText.textContent = '🚀 Generate Policy';
        btnLoader.style.display = 'none';
    }
});

function displayResults(result) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

    // Display policy
    document.getElementById('policyContent').textContent = result.policy;

    // Display compliance
    displayCompliance(result.compliance);

    // Display metadata
    displayMetadata(result.metadata);
}

function displayCompliance(compliance) {
    const container = document.getElementById('complianceContent');

    let html = '<div class="compliance-report">';

    // Overall score
    html += `
        <div class="score-card">
            <h3>Overall Compliance Score</h3>
            <div class="score-circle">${compliance.overall_score.toFixed(1)}%</div>
            <p class="grade">${compliance.grade}</p>
        </div>
    `;

    // NIST CSF
    html += '<div class="compliance-section">';
    html += '<h3>NIST CSF Coverage</h3>';
    html += `<p>Coverage: ${compliance.nist_csf.percentage.toFixed(1)}%</p>`;
    html += '<p>Functions Found: ' + compliance.nist_csf.functions_found.join(', ') + '</p>';
    if (compliance.nist_csf.functions_missing.length > 0) {
        html += '<p class="warning">Missing: ' + compliance.nist_csf.functions_missing.join(', ') + '</p>';
    }
    html += '</div>';

    // ISO 27001
    html += '<div class="compliance-section">';
    html += '<h3>ISO 27001 Coverage</h3>';
    html += `<p>Controls Referenced: ${compliance.iso_27001.controls_found}</p>`;
    html += `<p>Meets Minimum (10): ${compliance.iso_27001.meets_minimum ? '✓ Yes' : '✗ No'}</p>`;
    html += '</div>';

    // Structure
    html += '<div class="compliance-section">';
    html += '<h3>Document Structure</h3>';
    html += `<p>Score: ${compliance.structure.percentage.toFixed(1)}%</p>`;
    html += '<p>Sections Found: ' + compliance.structure.sections_found.join(', ') + '</p>';
    if (compliance.structure.sections_missing.length > 0) {
        html += '<p class="warning">Missing: ' + compliance.structure.sections_missing.join(', ') + '</p>';
    }
    html += '</div>';

    html += '</div>';

    container.innerHTML = html;
}

function displayMetadata(metadata) {
    const container = document.getElementById('metadataContent');

    let html = '<div class="metadata-report">';
    html += `<p><strong>Generation Time:</strong> ${metadata.generation_time.toFixed(2)} seconds</p>`;
    html += `<p><strong>SAST Vulnerabilities:</strong> ${metadata.sast_vulns}</p>`;
    html += `<p><strong>SCA Vulnerabilities:</strong> ${metadata.sca_vulns}</p>`;
    html += `<p><strong>DAST Vulnerabilities:</strong> ${metadata.dast_vulns}</p>`;
    html += `<p><strong>Total Issues:</strong> ${metadata.sast_vulns + metadata.sca_vulns + metadata.dast_vulns}</p>`;
    html += '</div>';

    container.innerHTML = html;
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
}

function downloadPolicy() {
    if (!currentPolicy) return;

    const blob = new Blob([currentPolicy], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `security_policy_${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

function resetForm() {
    document.getElementById('uploadSection').scrollIntoView({ behavior: 'smooth' });
    document.getElementById('resultsSection').style.display = 'none';

    document.getElementById('sastReport').value = '';
    document.getElementById('scaReport').value = '';
    document.getElementById('dastReport').value = '';
    document.getElementById('userPrompt').value = '';

    document.getElementById('sastFileName').textContent = 'No file chosen';
    document.getElementById('scaFileName').textContent = 'No file chosen';
    document.getElementById('dastFileName').textContent = 'No file chosen';

    currentPolicy = null;
    currentCompliance = null;
    currentMetadata = null;
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}
```

**Time Estimate:** 3 hours

---

## PHASE 6: Testing & Final Evaluation (Days 18-20)

### Task 6.1: End-to-End Testing 🧪

**Create test script:** `tests/test_e2e.py`

```python
import sys
sys.path.append('../backend')

from orchestrator.policy_generator import PolicyGenerator
from verification.compliance_checker import ComplianceChecker
from evaluation.metrics import PolicyEvaluator

def run_full_pipeline():
    """Test complete pipeline"""

    print("="*60)
    print("END-TO-END PIPELINE TEST")
    print("="*60)

    # Load sample reports
    with open('../data/sample_reports/sast_sample.json', 'r') as f:
        sast = f.read()
    with open('../data/sample_reports/sca_sample.json', 'r') as f:
        sca = f.read()
    with open('../data/sample_reports/dast_sample.xml', 'r') as f:
        dast = f.read()

    user_prompt = """
    Healthcare SaaS platform, 100 employees, HIPAA + ISO 27001 compliance required.
    Focus on data encryption, access controls, and secure development.
    """

    # Generate
    generator = PolicyGenerator()
    result = generator.generate_policy(sast, sca, dast, user_prompt)

    # Verify
    checker = ComplianceChecker()
    compliance = checker.verify_policy(result['policy'])

    print("\n" + checker.generate_report(compliance))

    # Evaluate (if baseline exists)
    try:
        with open('../data/manual_baseline/baseline_policy.txt', 'r') as f:
            baseline = f.read()

        evaluator = PolicyEvaluator()
        metrics = evaluator.evaluate(result['policy'], baseline)

        print(evaluator.generate_report(metrics, compliance))
    except FileNotFoundError:
        print("⚠️  No baseline policy found for evaluation")

    print("\n✅ Pipeline test complete!")

if __name__ == "__main__":
    run_full_pipeline()
```

**Run:**
```bash
cd tests
python test_e2e.py
```

**Time Estimate:** 2-3 hours

---

### Task 6.2: Create Final Documentation 📚

**File:** `PROJECT_REPORT.md`

Create a comprehensive report including:

1. **Abstract** (1 page)
2. **Introduction** (2-3 pages)
   - Problem statement
   - Objectives
   - Scope

3. **Literature Review** (3-4 pages)
   - DevSecOps overview
   - LLMs in security
   - Compliance frameworks

4. **Methodology** (5-6 pages)
   - System architecture
   - Component descriptions
   - LLM selection rationale
   - RAG system design

5. **Implementation** (8-10 pages)
   - Code structure
   - Parser implementation
   - LLM integration
   - RAG system
   - Orchestrator pipeline

6. **Evaluation** (6-8 pages)
   - Test setup
   - Results (BLEU, ROUGE, compliance scores)
   - Comparison with manual process
   - Discussion

7. **Ethical Considerations** (2-3 pages)
   - AI reliability
   - Privacy concerns
   - Accountability

8. **Conclusion** (2 pages)
   - Summary
   - Limitations
   - Future work

9. **References**

10. **Appendices**
    - Sample reports
    - Generated policy examples
    - Code snippets

**Time Estimate:** 12-15 hours

---

### Task 6.3: Prepare Presentation 🎤

**File:** `PRESENTATION.pptx`

Create slides covering:

1. Title & Introduction (1 slide)
2. Problem Statement (2 slides)
3. Solution Overview (2 slides)
4. Architecture Diagram (1-2 slides)
5. Demo (Live or video)
6. Results (3-4 slides with charts)
7. Evaluation Metrics (2 slides)
8. Challenges & Lessons (1-2 slides)
9. Conclusion & Future Work (1 slide)
10. Q&A

**Time Estimate:** 4-6 hours

---

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create complete project folder structure", "status": "completed", "activeForm": "Creating complete project folder structure"}, {"content": "Set up Python virtual environment and install dependencies", "status": "pending", "activeForm": "Setting up Python virtual environment and installing dependencies"}, {"content": "Configure API keys and environment variables", "status": "pending", "activeForm": "Configuring API keys and environment variables"}, {"content": "Download and prepare sample security reports (SAST/SCA/DAST)", "status": "pending", "activeForm": "Downloading sample security reports"}, {"content": "Obtain compliance documents (NIST CSF, ISO 27001)", "status": "pending", "activeForm": "Obtaining compliance documents"}, {"content": "Implement SAST parser", "status": "pending", "activeForm": "Implementing SAST parser"}, {"content": "Implement SCA parser", "status": "pending", "activeForm": "Implementing SCA parser"}, {"content": "Implement DAST parser", "status": "pending", "activeForm": "Implementing DAST parser"}, {"content": "Build LLM clients (Groq, DeepSeek, OpenAI)", "status": "pending", "activeForm": "Building LLM clients"}, {"content": "Create LLM factory and test API connections", "status": "pending", "activeForm": "Creating LLM factory"}, {"content": "Build document loader for compliance documents", "status": "pending", "activeForm": "Building document loader"}, {"content": "Set up ChromaDB vector store", "status": "pending", "activeForm": "Setting up ChromaDB vector store"}, {"content": "Initialize vector database with compliance docs", "status": "pending", "activeForm": "Initializing vector database"}, {"content": "Implement compliance retriever", "status": "pending", "activeForm": "Implementing compliance retriever"}, {"content": "Create prompt templates for all LLM stages", "status": "pending", "activeForm": "Creating prompt templates"}, {"content": "Build main policy generator orchestrator", "status": "pending", "activeForm": "Building policy generator orchestrator"}, {"content": "Test end-to-end policy generation pipeline", "status": "pending", "activeForm": "Testing policy generation pipeline"}, {"content": "Implement compliance verification module", "status": "pending", "activeForm": "Implementing compliance verification module"}, {"content": "Build evaluation metrics (BLEU, ROUGE)", "status": "pending", "activeForm": "Building evaluation metrics"}, {"content": "Create manual baseline policy for comparison", "status": "pending", "activeForm": "Creating manual baseline policy"}, {"content": "Build FastAPI backend with all endpoints", "status": "pending", "activeForm": "Building FastAPI backend"}, {"content": "Create web frontend (HTML, CSS, JavaScript)", "status": "pending", "activeForm": "Creating web frontend"}, {"content": "Integrate frontend with backend API", "status": "pending", "activeForm": "Integrating frontend with backend"}, {"content": "Run end-to-end system tests", "status": "pending", "activeForm": "Running end-to-end tests"}, {"content": "Write final project report", "status": "pending", "activeForm": "Writing final project report"}, {"content": "Prepare presentation slides", "status": "pending", "activeForm": "Preparing presentation slides"}]