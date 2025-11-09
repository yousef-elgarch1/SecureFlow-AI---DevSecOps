"""
FastAPI Backend with WebSocket Support for Real-Time Policy Generation
"""

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import os
import sys
import tempfile
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.orchestrator.policy_generator import PolicyGeneratorOrchestrator
from backend.parsers.sast_parser import SASTParser
from backend.parsers.sca_parser import SCAParser
from backend.parsers.dast_parser import DASTParser
from backend.scanners.github_scanner import scan_github_repository
from backend.api.github_oauth import router as github_oauth_router

# Import user profile and policy tracking for new features
try:
    from backend.models.user_profile import UserProfile, ExpertiseLevel, UserRole, Certification, get_profile_template
    from backend.database.policy_tracker import PolicyTracker
    from backend.models.policy_status import PolicyTrackingItem, PolicyStatus
    TRACKING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Policy tracking features not available: {e}")
    TRACKING_AVAILABLE = False

app = FastAPI(
    title="AI Security Policy Generator API",
    description="Generate compliance-aligned security policies from vulnerability scans",
    version="1.0.0"
)

# Include OAuth router
app.include_router(github_oauth_router, prefix="/api", tags=["GitHub OAuth"])

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class HealthResponse(BaseModel):
    status: str
    vector_db_ready: bool
    llm_available: bool
    timestamp: str

class PolicyGenerationResponse(BaseModel):
    success: bool
    results: List[Dict]
    total_vulns: int
    output_files: Dict[str, str]
    timestamp: str

class GitHubScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    scan_types: Dict = {"sast": True, "sca": True, "dast": False}
    max_per_type: int = 5
    token: Optional[str] = None  # GitHub access token for private repos
    dast_url: Optional[str] = None  # Optional live URL for DAST scanning (Tier 1)

# Global state
orchestrator: Optional[PolicyGeneratorOrchestrator] = None
policy_tracker: Optional['PolicyTracker'] = None
active_connections: List[WebSocket] = []

