"""
Smart DAST Scanner - 4-Tier Approach
Tier 1: URL-based scanning (user provides URL)
Tier 2: Auto-detect deployment (GitHub Pages, Vercel, Netlify, etc.)
Tier 3: Docker-based local deployment
Tier 4: Graceful fallback with helpful instructions
"""

import os
import subprocess
import logging
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import httpx

try:
    from backend.scanners.zap_scanner import scan_url_with_zap as scan_url
except ImportError:
    from backend.scanners.nuclei_scanner import scan_url_with_nuclei as scan_url

logger = logging.getLogger(__name__)


class SmartDASTScanner:
    """Intelligent DAST scanner with multi-tier fallback approach."""

    def __init__(self):
        self.temp_dir = None

    def scan(self, repo_path: Path, repo_url: str, branch: str, provided_url: Optional[str] = None) -> Dict:
        """
        Scan using 4-tier approach.

        Args:
            repo_path: Path to cloned repository
            repo_url: GitHub repository URL
            branch: Branch name
            provided_url: Optional user-provided live URL

        Returns:
            DAST scan results
        """
        logger.info("Starting Smart DAST scan...")

        # Tier 1: User-provided URL
        if provided_url:
            logger.info(f"[Tier 1] Using user-provided URL: {provided_url}")
            if self._is_url_alive(provided_url):
                return scan_url(provided_url)
            else:
                logger.warning(f"Provided URL {provided_url} is not accessible")

        # Tier 2: Auto-detect deployment
        logger.info("[Tier 2] Attempting to auto-detect deployment...")
        detected_url = self._detect_deployment(repo_url, branch)
        if detected_url:
            logger.info(f"[Tier 2] Detected deployment at: {detected_url}")
            if self._is_url_alive(detected_url):
                return scan_url(detected_url)

        # Tier 3: Docker-based local deployment
        logger.info("[Tier 3] Attempting Docker-based local deployment...")
        try:
            docker_result = self._docker_deploy_and_scan(repo_path)
            if docker_result:
                return docker_result
        except Exception as e:
            logger.warning(f"Docker deployment failed: {e}")

        # Tier 4: Graceful fallback
        logger.info("[Tier 4] DAST not possible - providing fallback guidance")
        return self._graceful_fallback(repo_url)

    def _is_url_alive(self, url: str) -> bool:
        """Check if a URL is accessible."""
        try:
            import httpx
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            return response.status_code < 400
        except Exception as e:
            logger.debug(f"URL {url} not accessible: {e}")
            return False

    def _detect_deployment(self, repo_url: str, branch: str) -> Optional[str]:
        """
        Auto-detect common deployment platforms.

        Returns:
            Detected URL or None
        """
        # Extract owner and repo from GitHub URL
        match = re.search(r'github\.com/([^/]+)/([^/]+?)(?:\.git)?$', repo_url)
        if not match:
            return None

        owner, repo = match.groups()
        repo = repo.replace('.git', '')

        # Check GitHub Pages
        github_pages_urls = [
            f"https://{owner}.github.io/{repo}",  # Project page
            f"https://{owner}.github.io",  # User/org page
        ]

        for url in github_pages_urls:
            if self._is_url_alive(url):
                logger.info(f"Detected GitHub Pages: {url}")
                return url

        # Check Vercel
        vercel_url = f"https://{repo}.vercel.app"
        if self._is_url_alive(vercel_url):
            logger.info(f"Detected Vercel deployment: {vercel_url}")
            return vercel_url

        # Check Netlify
        netlify_url = f"https://{repo}.netlify.app"
        if self._is_url_alive(netlify_url):
            logger.info(f"Detected Netlify deployment: {netlify_url}")
            return netlify_url

        # Check Render
        render_url = f"https://{repo}.onrender.com"
        if self._is_url_alive(render_url):
            logger.info(f"Detected Render deployment: {render_url}")
            return render_url

        # Check Heroku
        heroku_url = f"https://{repo}.herokuapp.com"
        if self._is_url_alive(heroku_url):
            logger.info(f"Detected Heroku deployment: {heroku_url}")
            return heroku_url

        logger.info("No deployment platform detected")
        return None

    def _detect_project_type(self, repo_path: Path) -> Tuple[str, Dict]:
        """
        Detect project type and configuration.

        Returns:
            (project_type, config) tuple
        """
        # Check for existing Dockerfile
        if (repo_path / "Dockerfile").exists():
            return ("docker", {"dockerfile": "Dockerfile"})

        # Check for Python (Flask/Django)
        if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists():
            if (repo_path / "manage.py").exists():
                return ("django", {"port": 8000})
            elif any((repo_path / "app.py").exists(), (repo_path / "wsgi.py").exists()):
                return ("flask", {"port": 5000})
            return ("python", {"port": 8000})

        # Check for Node.js
        if (repo_path / "package.json").exists():
            try:
                with open(repo_path / "package.json") as f:
                    pkg = json.load(f)
                    scripts = pkg.get("scripts", {})

                    if "next" in scripts.get("dev", ""):
                        return ("nextjs", {"port": 3000})
                    elif "react-scripts" in scripts.get("start", ""):
                        return ("react", {"port": 3000})
                    elif "vue-cli-service" in scripts.get("serve", ""):
                        return ("vue", {"port": 8080})
                    else:
                        return ("nodejs", {"port": 3000})
            except Exception as e:
                logger.warning(f"Failed to parse package.json: {e}")

        # Check for static site
        if (repo_path / "index.html").exists():
            return ("static", {"port": 8080})

        # Check for PHP
        if any((repo_path / "index.php").exists(), (repo_path / "composer.json").exists()):
            return ("php", {"port": 80})

        return ("unknown", {})

    def _docker_deploy_and_scan(self, repo_path: Path) -> Optional[Dict]:
        """
        Deploy using Docker and scan.

        Returns:
            Scan results or None if deployment failed
        """
        # Check if Docker is available
        if not shutil.which("docker"):
            logger.warning("Docker not available")
            return None

        try:
            # Detect project type
            project_type, config = self._detect_project_type(repo_path)
            logger.info(f"Detected project type: {project_type}")

            if project_type == "unknown":
                logger.warning("Could not detect project type for Docker deployment")
                return None

            # Generate Dockerfile if not exists
            dockerfile_path = repo_path / "Dockerfile"
            if not dockerfile_path.exists():
                dockerfile_content = self._generate_dockerfile(project_type, repo_path)
                if not dockerfile_content:
                    logger.warning(f"No Dockerfile template for {project_type}")
                    return None

                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)
                logger.info(f"Generated Dockerfile for {project_type}")

            # Build Docker image
            image_name = f"dast-scan-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            logger.info(f"Building Docker image: {image_name}")

            build_result = subprocess.run(
                ["docker", "build", "-t", image_name, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=300
            )

            if build_result.returncode != 0:
                logger.error(f"Docker build failed: {build_result.stderr}")
                return None

            # Run container
            port = config.get("port", 8080)
            logger.info(f"Starting container on port {port}")

            run_result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "-p", f"{port}:{port}",
                    "--name", image_name,
                    image_name
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if run_result.returncode != 0:
                logger.error(f"Docker run failed: {run_result.stderr}")
                return None

            container_id = run_result.stdout.strip()
            logger.info(f"Container started: {container_id}")

            # Wait for application to start
            import time
            time.sleep(10)

            # Scan localhost
            local_scan_url = f"http://localhost:{port}"
            logger.info(f"Scanning {local_scan_url}")

            scan_result = scan_url(local_scan_url)

            # Cleanup
            subprocess.run(["docker", "stop", container_id], timeout=30)
            subprocess.run(["docker", "rm", container_id], timeout=30)
            subprocess.run(["docker", "rmi", image_name], timeout=30)

            return scan_result

        except Exception as e:
            logger.error(f"Docker deployment error: {e}", exc_info=True)
            return None

    def _generate_dockerfile(self, project_type: str, repo_path: Path) -> Optional[str]:
        """Generate Dockerfile based on project type."""

        if project_type == "flask":
            return """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
"""

        elif project_type == "django":
            return """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py migrate --no-input
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"""

        elif project_type in ("nodejs", "react", "nextjs"):
            return """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build || true
EXPOSE 3000
CMD ["npm", "start"]
"""

        elif project_type == "static":
            return """FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
"""

        elif project_type == "php":
            return """FROM php:8.1-apache
COPY . /var/www/html/
EXPOSE 80
CMD ["apache2-foreground"]
"""

        return None

    def _graceful_fallback(self, repo_url: str) -> Dict:
        """Provide helpful fallback when DAST is not possible."""
        return {
            "tool": "Smart DAST Scanner",
            "scan_type": "DAST",
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
            "note": "DAST scanning not possible",
            "instructions": {
                "tier1": "Provide a live URL in the 'DAST URL' field for immediate scanning",
                "tier2": "Deploy to GitHub Pages, Vercel, or Netlify for automatic detection",
                "tier3": "Add a Dockerfile to enable local Docker-based scanning",
                "tier4": "DAST requires a running application - consider manual deployment"
            },
            "supported_deployments": [
                "GitHub Pages (username.github.io/repo)",
                "Vercel (repo.vercel.app)",
                "Netlify (repo.netlify.app)",
                "Render (repo.onrender.com)",
                "Heroku (repo.herokuapp.com)",
            ],
            "supported_frameworks": [
                "Flask (Python)",
                "Django (Python)",
                "Node.js / Express",
                "React / Next.js",
                "Vue.js",
                "Static HTML",
                "PHP / Laravel",
            ]
        }

    def cleanup(self):
        """Cleanup temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def __del__(self):
        """Ensure cleanup on destruction."""
        self.cleanup()
