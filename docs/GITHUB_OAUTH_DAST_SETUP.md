# GitHub OAuth & 4-Tier DAST Setup Guide

This guide explains how to set up GitHub OAuth authentication and the 4-tier DAST scanning system.

---

## 🔐 GitHub OAuth Setup

### Why GitHub OAuth?
GitHub OAuth allows the application to access **private repositories** for security scanning. Without OAuth, only public repositories can be scanned.

### Step 1: Register a GitHub OAuth App

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/developers
   - Click "OAuth Apps" → "New OAuth App"

2. **Fill in Application Details**
   ```
   Application name: AI Security Policy Generator
   Homepage URL: http://localhost:5173
   Authorization callback URL: http://localhost:5173/auth/github/callback
   ```

3. **Get Your Credentials**
   - After registration, copy your **Client ID**
   - Click "Generate a new client secret" and copy the **Client Secret**

### Step 2: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   ```env
   GITHUB_CLIENT_ID=your_client_id_here
   GITHUB_CLIENT_SECRET=your_client_secret_here
   GITHUB_REDIRECT_URI=http://localhost:5173/auth/github/callback
   ```

3. **Save the file** (make sure not to commit `.env` to git!)

### Step 3: Restart Backend

```bash
# If using batch file
start_backend.bat

# If using command line
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

### Step 4: Test OAuth Flow

1. Start the frontend: `cd frontend && npm run dev`
2. Go to http://localhost:5173
3. Click "GitHub Scan" tab
4. Click "Connect GitHub" button
5. Authorize the app in the popup
6. You should see your GitHub profile appear

---

## 🎯 4-Tier DAST Scanning System

The Smart DAST Scanner uses a **4-tier fallback approach** to scan applications dynamically:

### Tier 1: User-Provided URL ✅ **Fastest & Most Reliable**

**When to use:** You have a live deployment URL

**How it works:**
1. Enable DAST scanning in GitHub Mode
2. Enter your live URL in the "DAST URL" field
3. Scanner uses Nuclei to scan the live application

**Example:**
```
DAST URL: https://my-app.herokuapp.com
```

**Advantages:**
- ✅ Immediate scanning
- ✅ Scans production environment
- ✅ Most accurate results

---

### Tier 2: Auto-Deployment Detection 🔍 **Automatic**

**When to use:** Your app is deployed on common platforms

**How it works:**
The scanner automatically detects and scans deployments on:
- **GitHub Pages**: `username.github.io/repo`
- **Vercel**: `repo.vercel.app`
- **Netlify**: `repo.netlify.app`
- **Render**: `repo.onrender.com`
- **Heroku**: `repo.herokuapp.com`

**Example:**
```
Repository: https://github.com/username/my-react-app
Auto-detected: https://my-react-app.vercel.app
```

**Advantages:**
- ✅ Zero configuration needed
- ✅ Works automatically
- ✅ Supports multiple platforms

---

### Tier 3: Docker-Based Local Deployment 🐳 **Advanced**

**When to use:** Application not deployed, but has Docker support

**Requirements:**
- Docker Desktop installed and running
- Dockerfile in repository (or auto-generated)

**How it works:**
1. Scanner detects project type (Flask, Django, Node.js, React, etc.)
2. Generates appropriate Dockerfile if not present
3. Builds Docker image
4. Runs container locally
5. Scans `localhost:PORT`
6. Cleans up container and image

**Supported Frameworks:**
- Python: Flask, Django
- JavaScript: Node.js, Express, React, Next.js, Vue.js
- PHP: Laravel, vanilla PHP
- Static HTML sites

**Example:**
```
Detected: Flask application
Generated: Dockerfile for Python/Flask
Built: dast-scan-20241106123456
Scanning: http://localhost:5000
```

**Advantages:**
- ✅ No manual deployment needed
- ✅ Scans exactly as-deployed
- ✅ Supports many frameworks

**Note:** This may take 5-10 minutes for build + scan

---

### Tier 4: Graceful Fallback 📋 **Informative**

**When to use:** None of the above tiers work

**How it works:**
Returns helpful instructions and guidance instead of failing

**What you get:**
- Clear explanation of why DAST isn't possible
- Instructions for each tier
- List of supported platforms
- List of supported frameworks

**Example Response:**
```json
{
  "note": "DAST scanning not possible",
  "instructions": {
    "tier1": "Provide a live URL in the 'DAST URL' field",
    "tier2": "Deploy to GitHub Pages, Vercel, or Netlify",
    "tier3": "Add a Dockerfile to enable Docker scanning",
    "tier4": "DAST requires a running application"
  }
}
```

---

## 🛠️ Nuclei Installation (Required for DAST)

### Windows

**Option 1: Using Chocolatey (Recommended)**
```bash
choco install nuclei
```

**Option 2: Using Go**
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