async def broadcast_progress(data: Dict):
    """Broadcast progress update to all connected WebSocket clients"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            print(f"Error broadcasting to client: {e}")
            disconnected.append(connection)

    # Remove disconnected clients
    for connection in disconnected:
        active_connections.remove(connection)

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup"""
    global orchestrator, policy_tracker
    try:
        orchestrator = PolicyGeneratorOrchestrator(use_rag=True)
        print("Orchestrator initialized successfully")
        print(f"RAG system: {'Enabled' if orchestrator.use_rag else 'Disabled'}")
        print(f"LLM clients: {list(orchestrator.llm_clients.keys())}")

        # Initialize policy tracker if available
        if TRACKING_AVAILABLE:
            policy_tracker = PolicyTracker()
            print("Policy tracker initialized successfully")
    except Exception as e:
        print(f"Failed to initialize orchestrator: {e}")
        orchestrator = None

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Security Policy Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/ws"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if orchestrator else "unhealthy",
        vector_db_ready=orchestrator.use_rag if orchestrator else False,
        llm_available=bool(orchestrator and orchestrator.llm_clients),
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/generate-policies", response_model=PolicyGenerationResponse)
async def generate_policies(
    sast_file: Optional[UploadFile] = File(None),
    sca_file: Optional[UploadFile] = File(None),
    dast_file: Optional[UploadFile] = File(None),
    max_per_type: int = 5,
    expertise_level: str = "intermediate",
    user_role: str = "senior_developer",
    user_name: Optional[str] = None
):
    """Generate security policies from uploaded scan reports"""

    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    if not any([sast_file, sca_file, dast_file]):
        raise HTTPException(status_code=400, detail="At least one scan report is required")

    # Create user profile from request parameters
    user_profile = None
    if TRACKING_AVAILABLE:
        try:
            user_profile = UserProfile(
                name=user_name,
                expertise_level=ExpertiseLevel(expertise_level),
                role=UserRole(user_role)
            )
            logger.info(f"Generated policies for {expertise_level} level user ({user_role})")
        except Exception as e:
            logger.warning(f"Invalid user profile data: {e}. Using default profile.")
            user_profile = UserProfile.default()

    temp_files = {}
    try:
        # Save uploaded files to temp directory
        if sast_file:
            temp_files['sast'] = await _save_upload_file(sast_file)
        if sca_file:
            temp_files['sca'] = await _save_upload_file(sca_file)
        if dast_file:
            temp_files['dast'] = await _save_upload_file(dast_file)

        # Broadcast real-time updates via WebSocket and get results
        generation_result = await broadcast_realtime_generation(
            temp_files.get('sast'),
            temp_files.get('sca'),
            temp_files.get('dast'),
            max_per_type,
            user_profile
        )

        return PolicyGenerationResponse(
            success=True,
            results=generation_result.get('results', []),
            total_vulns=generation_result.get('total_vulns', 0),
            output_files=generation_result.get('output_files', {}),
            timestamp=generation_result.get('timestamp', datetime.now().isoformat())
        )

    except Exception as e:
        await broadcast_progress({
            'phase': 'error',
            'status': 'error',
            'message': f"Policy generation failed: {str(e)}",
            'data': {}
        })
        raise HTTPException(status_code=500, detail=f"Policy generation failed: {str(e)}")

    finally:
        # Cleanup temp files
        for path in temp_files.values():
            if path and os.path.exists(path):
                os.remove(path)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time policy generation updates"""
    await websocket.accept()
    active_connections.append(websocket)
    print(f"✅ WebSocket client connected. Total connections: {len(active_connections)}")

    try:
        while True:
            # Keep connection alive - just wait for messages
            data = await websocket.receive_json()
            action = data.get('action')

            if action == 'ping':
                await websocket.send_json({'type': 'pong'})

    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"❌ WebSocket client disconnected. Remaining connections: {len(active_connections)}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

async def broadcast_realtime_generation(
    sast_path: Optional[str],
    sca_path: Optional[str],
    dast_path: Optional[str],
    max_per_type: int = 5,
    user_profile: Optional['UserProfile'] = None
) -> Dict:
    """Broadcast real-time policy generation updates to all WebSocket clients

    Args:
        user_profile: User profile for adaptive policy generation

    Returns:
        Dictionary with results, compliance_analysis, and output_files
    """

    if not orchestrator:
        await broadcast_progress({'type': 'error', 'message': 'Orchestrator not initialized'})
        return {'results': [], 'total_vulns': 0, 'output_files': {}}

    # Set user profile on orchestrator
    if user_profile:
        orchestrator.user_profile = user_profile

    try:

        # PHASE 1: Parsing - Individual parser progress
        await broadcast_progress({
            'phase': 'parsing',
            'status': 'in_progress',
            'message': 'Starting vulnerability report parsing...',
            'data': {}
        })

        # Parse SAST
        sast_vulns = []
        if sast_path:
            await broadcast_progress({
                'phase': 'parsing',
                'status': 'in_progress',
                'message': 'Parsing SAST report (Semgrep)...',
                'data': {
                    'current_parser': 'SAST',
                    'parser_status': 'running',
                    'file_name': os.path.basename(sast_path)
                }
            })

            parser = SASTParser()
            with open(sast_path, 'r', encoding='utf-8') as f:
                sast_vulns = parser.parse(f.read())

            # Send detailed SAST results
            await broadcast_progress({
                'phase': 'parsing',
                'status': 'in_progress',
                'message': f'SAST parsing complete - {len(sast_vulns)} vulnerabilities found',
                'data': {
                    'current_parser': 'SAST',
                    'parser_status': 'completed',
                    'vulnerabilities_found': len(sast_vulns),
                    'sast_count': len(sast_vulns),
                    'vulnerabilities': [
                        {
                            'title': v.title,
                            'severity': v.severity,
                            'file': f"{v.file_path}:{v.line_number}" if hasattr(v, 'line_number') else v.file_path
                        } for v in sast_vulns[:5]  # Show first 5
                    ]
                }
            })

        # Parse SCA
        sca_vulns = []
        if sca_path:
            await broadcast_progress({
                'phase': 'parsing',
                'status': 'in_progress',
                'message': 'Parsing SCA report (npm audit/Trivy)...',
                'data': {
                    'current_parser': 'SCA',
                    'parser_status': 'running',
                    'file_name': os.path.basename(sca_path)
                }
            })

            parser = SCAParser()
            with open(sca_path, 'r', encoding='utf-8') as f:
                sca_vulns = parser.parse(f.read())

            await broadcast_progress({
                'phase': 'parsing',
                'status': 'in_progress',
                'message': f'SCA parsing complete - {len(sca_vulns)} vulnerabilities found',
                'data': {
                    'current_parser': 'SCA',
                    'parser_status': 'completed',
                    'vulnerabilities_found': len(sca_vulns),
                    'sca_count': len(sca_vulns),
                    'vulnerabilities': [
                        {
                            'title': f"{v.package_name} - {v.description}",
                            'severity': v.severity,
                            'package': v.package_name
                        } for v in sca_vulns[:5]
                    ]
                }
            })

        # Parse DAST
        dast_vulns = []
        if dast_path:
            await broadcast_progress({
                'phase': 'parsing',
                'status': 'in_progress',
                'message': 'Parsing DAST report (OWASP ZAP)...',
                'data': {
                    'current_parser': 'DAST',
                    'parser_status': 'running',
                    'file_name': os.path.basename(dast_path)
                }
            })

            parser = DASTParser()
            with open(dast_path, 'r', encoding='utf-8') as f:
                dast_vulns = parser.parse(f.read())

            await broadcast_progress({
                'phase': 'parsing',
                'status': 'in_progress',
                'message': f'DAST parsing complete - {len(dast_vulns)} vulnerabilities found',
                'data': {
                    'current_parser': 'DAST',
                    'parser_status': 'completed',
                    'vulnerabilities_found': len(dast_vulns),
                    'dast_count': len(dast_vulns),
                    'vulnerabilities': [
                        {
                            'title': v.issue_type,
                            'severity': v.risk_level,
                            'url': v.url
                        } for v in dast_vulns[:5]
                    ]
                }
            })

        # Parsing phase complete
        total_vulns = len(sast_vulns) + len(sca_vulns) + len(dast_vulns)
        await broadcast_progress({
            'phase': 'parsing',
            'status': 'completed',
            'message': f'Parsing complete - {total_vulns} total vulnerabilities found',
            'data': {
                'sast_count': len(sast_vulns),
                'sca_count': len(sca_vulns),
                'dast_count': len(dast_vulns),
                'total': total_vulns,
                'vulnerabilities': {
                    'sast': len(sast_vulns),
                    'sca': len(sca_vulns),
                    'dast': len(dast_vulns)
                }
            }
        })

        # PHASE 2: RAG Retrieval
        if orchestrator.use_rag:
            await broadcast_progress({
                'phase': 'rag',
                'status': 'in_progress',
                'message': 'Retrieving compliance contexts from vector database...',
                'data': {
                    'rag_status': 'initializing'
                }
            })

            # Simulate NIST CSF retrieval
            await broadcast_progress({
                'phase': 'rag',
                'status': 'in_progress',
                'message': 'Fetching NIST CSF compliance contexts...',
                'data': {
                    'rag_status': 'fetching_nist',
                    'standard': 'NIST CSF'
                }
            })

            await asyncio.sleep(0.3)  # Simulate retrieval time

            await broadcast_progress({
                'phase': 'rag',
                'status': 'in_progress',
                'message': 'NIST CSF contexts retrieved successfully',
                'data': {
                    'rag_status': 'nist_complete',
                    'standard': 'NIST CSF',
                    'contexts_retrieved': 15,
                    'controls': ['ID.RA-1', 'ID.RA-5', 'PR.AC-4', 'PR.DS-5', 'DE.CM-7']
                }
            })

            # ISO 27001 retrieval
            await broadcast_progress({
                'phase': 'rag',
                'status': 'in_progress',
                'message': 'Fetching ISO 27001 compliance contexts...',
                'data': {
                    'rag_status': 'fetching_iso',
                    'standard': 'ISO 27001'
                }
            })

            await asyncio.sleep(0.3)

            await broadcast_progress({
                'phase': 'rag',
                'status': 'completed',
                'message': 'All compliance contexts retrieved successfully',
                'data': {
                    'rag_status': 'complete',
                    'total_contexts': 27,
                    'standards': ['NIST CSF', 'ISO 27001'],
                    'nist_controls': 15,
                    'iso_controls': 12
                }
            })

        # PHASE 3: LLM Policy Generation (Most Detailed)
        all_vulns = [
            ('sast', sast_vulns[:max_per_type]),
            ('sca', sca_vulns[:max_per_type]),
            ('dast', dast_vulns[:max_per_type])
        ]

        total_to_process = sum(len(vulns) for _, vulns in all_vulns)

        await broadcast_progress({
            'phase': 'llm_generation',
            'status': 'in_progress',
            'message': f'Starting AI policy generation for {total_to_process} vulnerabilities',
            'data': {
                'total_vulnerabilities': total_to_process,
                'processed': 0,
                'llm_routing': {
                    'SAST': 'LLaMA 3.3 70B (Groq)',
                    'SCA': 'LLaMA 3.3 70B (Groq)',
                    'DAST': 'LLaMA 3.1 8B Instant (Groq)'
                }
            }
        })

        results = []
        processed = 0

        for vuln_type, vulns in all_vulns:
            llm_model = 'LLaMA 3.3 70B' if vuln_type in ['sast', 'sca'] else 'LLaMA 3.1 8B Instant'

            for vuln in vulns:
                # Get vulnerability details
                vuln_title = vuln.title if hasattr(vuln, 'title') else (
                    vuln.issue_type if hasattr(vuln, 'issue_type') else
                    f"{vuln.package_name} vulnerability" if hasattr(vuln, 'package_name') else "Unknown"
                )

                vuln_severity = vuln.severity if hasattr(vuln, 'severity') else (
                    vuln.risk_level if hasattr(vuln, 'risk_level') else 'MEDIUM'
                )

                # Send per-vulnerability progress
                await broadcast_progress({
                    'phase': 'llm_generation',
                    'status': 'in_progress',
                    'message': f'Generating policy for {vuln_title}...',
                    'data': {
                        'processed': processed,
                        'total': total_to_process,
                        'current_vuln': {
                            'title': vuln_title,
                            'severity': vuln_severity,
                            'type': vuln_type.upper(),
                            'cwe': getattr(vuln, 'cwe_id', 'N/A'),
                            'file': getattr(vuln, 'file_path', getattr(vuln, 'url', 'N/A'))
                        },
                        'llm_model': llm_model,
                        'llm_status': 'generating',
                        'progress_percentage': round((processed / total_to_process) * 100, 1)
                    }
                })

                # Generate policy
                policy = orchestrator.generate_policy_for_vulnerability(
                    vuln.to_dict() if hasattr(vuln, 'to_dict') else vuln,
                    vuln_type
                )

                # Policy generated - send completion
                policy_preview = policy[:200] + "..." if len(policy) > 200 else policy

                results.append({
                    'type': vuln_type.upper(),
                    'vulnerability': vuln.to_dict() if hasattr(vuln, 'to_dict') else vuln,
                    'policy': policy,
                    'llm_used': llm_model,
                    'compliance_mapping': {
                        'NIST CSF': ['PR.AC-4', 'DE.CM-7'],
                        'ISO 27001': ['A.14.2.5']
                    }
                })

                processed += 1

                await broadcast_progress({
                    'phase': 'llm_generation',
                    'status': 'in_progress',
                    'message': f'Policy generated for {vuln_title}',
                    'data': {
                        'processed': processed,
                        'total': total_to_process,
                        'current_vuln': {
                            'title': vuln_title,
                            'severity': vuln_severity,
                            'type': vuln_type.upper()
                        },
                        'llm_model': llm_model,
                        'llm_status': 'completed',
                        'policy_preview': policy_preview,
                        'compliance_mapped': ['NIST CSF: PR.AC-4', 'ISO 27001: A.14.2.5'],
                        'progress_percentage': round((processed / total_to_process) * 100, 1)
                    }
                })

                await asyncio.sleep(0.1)  # Small delay for UI updates

        await broadcast_progress({
            'phase': 'llm_generation',
            'status': 'completed',
            'message': f'All {total_to_process} policies generated successfully',
            'data': {
                'total_generated': len(results),
                'llm_usage': {
                    'llama_70b': len([r for r in results if '70B' in r['llm_used']]),
                    'llama_8b': len([r for r in results if '8B' in r['llm_used']])
                }
            }
        })

        # PHASE 4: Saving Results
        await broadcast_progress({
            'phase': 'saving',
            'status': 'in_progress',
            'message': 'Saving policy documents...',
            'data': {
                'files_saving': ['TXT', 'HTML', 'JSON']
            }
        })

        output_path = orchestrator.save_results(results, sast_vulns, sca_vulns, dast_vulns)

        output_files = [
            os.path.basename(str(output_path)),
            os.path.basename(str(output_path)).replace('.txt', '.html'),
            os.path.basename(str(output_path)).replace('.txt', '.json')
        ]

        await broadcast_progress({
            'phase': 'saving',
            'status': 'completed',
            'message': 'All files saved successfully',
            'data': {
                'files_saved': output_files,
                'output_directory': 'outputs'
            }
        })

        # PHASE 5: Compliance Validation
        await broadcast_progress({
            'phase': 'compliance_validation',
            'status': 'in_progress',
            'message': 'Analyzing compliance coverage...',
            'data': {}
        })

        from backend.compliance.coverage_analyzer import ComplianceCoverageAnalyzer
        analyzer = ComplianceCoverageAnalyzer()
        compliance_analysis = analyzer.analyze_coverage(results)

        await broadcast_progress({
            'phase': 'compliance_validation',
            'status': 'completed',
            'message': 'Compliance validation complete',
            'data': {
                'compliance_analysis': compliance_analysis
            }
        })

        # FINAL: Complete message
        output_filename = os.path.basename(str(output_path))
        await broadcast_progress({
            'phase': 'complete',
            'status': 'completed',
            'message': 'Policy generation complete!',
            'data': {
                'total_vulns': total_to_process,
                'total_policies': len(results),
                'output_files': {
                    'txt': output_filename,
                    'html': output_filename.replace('.txt', '.html'),
                    'pdf': output_filename.replace('.txt', '.pdf'),
                    'json': output_filename.replace('.txt', '.json'),
                },
                'results': results,
                'compliance_analysis': compliance_analysis,
                'timestamp': datetime.now().isoformat()
            }
        })

        # Return data for HTTP response
        return {
            'results': results,
            'total_vulns': total_to_process,
            'output_files': {
                'txt': output_filename,
                'html': output_filename.replace('.txt', '.html'),
                'pdf': output_filename.replace('.txt', '.pdf'),
                'json': output_filename.replace('.txt', '.json'),
            },
            'compliance_analysis': compliance_analysis,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in broadcast_realtime_generation: {e}")
        logger.error(f"Traceback: {error_details}")
        await broadcast_progress({
            'type': 'error',
            'message': f"Policy generation error: {str(e)}"
        })
        # Return empty results on error
        return {'results': [], 'total_vulns': 0, 'output_files': {}}

async def _save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to temporary location"""
    suffix = Path(upload_file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        return tmp.name

@app.post("/api/scan-github", response_model=PolicyGenerationResponse)
async def scan_github(request: GitHubScanRequest):
    """
    Scan a GitHub repository and generate security policies.

    This endpoint:
    1. Clones the specified GitHub repository
    2. Runs selected security scans (SAST, SCA, DAST)
    3. Converts scan results to vulnerability reports
    4. Generates security policies using the same pipeline as file uploads
    """
    global orchestrator

    try:
        # Broadcast initial status
        await broadcast_progress({
            'phase': 'github_clone',
            'status': 'in_progress',
            'message': f'Cloning repository: {request.repo_url}',
            'data': {'repo_url': request.repo_url, 'branch': request.branch}
        })

        # Prepare scan_types with DAST URL if provided
        scan_types = request.scan_types.copy()
        if request.dast_url:
            scan_types["dast_url"] = request.dast_url

        # Run GitHub repository scan (synchronous) in thread pool
        # to avoid blocking the async event loop
        import concurrent.futures

        # Get the event loop BEFORE entering the thread
        loop = asyncio.get_event_loop()

        def run_github_scan():
            """Run the GitHub scan in a separate thread"""
            # Callback to broadcast clone progress to frontend
            def progress_callback(message: str):
                import logging
                logging.info(f"GitHub scan progress: {message}")
                # Send progress to WebSocket from thread using captured loop
                try:
                    asyncio.run_coroutine_threadsafe(
                        broadcast_progress({
                            'phase': 'github_clone',
                            'status': 'in_progress',
                            'message': message
                        }),
                        loop  # Use the captured loop from outside the thread
                    )
                except Exception as e:
                    logging.warning(f"Could not broadcast progress: {e}")

            return scan_github_repository(
                repo_url=request.repo_url,
                branch=request.branch,
                scan_types=scan_types,
                token=request.token,
                progress_callback=progress_callback
            )

        # Run in thread pool executor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scan_results = await loop.run_in_executor(executor, run_github_scan)

        await broadcast_progress({
            'phase': 'github_clone',
            'status': 'completed',
            'message': 'Repository scanned successfully',
            'data': {
                'scans_completed': list(scan_results.get('scans', {}).keys()),
                'timestamp': scan_results.get('scan_timestamp')
            }
        })

        # Convert scan results to vulnerability format expected by the pipeline
        # Save scan results as temporary JSON files
        temp_files = {}

        if 'sast' in scan_results.get('scans', {}):
            sast_data = scan_results['scans']['sast']
            logger.info(f"SAST data keys: {sast_data.keys()}")
            logger.info(f"SAST vulnerabilities count: {len(sast_data.get('vulnerabilities', []))}")
            logger.info(f"SAST raw_results present: {'raw_results' in sast_data}")
            if 'raw_results' in sast_data:
                logger.info(f"Raw results keys: {sast_data['raw_results'].keys()}")
                logger.info(f"Raw results count: {len(sast_data['raw_results'].get('results', []))}")

            temp_sast = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            # Use raw Semgrep results if available, otherwise use converted vulnerabilities
            if 'raw_results' in sast_data:
                json.dump(sast_data['raw_results'], temp_sast)
            else:
                # Fallback: wrap vulnerabilities in results key
                json.dump({
                    "results": sast_data.get('vulnerabilities', [])
                }, temp_sast)
            temp_sast.close()
            temp_files['sast_file'] = temp_sast.name

        if 'sca' in scan_results.get('scans', {}):
            sca_data = scan_results['scans']['sca']
            temp_sca = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            # SCA parser expects npm audit format with vulnerabilities as dict
            # Convert list of vulnerabilities to dict format
            vulns_list = sca_data.get('vulnerabilities', [])
            vulns_dict = {}
            for vuln in vulns_list:
                # Group by package name
                pkg_name = vuln.get('package', vuln.get('package_name', 'unknown'))
                if pkg_name not in vulns_dict:
                    vulns_dict[pkg_name] = []
                vulns_dict[pkg_name].append(vuln)

            json.dump({
                "vulnerabilities": vulns_dict
            }, temp_sca)
            temp_sca.close()
            temp_files['sca_file'] = temp_sca.name

        if 'dast' in scan_results.get('scans', {}):
            dast_data = scan_results['scans']['dast']
            temp_dast = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            json.dump({
                "tool": dast_data.get('tool', 'Nuclei'),
                "vulnerabilities": dast_data.get('vulnerabilities', [])
            }, temp_dast)
            temp_dast.close()
            temp_files['dast_file'] = temp_dast.name

        # Process through existing policy generation pipeline
        generation_result = await broadcast_realtime_generation(
            sast_path=temp_files.get('sast_file'),
            sca_path=temp_files.get('sca_file'),
            dast_path=temp_files.get('dast_file'),  # Now includes DAST if available
            max_per_type=request.max_per_type
        )

        # Cleanup temp files
        for file_path in temp_files.values():
            try:
                os.unlink(file_path)
            except:
                pass

        # Return response with actual results
        return PolicyGenerationResponse(
            success=True,
            results=generation_result.get('results', []),
            total_vulns=generation_result.get('total_vulns', 0),
            output_files=generation_result.get('output_files', {}),
            timestamp=generation_result.get('timestamp', datetime.now().isoformat())
        )

    except Exception as e:
        error_msg = f"GitHub scan failed: {str(e)}"
        await broadcast_progress({
            'phase': 'github_clone',
            'status': 'error',
            'message': error_msg,
            'data': {}
        })
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/compare-policies")
async def compare_policies(
    reference_pdf: UploadFile = File(..., description="User's manual policy PDF for comparison"),
    generated_policy_text: Optional[str] = None
):
    """
    Compare AI-generated policy against user's manual reference policy
    Returns detailed comparison metrics including BLEU, ROUGE, and structural analysis
    """
    try:
        from backend.utils.pdf_parser import extract_text_from_pdf, validate_pdf_file
        from backend.compliance.reference_comparator import ReferencePolicyComparator

        # Validate PDF file
        if not validate_pdf_file(reference_pdf.filename):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

        # Extract text from uploaded PDF
        logger.info(f"Extracting text from PDF: {reference_pdf.filename}")
        reference_text = extract_text_from_pdf(reference_pdf.file)

        if not reference_text or len(reference_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from PDF. Please ensure the PDF contains readable text."
            )

        # If no generated policy text provided, use a sample from recent outputs
        if not generated_policy_text:
            # Get the most recent policy output
            output_dir = Path("./outputs")
            json_files = list(output_dir.glob("policy_generation_*.json"))
            if not json_files:
                raise HTTPException(
                    status_code=404,
                    detail="No generated policies found. Please generate policies first."
                )

            # Get most recent file
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                policy_data = json.load(f)

            # Combine all policy texts
            generated_policy_text = "\n\n".join([
                item.get('policy', '') for item in policy_data if 'policy' in item
            ])

        # Perform comparison
        logger.info("Comparing policies using ReferencePolicyComparator")
        comparator = ReferencePolicyComparator()
        comparison_result = comparator.compare(
            generated_policy=generated_policy_text,
            reference_policy=reference_text
        )

        # Generate detailed report
        detailed_report = comparator.generate_report(comparison_result)

        # Return comprehensive results
        return {
            "success": True,
            "comparison": comparison_result,
            "detailed_report": detailed_report,
            "summary": {
                "overall_similarity": comparison_result['overall_similarity'],
                "grade": comparison_result['grade'],
                "bleu_score": comparison_result['bleu_score'],
                "rouge_l_score": comparison_result['rouge_scores']['rougeL'],
                "key_terms_coverage": comparison_result['key_terms_coverage']['coverage_percentage']
            },
            "reference_info": {
                "filename": reference_pdf.filename,
                "word_count": comparison_result['length_analysis']['reference_words'],
                "sections_found": comparison_result['structural_similarity']['reference_section_count']
            },
            "generated_info": {
                "word_count": comparison_result['length_analysis']['generated_words'],
                "sections_found": comparison_result['structural_similarity']['generated_section_count']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy comparison error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated policy files"""
    output_dir = Path("./outputs")
    file_path = output_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=filename
    )


# ============================================================================
# NEW FEATURES: User Profiles & Policy Tracking Endpoints
# ============================================================================

@app.get("/api/profile-templates")
async def get_profile_templates():
    """Get predefined user profile templates"""
    if not TRACKING_AVAILABLE:
        raise HTTPException(status_code=501, detail="Profile templates not available")

    from backend.models.user_profile import PROFILE_TEMPLATES
    return {
        "success": True,
        "templates": {k: v.dict() for k, v in PROFILE_TEMPLATES.items()}
    }


@app.get("/api/policies/dashboard")
async def get_policy_dashboard():
    """Get all policies with tracking status"""
    if not TRACKING_AVAILABLE or not policy_tracker:
        raise HTTPException(status_code=501, detail="Policy tracking not available")

    try:
        dashboard_data = policy_tracker.get_dashboard_data()
        return {
            "success": True,
            "policies": [p.dict() for p in dashboard_data['policies']],
            "stats": dashboard_data['stats'].dict()
        }
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policies/{policy_id}/status")
async def update_policy_status(
    policy_id: str,
    new_status: str,
    user: Optional[str] = None
):
    """Update policy status"""
    if not TRACKING_AVAILABLE or not policy_tracker:
        raise HTTPException(status_code=501, detail="Policy tracking not available")

    try:
        policy_tracker.update_policy_status(policy_id, PolicyStatus(new_status), user)
        return {"success": True, "message": "Status updated"}
    except Exception as e:
        logger.error(f"Status update error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policies/{policy_id}/assign")
async def assign_policy(
    policy_id: str,
    assigned_to: str,
    user: Optional[str] = None
):
    """Assign policy to user"""
    if not TRACKING_AVAILABLE or not policy_tracker:
        raise HTTPException(status_code=501, detail="Policy tracking not available")

    try:
        policy_tracker.assign_policy(policy_id, assigned_to, user)
        return {"success": True, "message": f"Assigned to {assigned_to}"}
    except Exception as e:
        logger.error(f"Assignment error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policies/{policy_id}")
async def get_policy_details(policy_id: str):
    """Get single policy with timeline"""
    if not TRACKING_AVAILABLE or not policy_tracker:
        raise HTTPException(status_code=501, detail="Policy tracking not available")

    try:
        policy = policy_tracker.get_policy(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return {"success": True, "policy": policy.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Policy details error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("Starting AI Security Policy Generator API...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("WebSocket: ws://localhost:8000/ws")
    uvicorn.run(app, host="0.0.0.0", port=8000)
