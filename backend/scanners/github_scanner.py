"""
GitHub Repository Scanner
Clones and scans GitHub repositories for security vulnerabilities.
"""

import os
import shutil
import subprocess
import tempfile
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubScanner:
    """Handles cloning and scanning of GitHub repositories."""

    def __init__(self):
        self.temp_dir = None
        self.repo_path = None

    def clone_repository(self, repo_url: str, branch: str = "main", token: Optional[str] = None, progress_callback=None) -> Path:
        """
        Clone a GitHub repository to a temporary directory.

        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
            branch: Branch to clone (default: main)
            token: Optional GitHub access token for private repositories
            progress_callback: Optional callback function to report progress

        Returns:
            Path to cloned repository
        """
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="github_scan_")
            logger.info(f"Created temp directory: {self.temp_dir}")

            if progress_callback:
                progress_callback(f"Created temporary directory: {self.temp_dir}")

            # Extract repo name from URL
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            self.repo_path = Path(self.temp_dir) / repo_name

            # Build authenticated URL if token provided
            clone_url = repo_url
            if token:
                # Convert https://github.com/user/repo to https://TOKEN@github.com/user/repo
                if clone_url.startswith('https://github.com/'):
                    clone_url = clone_url.replace('https://github.com/', f'https://{token}@github.com/')
                    logger.info(f"Using authenticated clone for private repository")
                else:
                    logger.warning(f"Token provided but URL format not recognized: {repo_url}")

            # Clone repository with progress - try up to 3 times
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Cloning {repo_url} (branch: {branch}) - Attempt {attempt}/{max_retries}...")
                    if progress_callback:
                        progress_callback(f"Cloning repository (attempt {attempt}/{max_retries})...")
                        progress_callback(f"This may take several minutes for large repositories...")

                    # Use git clone without capture_output to show progress
                    # Increase timeout to 15 minutes for large repos
                    result = subprocess.run(
                        ["git", "clone", "--depth", "1", "--branch", branch, "--progress", clone_url, str(self.repo_path)],
                        capture_output=True,
                        text=True,
                        timeout=900  # 15 minute timeout (increased from 5)
                    )

                    if result.returncode == 0:
                        logger.info(f"Successfully cloned repository to {self.repo_path}")
                        if progress_callback:
                            progress_callback(f"Successfully cloned to: {self.repo_path}")
                        return self.repo_path
                    else:
                        error_msg = result.stderr
                        logger.warning(f"Clone attempt {attempt} failed: {error_msg}")

                        if attempt < max_retries:
                            if progress_callback:
                                progress_callback(f"Clone attempt {attempt} failed, retrying...")
                            # Clean up failed clone
                            if self.repo_path.exists():
                                shutil.rmtree(self.repo_path, ignore_errors=True)
                            continue
                        else:
                            raise Exception(f"Git clone failed after {max_retries} attempts: {error_msg}")

                except subprocess.TimeoutExpired:
                    logger.warning(f"Clone attempt {attempt} timed out after 15 minutes")
                    if attempt < max_retries:
                        if progress_callback:
                            progress_callback(f"Clone attempt {attempt} timed out, retrying...")
                        # Clean up failed clone
                        if self.repo_path.exists():
                            shutil.rmtree(self.repo_path, ignore_errors=True)
                        continue
                    else:
                        raise Exception(f"Repository clone timeout after {max_retries} attempts (>15 minutes each)")

        except Exception as e:
            self.cleanup()
            error_msg = str(e)
            logger.error(f"Failed to clone repository: {error_msg}")

            # Provide helpful error message
            if "invalid index-pack output" in error_msg or "fetch-pack" in error_msg:
                raise Exception(
                    f"Git clone failed due to network issues or repository size. "
                    f"The repository may be too large. Try a smaller repository first. "
                    f"Original error: {error_msg}"
                )
            else:
                raise Exception(f"Failed to clone repository: {error_msg}")

    def cleanup(self):
        """Remove temporary directory and cloned repository."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                # On Windows, .git files can be locked. Use onerror handler
                def handle_remove_readonly(func, path, exc):
                    """Error handler for Windows readonly files"""
                    import stat
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR)
                        func(path)
                    else:
                        raise

                shutil.rmtree(self.temp_dir, onerror=handle_remove_readonly)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}. Will retry on next run.")

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()


class SemgrepScanner:
    """Wrapper for Semgrep SAST scanning."""

    @staticmethod
    def scan(repo_path: Path) -> Dict:
        """
        Run Semgrep scan on repository.

        Args:
            repo_path: Path to repository to scan

        Returns:
            Dictionary with scan results in our format
        """
        try:
            logger.info(f"Running Semgrep scan on {repo_path}...")

            # Try to find semgrep executable
            import shutil
            semgrep_path = shutil.which("semgrep")
            if not semgrep_path:
                logger.warning("Semgrep not found in PATH, trying venv...")
                # Try venv location
                venv_semgrep = Path(__file__).parent.parent.parent / "venv" / "Scripts" / "semgrep.exe"
                if venv_semgrep.exists():
                    semgrep_path = str(venv_semgrep)
                else:
                    raise Exception("Semgrep executable not found. Please ensure it's installed.")

            logger.info(f"Using Semgrep at: {semgrep_path}")

            # Set environment to handle Unicode properly on Windows
            import os
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'

            # Run semgrep with JSON output
            # Using p/security-audit instead of --config=auto to avoid Windows encoding issues
            result = subprocess.run(
                [
                    semgrep_path,
                    "--config=p/security-audit",  # Security-focused ruleset
                    "--json",
                    str(repo_path)
                ],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env=env,
                encoding='utf-8',
                errors='replace'  # Replace problematic characters instead of failing
            )

            # Semgrep returns 0 for success, 1 for findings, >1 for errors
            logger.info(f"Semgrep return code: {result.returncode}")
            logger.info(f"Semgrep stderr: {result.stderr[:1000] if result.stderr else 'None'}")
            logger.info(f"Semgrep stdout length: {len(result.stdout) if result.stdout else 0}")

            if result.returncode > 1:
                error_msg = result.stderr if result.stderr else f"Return code: {result.returncode}"
                logger.error(f"Semgrep scan failed with return code {result.returncode}")
                logger.error(f"Semgrep error output: {result.stderr}")
                logger.error(f"Semgrep stdout: {result.stdout[:500] if result.stdout else 'None'}")

                # Return empty results instead of raising exception
                logger.warning("Returning empty SAST results due to Semgrep error")
                return {
                    "tool": "Semgrep",
                    "scan_type": "SAST",
                    "timestamp": datetime.now().isoformat(),
                    "vulnerabilities": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                    "error": error_msg
                }

            # Parse JSON output
            if not result.stdout:
                logger.warning("Semgrep returned no output, assuming no vulnerabilities found")
                scan_results = {"results": []}
            else:
                try:
                    scan_results = json.loads(result.stdout)
                except json.JSONDecodeError as je:
                    logger.error(f"Failed to parse Semgrep JSON output: {je}")
                    logger.error(f"Semgrep stdout: {result.stdout[:500]}")
                    scan_results = {"results": []}

            # Convert to our format
            vulnerabilities = []
            for finding in scan_results.get("results", []):
                vuln = {
                    "title": finding.get("check_id", "Unknown vulnerability"),
                    "severity": finding.get("extra", {}).get("severity", "MEDIUM").upper(),
                    "description": finding.get("extra", {}).get("message", "No description"),
                    "file": finding.get("path", ""),
                    "line": finding.get("start", {}).get("line", 0),
                    "code": finding.get("extra", {}).get("lines", ""),
                    "cwe": finding.get("extra", {}).get("metadata", {}).get("cwe", []),
                    "owasp": finding.get("extra", {}).get("metadata", {}).get("owasp", []),
                    "recommendation": finding.get("extra", {}).get("metadata", {}).get("recommendation", "Review and fix the vulnerability"),
                }
                vulnerabilities.append(vuln)

            logger.info(f"Semgrep found {len(vulnerabilities)} vulnerabilities")

            return {
                "tool": "Semgrep",
                "scan_type": "SAST",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": vulnerabilities,
                "raw_results": scan_results,  # Keep raw Semgrep results for parser
                "summary": {
                    "total": len(vulnerabilities),
                    "critical": len([v for v in vulnerabilities if v["severity"] == "CRITICAL"]),
                    "high": len([v for v in vulnerabilities if v["severity"] == "HIGH"]),
                    "medium": len([v for v in vulnerabilities if v["severity"] == "MEDIUM"]),
                    "low": len([v for v in vulnerabilities if v["severity"] == "LOW"]),
                }
            }

        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timeout (>10 minutes)")
            return {
                "tool": "Semgrep",
                "scan_type": "SAST",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                "error": "Scan timeout (>10 minutes)"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Semgrep output: {e}")
            return {
                "tool": "Semgrep",
                "scan_type": "SAST",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                "error": f"Failed to parse output: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Semgrep scan error: {str(e)}")
            return {
                "tool": "Semgrep",
                "scan_type": "SAST",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                "error": str(e)
            }


class SafetyScanner:
    """Wrapper for Safety SCA scanning."""

    @staticmethod
    def scan(repo_path: Path) -> Dict:
        """
        Run Safety scan for vulnerable dependencies.

        Args:
            repo_path: Path to repository to scan

        Returns:
            Dictionary with scan results in our format
        """
        try:
            logger.info(f"Running Safety scan on {repo_path}...")

            # Look for requirements files
            req_files = [
                repo_path / "requirements.txt",
                repo_path / "requirements" / "base.txt",
                repo_path / "requirements" / "prod.txt",
            ]

            req_file = None
            for rf in req_files:
                if rf.exists():
                    req_file = rf
                    break

            if not req_file:
                logger.warning("No requirements.txt found, skipping Safety scan")
                return {
                    "tool": "Safety",
                    "scan_type": "SCA",
                    "timestamp": datetime.now().isoformat(),
                    "vulnerabilities": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                    "note": "No requirements.txt found"
                }

            # Try to find safety executable
            import shutil
            safety_path = shutil.which("safety")
            if not safety_path:
                logger.warning("Safety not found in PATH, trying venv...")
                # Try venv location
                venv_safety = Path(__file__).parent.parent.parent / "venv" / "Scripts" / "safety.exe"
                if venv_safety.exists():
                    safety_path = str(venv_safety)
                else:
                    raise Exception("Safety executable not found. Please ensure it's installed.")

            logger.info(f"Using Safety at: {safety_path}")

            # Run safety check
            result = subprocess.run(
                [
                    safety_path,
                    "check",
                    "--file", str(req_file),
                    "--json",
                    "--output", "json"
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse JSON output
            try:
                scan_results = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError:
                # Safety might return non-JSON if no vulns found
                scan_results = []

            # Convert to our format
            vulnerabilities = []
            for finding in scan_results:
                vuln = {
                    "title": f"Vulnerable dependency: {finding.get('package', 'Unknown')}",
                    "severity": "HIGH",  # Safety doesn't provide severity, default to HIGH
                    "description": finding.get('advisory', 'No description'),
                    "package": finding.get('package', ''),
                    "installed_version": finding.get('installed_version', ''),
                    "affected_versions": finding.get('affected_versions', ''),
                    "vulnerable_spec": finding.get('vulnerable_spec', ''),
                    "cve": finding.get('cve', ''),
                    "recommendation": f"Upgrade to version {finding.get('fixed_version', 'latest')}" if finding.get('fixed_version') else "Update to a non-vulnerable version",
                }
                vulnerabilities.append(vuln)

            logger.info(f"Safety found {len(vulnerabilities)} vulnerable dependencies")

            return {
                "tool": "Safety",
                "scan_type": "SCA",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": vulnerabilities,
                "summary": {
                    "total": len(vulnerabilities),
                    "critical": 0,  # Safety doesn't provide severity ratings
                    "high": len(vulnerabilities),
                    "medium": 0,
                    "low": 0,
                }
            }

        except subprocess.TimeoutExpired:
            raise Exception("Safety scan timeout (>5 minutes)")
        except Exception as e:
            logger.error(f"Safety scan error: {e}")
            return {
                "tool": "Safety",
                "scan_type": "SCA",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                "error": str(e)
            }


def scan_github_repository(
    repo_url: str,
    branch: str = "main",
    scan_types: Dict[str, bool] = None,
    token: Optional[str] = None,
    progress_callback=None
) -> Dict[str, any]:
    """
    Main function to scan a GitHub repository.

    Args:
        repo_url: GitHub repository URL
        branch: Branch to scan (default: main)
        scan_types: Dict of scan types to run {'sast': True, 'sca': True, 'dast': False}
        token: Optional GitHub access token for private repositories
        progress_callback: Optional callback function to report progress

    Returns:
        Dictionary with all scan results
    """
    if scan_types is None:
        scan_types = {"sast": True, "sca": True, "dast": False}

    scanner = GitHubScanner()
    results = {
        "repository": repo_url,
        "branch": branch,
        "scan_timestamp": datetime.now().isoformat(),
        "scans": {}
    }

    try:
        logger.info(f"Starting GitHub scan for {repo_url} (branch: {branch})")

        # Clone repository with progress
        if progress_callback:
            progress_callback(f"Starting clone of {repo_url}...")

        repo_path = scanner.clone_repository(repo_url, branch, token, progress_callback)
        logger.info(f"Repository cloned successfully to {repo_path}")

        if progress_callback:
            progress_callback(f"Clone complete! Starting security scans...")

        # Run SAST scan (Semgrep)
        if scan_types.get("sast", False):
            try:
                logger.info("Starting SAST scan with Semgrep...")
                results["scans"]["sast"] = SemgrepScanner.scan(repo_path)
                logger.info("SAST scan completed successfully")
            except Exception as e:
                logger.error(f"SAST scan failed: {e}", exc_info=True)
                results["scans"]["sast"] = {
                    "error": str(e),
                    "tool": "Semgrep",
                    "scan_type": "SAST",
                    "vulnerabilities": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
                }

        # Run SCA scan (Safety)
        if scan_types.get("sca", False):
            try:
                logger.info("Starting SCA scan with Safety...")
                results["scans"]["sca"] = SafetyScanner.scan(repo_path)
                logger.info("SCA scan completed successfully")
            except Exception as e:
                logger.error(f"SCA scan failed: {e}", exc_info=True)
                results["scans"]["sca"] = {
                    "error": str(e),
                    "tool": "Safety",
                    "scan_type": "SCA",
                    "vulnerabilities": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
                }

        # DAST scanning with Smart DAST Scanner (4-tier approach)
        if scan_types.get("dast", False):
            try:
                logger.info("Starting Smart DAST scan...")
                from backend.scanners.smart_dast_scanner import SmartDASTScanner

                dast_scanner = SmartDASTScanner()
                # Get DAST URL from scan_types if provided
                dast_url = scan_types.get("dast_url")
                results["scans"]["dast"] = dast_scanner.scan(
                    repo_path=repo_path,
                    repo_url=repo_url,
                    branch=branch,
                    provided_url=dast_url
                )
                logger.info("Smart DAST scan completed")
            except Exception as e:
                logger.error(f"Smart DAST scan failed: {e}", exc_info=True)
                results["scans"]["dast"] = {
                    "error": str(e),
                    "tool": "Smart DAST Scanner",
                    "scan_type": "DAST",
                    "vulnerabilities": [],
                    "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
                }

        logger.info(f"GitHub scan completed. Total scans: {len(results['scans'])}")
        return results

    except Exception as e:
        logger.error(f"GitHub repository scan failed: {e}", exc_info=True)
        raise
    finally:
        # Always cleanup
        scanner.cleanup()