**Option 3: Manual Download**
1. Download from: https://github.com/projectdiscovery/nuclei/releases
2. Extract to `C:\Program Files\nuclei\`
3. Add to PATH environment variable

### Linux/Mac

**Using Go:**
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

**Using Package Manager:**
```bash
# Ubuntu/Debian
sudo apt install nuclei

# macOS
brew install nuclei
```

### Verify Installation

```bash
nuclei -version
```

You should see output like:
```
Nuclei v3.x.x
```

---

## 🐳 Docker Installation (Optional - For Tier 3)

### Windows

Download and install **Docker Desktop for Windows**:
https://www.docker.com/products/docker-desktop/

### Linux

```bash
# Ubuntu/Debian
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

### Mac

Download and install **Docker Desktop for Mac**:
https://www.docker.com/products/docker-desktop/

### Verify Installation

```bash
docker --version
docker ps
```

---

## 📊 Usage Examples

### Example 1: Scan Public Repo with DAST URL

```
Repository: https://github.com/juice-shop/juice-shop
Branch: master
Scan Types: ✅ SAST, ✅ SCA, ✅ DAST
DAST URL: https://juice-shop.herokuapp.com
```

**Result:** Uses Tier 1 (user-provided URL)

---

### Example 2: Scan with Auto-Detection

```
Repository: https://github.com/username/my-nextjs-app
Branch: main
Scan Types: ✅ SAST, ✅ SCA, ✅ DAST
DAST URL: (leave empty)
```

**Result:** Uses Tier 2 (auto-detects Vercel deployment)

---

### Example 3: Scan with Docker

```
Repository: https://github.com/username/flask-api
Branch: main
Scan Types: ✅ SAST, ✅ SCA, ✅ DAST
DAST URL: (leave empty)
Docker: Running
```

**Result:** Uses Tier 3 (builds and scans locally)

---

### Example 4: Private Repo Scan

```
1. Click "Connect GitHub" button
2. Authorize the app
3. Enter private repository URL
4. Select scan types
5. Submit
```

**Result:** Uses OAuth token to clone private repo

---

## 🔧 Troubleshooting

### GitHub OAuth Not Working

**Problem:** "GitHub OAuth not configured" error

**Solution:**
1. Check `.env` file exists with correct values
2. Restart backend server
3. Check backend logs for OAuth configuration
4. Verify callback URL matches exactly: `http://localhost:5173/auth/github/callback`

---

### Nuclei Not Found

**Problem:** "Nuclei not installed" error

**Solution:**
1. Install Nuclei (see installation section above)
2. Verify with: `nuclei -version`
3. Add Nuclei to PATH if needed
4. Restart backend server

---

### Docker Not Available

**Problem:** DAST skips to Tier 4

**Solution:**
1. Install Docker Desktop
2. Start Docker Desktop
3. Verify with: `docker ps`
4. Make sure Docker daemon is running

---

### DAST URL Not Accessible

**Problem:** "Provided URL is not accessible"

**Solution:**
1. Verify URL is correct and publicly accessible
2. Check if application is running
3. Try accessing URL in browser
4. Check for HTTPS/HTTP mismatch

---

## 🎓 Best Practices

### For Maximum DAST Coverage:

1. **Always provide DAST URL if available** (Tier 1 is fastest)
2. **Deploy to Vercel/Netlify** for auto-detection
3. **Include Dockerfile** for Docker-based scanning
4. **Test locally first** before scanning production

### For Private Repositories:

1. **Use GitHub OAuth** - required for private repos
2. **Request minimal scopes** - app only needs `repo` and `read:user`
3. **Revoke access** when done (GitHub Settings → Applications)

### For Best Results:

1. **Enable all 3 scan types** (SAST + SCA + DAST)
2. **Use main/master branch** for most accurate results
3. **Ensure app is running** before DAST scan
4. **Review fallback instructions** if DAST fails

---

## 📚 Additional Resources

- **Nuclei Documentation**: https://docs.nuclei.sh/
- **GitHub OAuth Docs**: https://docs.github.com/en/developers/apps/building-oauth-apps
- **Docker Documentation**: https://docs.docker.com/

---

## ✅ Quick Checklist

Before running a scan, ensure:

- [ ] Backend server is running (`http://localhost:8000`)
- [ ] Frontend is running (`http://localhost:5173`)
- [ ] `.env` file is configured with GitHub OAuth credentials
- [ ] Nuclei is installed (run `nuclei -version`)
- [ ] Docker is running (optional, for Tier 3)
- [ ] Repository URL is valid
- [ ] At least one scan type is selected

---

**Need help?** Check the backend logs for detailed error messages:
```bash
# Backend logs show:
# - OAuth configuration status
# - Nuclei availability
# - Docker availability
# - DAST tier decisions
# - Scan progress
```
