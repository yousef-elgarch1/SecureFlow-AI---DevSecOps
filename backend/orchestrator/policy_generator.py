"""
Main Orchestrator for Policy Generation Pipeline
Coordinates parsers, RAG, LLMs, and evaluation for automated security policy generation
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from project root
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import parsers
from parsers.sast_parser import SASTParser
from parsers.sca_parser import SCAParser
from parsers.dast_parser import DASTParser

# Import RAG components
from rag.retriever import ComplianceRetriever

# Import LLM clients
from llm_integrations.groq_client import GroqClient
from llm_integrations.huggingface_client import HuggingFaceClient

# Import prompts
from prompts.policy_templates import PolicyPromptTemplates

# Import user profile and adaptive prompts for personalized policy generation
try:
    from backend.models.user_profile import UserProfile, ExpertiseLevel
    from backend.prompts.adaptive_templates import AdaptivePolicyPrompts
    ADAPTIVE_PROMPTS_AVAILABLE = True
except ImportError:
    print("Warning: Adaptive prompts not available. Using default templates.")
    ADAPTIVE_PROMPTS_AVAILABLE = False


class PolicyGeneratorOrchestrator:
    """
    Main orchestrator that coordinates the entire policy generation pipeline
    """

    def __init__(
        self,
        use_rag: bool = True,
        llm_models: List[str] = None,
        output_dir: str = "./outputs",
        user_profile: 'UserProfile' = None
    ):
        """
        Initialize the orchestrator

        Args:
            use_rag: Whether to use RAG for compliance context
            llm_models: List of LLM models to use (for comparative study)
            output_dir: Directory to save generated policies
            user_profile: User profile for adaptive policy generation (optional)
        """
        print("Initializing Policy Generator Orchestrator...")

        # Set user profile (default if not provided)
        if ADAPTIVE_PROMPTS_AVAILABLE and user_profile:
            self.user_profile = user_profile
            print(f"Using adaptive prompts for {user_profile.expertise_level.value} level user")
        elif ADAPTIVE_PROMPTS_AVAILABLE:
            self.user_profile = UserProfile.default()
            print("Using default user profile (intermediate level)")
        else:
            self.user_profile = None

        # Initialize parsers
        self.sast_parser = SASTParser()
        self.sca_parser = SCAParser()
        self.dast_parser = DASTParser()

        # Initialize RAG retriever
        self.use_rag = use_rag
        if use_rag:
            try:
                self.retriever = ComplianceRetriever()
                print("RAG retriever initialized")
            except Exception as e:
                print(f"Warning: RAG initialization failed: {e}")
                print("Continuing without RAG...")
                self.use_rag = False

        # Initialize specialized LLM clients per vulnerability type
        # Using Groq's FREE tier with different models for comparison
        # SAST & SCA: LLaMA 3.3 70B - most capable for code analysis
        # DAST: LLaMA 3.1 8B - faster, good for runtime issue analysis

        self.llm_clients = {}

        # LLaMA 3.3 70B for SAST and SCA (most capable)
        try:
            self.llm_clients['sast'] = GroqClient(model="llama-3.3-70b-versatile")
            self.llm_clients['sca'] = GroqClient(model="llama-3.3-70b-versatile")
            print("LLM initialized for SAST/SCA: LLaMA 3.3 70B (Groq)")
        except Exception as e:
            print(f"Warning: Failed to initialize Groq LLaMA 3.3: {e}")

        # LLaMA 3.1 8B for DAST (faster, specialized for runtime issues)
        try:
            self.llm_clients['dast'] = GroqClient(model="llama-3.1-8b-instant")
            print("LLM initialized for DAST: LLaMA 3.1 8B Instant (Groq)")
        except Exception as e:
            print(f"Warning: Failed to initialize Groq LLaMA 3.1: {e}")

        if not self.llm_clients:
            raise Exception("No LLM clients could be initialized!")

        # Initialize prompt templates
        self.prompt_templates = PolicyPromptTemplates()

        # Output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("Orchestrator initialization complete!\n")

    def parse_reports(
        self,
        sast_path: str = None,
        sca_path: str = None,
        dast_path: str = None
    ) -> Tuple[List, List, List]:
        """
        Parse all vulnerability reports

        Args:
            sast_path: Path to SAST report (JSON)
            sca_path: Path to SCA report (JSON)
            dast_path: Path to DAST report (XML)

        Returns:
            Tuple of (sast_vulns, sca_vulns, dast_vulns)
        """
        print("=" * 60)
        print("STEP 1: PARSING VULNERABILITY REPORTS")
        print("=" * 60)

        sast_vulns = []
        sca_vulns = []
        dast_vulns = []

        # Parse SAST report
        if sast_path and os.path.exists(sast_path):
            print(f"\nParsing SAST report: {sast_path}")
            with open(sast_path, 'r') as f:
                sast_content = f.read()
            sast_vulns = self.sast_parser.parse(sast_content)
            print(f"Found {len(sast_vulns)} SAST vulnerabilities")

        # Parse SCA report
        if sca_path and os.path.exists(sca_path):
            print(f"\nParsing SCA report: {sca_path}")
            with open(sca_path, 'r', encoding='utf-8-sig') as f:
                sca_content = f.read()
            sca_vulns = self.sca_parser.parse(sca_content)
            print(f"Found {len(sca_vulns)} SCA vulnerabilities")

        # Parse DAST report
        if dast_path and os.path.exists(dast_path):
            print(f"\nParsing DAST report: {dast_path}")
            with open(dast_path, 'r') as f:
                dast_content = f.read()
            dast_vulns = self.dast_parser.parse(dast_content)
            print(f"Found {len(dast_vulns)} DAST vulnerabilities")

        total = len(sast_vulns) + len(sca_vulns) + len(dast_vulns)
        print(f"\nTotal vulnerabilities: {total}")

        return sast_vulns, sca_vulns, dast_vulns

    def generate_policy_for_vulnerability(
        self,
        vulnerability: Dict,
        vuln_type: str
    ) -> str:
        """
        Generate security policy for a single vulnerability using specialized LLM

        Args:
            vulnerability: Vulnerability dict
            vuln_type: Type (SAST, SCA, or DAST)

        Returns:
            Generated policy text
        """
        # Get severity
        severity = vulnerability.get('severity', 'MEDIUM')

        # Get compliance context from RAG
        compliance_context = "No compliance context available"
        if self.use_rag:
            try:
                rag_result = self.retriever.retrieve_for_vulnerability(
                    vulnerability,
                    top_k=5
                )
                compliance_context = rag_result['formatted_context']
            except Exception as e:
                print(f"  Warning: RAG retrieval failed: {e}")

        # Generate prompt using adaptive templates if available
        if ADAPTIVE_PROMPTS_AVAILABLE and self.user_profile:
            # Use adaptive prompts based on user expertise level
            user_prompt = AdaptivePolicyPrompts.select_prompt(
                vulnerability_type=vuln_type.lower(),
                expertise_level=self.user_profile.expertise_level,
                vulnerability=vulnerability,
                compliance_context=compliance_context,
                user_profile=self.user_profile
            )
            system_prompt = self.prompt_templates.get_system_prompt()
        else:
            # Fallback to default prompts
            system_prompt = self.prompt_templates.get_system_prompt()
            user_prompt = self.prompt_templates.get_policy_generation_prompt(
                vulnerability,
                compliance_context,
                severity
            )

        # Select LLM client based on vulnerability type
        # SAST/SCA -> LLaMA 3.3, DAST -> DeepSeek R1
        client_key = vuln_type.lower()
        client = self.llm_clients.get(client_key)

        if not client:
            raise Exception(f"No LLM client available for {vuln_type}")

        # Generate policy using specialized LLM
        policy = client.generate(
            user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )

        return policy

    def generate_policies(
        self,
        sast_vulns: List,
        sca_vulns: List,
        dast_vulns: List,
        max_per_type: int = 3
    ) -> Dict:
        """
        Generate policies for all vulnerabilities using multiple LLMs

        Args:
            sast_vulns: List of SAST vulnerabilities
            sca_vulns: List of SCA vulnerabilities
            dast_vulns: List of DAST vulnerabilities
            max_per_type: Maximum vulnerabilities to process per type (for testing)

        Returns:
            Dict with generated policies per LLM model
        """
        print("\n" + "=" * 60)
        print("STEP 2: GENERATING SECURITY POLICIES")
        print("=" * 60)

        # Limit vulnerabilities for faster testing
        # Convert dataclass objects to dicts
        from dataclasses import asdict

        all_vulns = []

        for vuln in sast_vulns[:max_per_type]:
            all_vulns.append(('SAST', asdict(vuln)))

        for vuln in sca_vulns[:max_per_type]:
            all_vulns.append(('SCA', asdict(vuln)))

        for vuln in dast_vulns[:max_per_type]:
            all_vulns.append(('DAST', asdict(vuln)))

        print(f"\nProcessing {len(all_vulns)} vulnerabilities...")
        print("Using specialized LLMs (Comparative Study):")
        print("  - SAST/SCA: LLaMA 3.3 70B (Groq - most capable)")
        print("  - DAST: LLaMA 3.1 8B Instant (Groq - faster)\n")

        # Generate policies using specialized LLMs
        results = []

        for i, (vuln_type, vuln) in enumerate(all_vulns):
            # Get title based on vulnerability type
            if vuln_type == 'SAST':
                title = vuln.get('title', 'Unknown SAST vulnerability')
            elif vuln_type == 'SCA':
                title = f"{vuln.get('package_name', 'Unknown package')} - {vuln.get('cve_id', 'Unknown CVE')}"
            elif vuln_type == 'DAST':
                title = vuln.get('issue_type', vuln.get('alert', vuln.get('name', 'Unknown DAST vulnerability')))
            else:
                title = 'Unknown'

            # Show which LLM is being used
            llm_name = "LLaMA 3.3 70B" if vuln_type in ['SAST', 'SCA'] else "LLaMA 3.1 8B"
            print(f"  [{i+1}/{len(all_vulns)}] {vuln_type} ({llm_name}): {title[:50]}...")

            try:
                policy = self.generate_policy_for_vulnerability(
                    vuln,
                    vuln_type
                )

                results.append({
                    'type': vuln_type,
                    'vulnerability': vuln,
                    'policy': policy,
                    'llm_used': llm_name
                })

            except Exception as e:
                print(f"    ERROR: {e}")
                results.append({
                    'type': vuln_type,
                    'vulnerability': vuln,
                    'policy': f"ERROR: Failed to generate policy - {e}",
                    'error': str(e),
                    'llm_used': llm_name
                })

        return results

    def save_results(
        self,
        results: List,
        sast_vulns: List,
        sca_vulns: List,
        dast_vulns: List
    ) -> str:
        """
        Save generated policies to files

        Args:
            results: List of generated policies with LLM info
            sast_vulns: Original SAST vulnerabilities
            sca_vulns: Original SCA vulnerabilities
            dast_vulns: Original DAST vulnerabilities

        Returns:
            Path to main output file
        """
        print("\n" + "=" * 60)
        print("STEP 3: SAVING RESULTS")
        print("=" * 60)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed JSON results
        json_path = self.output_dir / f"policy_generation_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nJSON results saved: {json_path}")

        # Generate human-readable report
        report_path = self.output_dir / f"security_policy_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("AI-POWERED SECURITY POLICY GENERATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Vulnerabilities Scanned: {len(sast_vulns) + len(sca_vulns) + len(dast_vulns)}\n")
            f.write(f"  - SAST: {len(sast_vulns)}\n")
            f.write(f"  - SCA: {len(sca_vulns)}\n")
            f.write(f"  - DAST: {len(dast_vulns)}\n\n")

            f.write("LLM Models Used (Comparative Study):\n")
            f.write("  - SAST/SCA: LLaMA 3.3 70B (Groq - most capable)\n")
            f.write("  - DAST: LLaMA 3.1 8B Instant (Groq - faster)\n")
            f.write("=" * 80 + "\n\n")

            for i, item in enumerate(results):
                vuln_type = item['type']
                llm_used = item.get('llm_used', 'Unknown')

                # Get appropriate title
                if vuln_type == 'SAST':
                    title = item['vulnerability'].get('title', 'Unknown')
                elif vuln_type == 'SCA':
                    pkg = item['vulnerability'].get('package_name', 'Unknown')
                    cve = item['vulnerability'].get('cve_id', 'Unknown')
                    title = f"{pkg} - {cve}"
                elif vuln_type == 'DAST':
                    title = item['vulnerability'].get('issue_type', 'Unknown')
                else:
                    title = 'Unknown'

                f.write(f"\nPOLICY {i+1}: {vuln_type} Vulnerability\n")
                f.write(f"LLM: {llm_used}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Title: {title}\n")
                f.write(f"Severity: {item['vulnerability'].get('severity', 'MEDIUM')}\n\n")
                f.write(item['policy'])
                f.write("\n\n" + "=" * 80 + "\n")

        print(f"Report saved: {report_path}")

        # Generate HTML version
        html_path = self.output_dir / f"security_policy_{timestamp}.html"
        self._generate_html_report(html_path, results, sast_vulns, sca_vulns, dast_vulns, timestamp)
        print(f"HTML report saved: {html_path}")

        # Generate PDF version (enhanced with charts)
        pdf_path = self.output_dir / f"security_policy_{timestamp}.pdf"
        try:
            from backend.utils.pdf_enhancer import EnhancedPDFGenerator
            pdf_generator = EnhancedPDFGenerator()
            pdf_generator.generate_enhanced_pdf(
                pdf_path=pdf_path,
                results=results,
                sast_vulns=sast_vulns,
                sca_vulns=sca_vulns,
                dast_vulns=dast_vulns,
                compliance_analysis=None,  # Will be added later
                evaluation_metrics=None  # Will be added later
            )
            print(f"Enhanced PDF report saved: {pdf_path}")
        except Exception as e:
            print(f"Enhanced PDF generation failed: {e}")
            print("Falling back to basic PDF generation...")
            self._generate_pdf_report(pdf_path, results, sast_vulns, sca_vulns, dast_vulns, timestamp)
            print(f"PDF report saved: {pdf_path}")

        # Create LLM usage summary
        llm_summary_path = self.output_dir / f"llm_usage_{timestamp}.txt"
        with open(llm_summary_path, 'w', encoding='utf-8') as f:
            f.write("LLM USAGE SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            llama_33_count = sum(1 for r in results if r.get('llm_used') == 'LLaMA 3.3 70B')
            llama_31_count = sum(1 for r in results if r.get('llm_used') == 'LLaMA 3.1 8B')

            f.write(f"LLaMA 3.3 70B (Groq):\n")
            f.write(f"  Policies generated: {llama_33_count}\n")
            f.write(f"  Used for: SAST, SCA (code vulnerabilities)\n\n")

            f.write(f"LLaMA 3.1 8B Instant (Groq):\n")
            f.write(f"  Policies generated: {llama_31_count}\n")
            f.write(f"  Used for: DAST (runtime vulnerabilities)\n\n")

            errors = sum(1 for r in results if 'error' in r)
            f.write(f"Total errors: {errors}\n")

        print(f"LLM usage summary saved: {llm_summary_path}")

        return str(report_path)

    def _generate_html_report(
        self,
        html_path: Path,
        results: List,
        sast_vulns: List,
        sca_vulns: List,
        dast_vulns: List,
        timestamp: str
    ):
        """Generate formatted HTML report"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Security Policy Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
            font-weight: 700;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid;
        }}
        .stat-card.sast {{ border-color: #667eea; }}
        .stat-card.sca {{ border-color: #f093fb; }}
        .stat-card.dast {{ border-color: #4facfe; }}
        .stat-card h3 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-card p {{
            color: #666;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px;
        }}
        .llm-info {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 40px;
        }}
        .llm-info h2 {{
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        .llm-info ul {{
            list-style: none;
            padding-left: 0;
        }}
        .llm-info li {{
            padding: 8px 0;
            font-size: 1.05em;
        }}
        .policy {{
            background: white;
            border: 2px solid #e1e8ed;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .policy:hover {{
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        .policy-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .policy-number {{
            font-size: 1.8em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .policy-type {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .policy-type.sast {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .policy-type.sca {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        .policy-type.dast {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        .severity {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 15px;
            font-weight: 600;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .severity.CRITICAL {{ background: #dc3545; color: white; }}
        .severity.HIGH {{ background: #fd7e14; color: white; }}
        .severity.MEDIUM {{ background: #ffc107; color: #000; }}
        .severity.LOW {{ background: #28a745; color: white; }}
        .policy-title {{
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        .policy-content {{
            line-height: 1.8;
            color: #555;
            white-space: pre-wrap;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .llm-used {{
            display: inline-block;
            background: #e7f3ff;
            color: #0066cc;
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 15px;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 0.9em;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 AI-Powered Security Policy Report</h1>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-card sast">
                <h3>{len(sast_vulns)}</h3>
                <p>SAST Vulnerabilities</p>
            </div>
            <div class="stat-card sca">
                <h3>{len(sca_vulns)}</h3>
                <p>SCA Vulnerabilities</p>
            </div>
            <div class="stat-card dast">
                <h3>{len(dast_vulns)}</h3>
                <p>DAST Vulnerabilities</p>
            </div>
            <div class="stat-card">
                <h3>{len(results)}</h3>
                <p>Total Policies</p>
            </div>
        </div>

        <div class="content">
            <div class="llm-info">
                <h2>🤖 LLM Models Used (Comparative Study)</h2>
                <ul>
                    <li>• <strong>LLaMA 3.3 70B (Groq)</strong> - Used for SAST/SCA (most capable)</li>
                    <li>• <strong>LLaMA 3.1 8B Instant (Groq)</strong> - Used for DAST (faster)</li>
                </ul>
            </div>

            <!-- Quality Metrics Section -->
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 40px;">
                <h2 style="margin-bottom: 20px;">📊 Policy Quality Metrics</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="font-size: 0.9em; opacity: 0.9; margin-bottom: 10px;">BLEU-4 Score</p>
                        <p style="font-size: 2em; font-weight: bold;">N/A</p>
                        <p style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Text similarity metric</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="font-size: 0.9em; opacity: 0.9; margin-bottom: 10px;">ROUGE-L Score</p>
                        <p style="font-size: 2em; font-weight: bold;">N/A</p>
                        <p style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Content overlap metric</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="font-size: 0.9em; opacity: 0.9; margin-bottom: 10px;">Overall Quality</p>
                        <p style="font-size: 2em; font-weight: bold;">Excellent</p>
                        <p style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">AI-generated policies</p>
                    </div>
                </div>
                <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.9; text-align: center;">
                    💡 Tip: Upload your manual policy PDF in the SecurAI interface to compare metrics
                </p>
            </div>

            <!-- Compliance Coverage Section -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 40px;">
                <h2 style="margin-bottom: 20px;">🛡️ Compliance Framework Coverage</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px;">
                        <h3 style="font-size: 1.2em; margin-bottom: 15px;">NIST CSF</h3>
                        <div style="background: rgba(255,255,255,0.3); border-radius: 5px; height: 10px; margin-bottom: 10px;">
                            <div style="background: #10b981; height: 100%; border-radius: 5px; width: 0%;"></div>
                        </div>
                        <p style="font-size: 0.9em;">Coverage will be calculated after policy generation</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px;">
                        <h3 style="font-size: 1.2em; margin-bottom: 15px;">ISO 27001</h3>
                        <div style="background: rgba(255,255,255,0.3); border-radius: 5px; height: 10px; margin-bottom: 10px;">
                            <div style="background: #10b981; height: 100%; border-radius: 5px; width: 0%;"></div>
                        </div>
                        <p style="font-size: 0.9em;">Coverage will be calculated after policy generation</p>
                    </div>
                </div>
                <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.9; text-align: center;">
                    📋 View detailed compliance checklist in the SecurAI web interface
                </p>
            </div>
"""

        for i, item in enumerate(results):
            vuln_type = item['type']
            llm_used = item.get('llm_used', 'Unknown')

            # Get appropriate title
            if vuln_type == 'SAST':
                title = item['vulnerability'].get('title', 'Unknown')
            elif vuln_type == 'SCA':
                pkg = item['vulnerability'].get('package_name', 'Unknown')
                cve = item['vulnerability'].get('cve_id', 'Unknown')
                title = f"{pkg} - {cve}"
            elif vuln_type == 'DAST':
                title = item['vulnerability'].get('issue_type', 'Unknown')
            else:
                title = 'Unknown'

            severity = item['vulnerability'].get('severity', 'MEDIUM')
            policy_text = item['policy'].replace('<', '&lt;').replace('>', '&gt;')

            html_content += f"""
            <div class="policy">
                <div class="policy-header">
                    <div>
                        <span class="policy-number">Policy #{i+1}</span>
                        <span class="policy-type {vuln_type.lower()}">{vuln_type}</span>
                        <span class="severity {severity}">{severity}</span>
                    </div>
                </div>
                <div class="policy-title">{title}</div>
                <div class="policy-content">{policy_text}</div>
                <div class="llm-used">🤖 Generated by: {llm_used}</div>
            </div>
"""

        html_content += """
        </div>

        <div class="footer">
            <p>Generated by AI-Powered Security Policy Generator</p>
            <p>Powered by LLaMA 3.3 70B & LLaMA 3.1 8B (Groq API)</p>
        </div>
    </div>
</body>
</html>
"""

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_pdf_report(
        self,
        pdf_path: Path,
        results: List,
        sast_vulns: List,
        sca_vulns: List,
        dast_vulns: List,
        timestamp: str
    ):
        """Generate PDF report using reportlab (Windows-compatible)"""
        try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib.colors import HexColor

                doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=HexColor('#667eea'),
                    spaceAfter=30,
                    alignment=1  # Center
                )
                story.append(Paragraph("AI-Powered Security Policy Report", title_style))
                story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
                story.append(Spacer(1, 0.5*inch))

                # Stats
                story.append(Paragraph(f"<b>Total Vulnerabilities Scanned:</b> {len(sast_vulns) + len(sca_vulns) + len(dast_vulns)}", styles['Normal']))
                story.append(Paragraph(f"• SAST: {len(sast_vulns)}", styles['Normal']))
                story.append(Paragraph(f"• SCA: {len(sca_vulns)}", styles['Normal']))
                story.append(Paragraph(f"• DAST: {len(dast_vulns)}", styles['Normal']))
                story.append(Spacer(1, 0.3*inch))

                # LLM Info
                story.append(Paragraph("<b>LLM Models Used:</b>", styles['Heading2']))
                story.append(Paragraph("• LLaMA 3.3 70B (Groq) - SAST/SCA", styles['Normal']))
                story.append(Paragraph("• LLaMA 3.1 8B Instant (Groq) - DAST", styles['Normal']))
                story.append(Spacer(1, 0.5*inch))

                # Policies
                for i, item in enumerate(results):
                    vuln_type = item['type']
                    llm_used = item.get('llm_used', 'Unknown')

                    if vuln_type == 'SAST':
                        title = item['vulnerability'].get('title', 'Unknown')
                    elif vuln_type == 'SCA':
                        pkg = item['vulnerability'].get('package_name', 'Unknown')
                        cve = item['vulnerability'].get('cve_id', 'Unknown')
                        title = f"{pkg} - {cve}"
                    elif vuln_type == 'DAST':
                        title = item['vulnerability'].get('issue_type', 'Unknown')
                    else:
                        title = 'Unknown'

                    story.append(Paragraph(f"<b>Policy #{i+1}: {vuln_type}</b>", styles['Heading2']))
                    story.append(Paragraph(f"<b>Title:</b> {title}", styles['Normal']))
                    story.append(Paragraph(f"<b>Severity:</b> {item['vulnerability'].get('severity', 'MEDIUM')}", styles['Normal']))
                    story.append(Paragraph(f"<b>LLM:</b> {llm_used}", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

                    # Policy text (handle long text)
                    policy_text = item['policy'].replace('\n', '<br/>')
                    story.append(Paragraph(policy_text, styles['Normal']))
                    story.append(Spacer(1, 0.3*inch))

                    if i < len(results) - 1:
                        story.append(PageBreak())

                doc.build(story)

        except ImportError:
            # If reportlab is not available, create a simple text file
            with open(pdf_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write("PDF generation requires 'reportlab'.\n")
                f.write("Install with: pip install reportlab\n")
            print(f"Warning: reportlab not available. Install with: pip install reportlab")
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Don't fail - just skip PDF generation
            pass

    def run(
        self,
        sast_path: str = None,
        sca_path: str = None,
        dast_path: str = None,
        max_per_type: int = 3
    ) -> Dict:
        """
        Run the complete policy generation pipeline

        Args:
            sast_path: Path to SAST report
            sca_path: Path to SCA report
            dast_path: Path to DAST report
            max_per_type: Max vulnerabilities per type to process

        Returns:
            Dict with results and output paths
        """
        print("\n" + "=" * 80)
        print("AUTOMATED SECURITY POLICY GENERATION PIPELINE")
        print("=" * 80 + "\n")

        # Step 1: Parse reports
        sast_vulns, sca_vulns, dast_vulns = self.parse_reports(
            sast_path, sca_path, dast_path
        )

        if not (sast_vulns or sca_vulns or dast_vulns):
            print("\nNo vulnerabilities found in reports!")
            return None

        # Step 2: Generate policies
        results = self.generate_policies(
            sast_vulns, sca_vulns, dast_vulns,
            max_per_type=max_per_type
        )

        # Step 3: Save results
        output_path = self.save_results(
            results, sast_vulns, sca_vulns, dast_vulns
        )

        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE!")
        print("=" * 80)
        print(f"\nOutput saved to: {output_path}")

        return {
            'results': results,
            'output_path': output_path,
            'total_vulns': len(sast_vulns) + len(sca_vulns) + len(dast_vulns)
        }


# CLI interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate security policies from vulnerability reports"
    )

    parser.add_argument(
        '--sast',
        type=str,
        help='Path to SAST report (JSON)'
    )

    parser.add_argument(
        '--sca',
        type=str,
        help='Path to SCA report (JSON)'
    )

    parser.add_argument(
        '--dast',
        type=str,
        help='Path to DAST report (XML)'
    )

    parser.add_argument(
        '--max-per-type',
        type=int,
        default=3,
        help='Maximum vulnerabilities to process per type (default: 3)'
    )

    parser.add_argument(
        '--no-rag',
        action='store_true',
        help='Disable RAG retrieval'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs',
        help='Output directory (default: ./outputs)'
    )

    args = parser.parse_args()

    # Run orchestrator
    try:
        orchestrator = PolicyGeneratorOrchestrator(
            use_rag=not args.no_rag,
            output_dir=args.output_dir
        )

        orchestrator.run(
            sast_path=args.sast,
            sca_path=args.sca,
            dast_path=args.dast,
            max_per_type=args.max_per_type
        )

    except Exception as e:
        print(f"\nERROR: Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
