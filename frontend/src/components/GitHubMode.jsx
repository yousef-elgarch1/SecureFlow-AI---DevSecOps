import React, { useState, useEffect } from 'react';
import { Github, GitBranch, Check, AlertCircle, Code2, Shield, Search, RefreshCw } from 'lucide-react';
import GitHubLogin from './GitHubLogin';

const GitHubMode = ({ config, onConfigChange, onSubmit, loading }) => {
  const [errors, setErrors] = useState({});
  const [branches, setBranches] = useState([]);
  const [loadingBranches, setLoadingBranches] = useState(false);
  const [branchError, setBranchError] = useState(null);
  const [githubToken, setGithubToken] = useState(null);
  const [githubUser, setGithubUser] = useState(null);

  const validateRepoUrl = (url) => {
    if (!url) return 'Repository URL is required';
    const githubPattern = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    if (!githubPattern.test(url.trim())) {
      return 'Please enter a valid GitHub repository URL (e.g., https://github.com/username/repo)';
    }
    return null;
  };

  const extractRepoInfo = (url) => {
    // Extract owner and repo from GitHub URL
    const match = url.match(/github\.com\/([\w-]+)\/([\w.-]+)/);
    if (match) {
      return { owner: match[1], repo: match[2].replace('.git', '') };
    }
    return null;
  };

  const fetchBranches = async (url) => {
    const repoInfo = extractRepoInfo(url);
    if (!repoInfo) {
      setBranchError('Invalid GitHub URL');
      return;
    }

    setLoadingBranches(true);
    setBranchError(null);

    try {
      const response = await fetch(
        `https://api.github.com/repos/${repoInfo.owner}/${repoInfo.repo}/branches`,
        {
          headers: {
            'Accept': 'application/vnd.github.v3+json'
          }
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Repository not found. Make sure it is public.');
        } else if (response.status === 403) {
          throw new Error('GitHub API rate limit exceeded. Please try again later.');
        } else {
          throw new Error(`Failed to fetch branches: ${response.statusText}`);
        }
      }

      const branchesData = await response.json();
      const branchNames = branchesData.map(b => b.name);
      setBranches(branchNames);

      // Auto-select main or master if available
      if (branchNames.includes('main') && !config.branch) {
        onConfigChange({ ...config, branch: 'main' });
      } else if (branchNames.includes('master') && !config.branch) {
        onConfigChange({ ...config, branch: 'master' });
      } else if (branchNames.length > 0 && !config.branch) {
        onConfigChange({ ...config, branch: branchNames[0] });
      }
    } catch (error) {
      setBranchError(error.message);
      setBranches([]);
    } finally {
      setLoadingBranches(false);
    }
  };

  // Auto-fetch branches when URL changes and is valid
  useEffect(() => {
    if (config.repoUrl && !validateRepoUrl(config.repoUrl)) {
      fetchBranches(config.repoUrl);
    } else {
      setBranches([]);
      setBranchError(null);
    }
  }, [config.repoUrl]);

  const handleUrlChange = (e) => {
    const url = e.target.value;
    onConfigChange({ ...config, repoUrl: url });
    const error = validateRepoUrl(url);
    setErrors({ ...errors, repoUrl: error });
  };

  const handleBranchChange = (e) => {
    onConfigChange({ ...config, branch: e.target.value });
  };

  const handleDastUrlChange = (e) => {
    onConfigChange({ ...config, dastUrl: e.target.value });
  };

  const handleAuthSuccess = (token, user) => {
    setGithubToken(token);
    setGithubUser(user);
    // Store token in config for passing to scan function
    onConfigChange({ ...config, token });
  };

  const handleAuthError = (error) => {
    console.error('GitHub auth error:', error);
    setErrors({ ...errors, auth: error.message });
  };

  const handleScanTypeToggle = (type) => {
    onConfigChange({
      ...config,
      scanTypes: {
        ...config.scanTypes,
        [type]: !config.scanTypes[type]
      }
    });
  };

  const handleSubmit = () => {
    const error = validateRepoUrl(config.repoUrl);
    if (error) {
      setErrors({ repoUrl: error });
      return;
    }

    const hasAnyScanType = Object.values(config.scanTypes).some(v => v);
    if (!hasAnyScanType) {
      alert('Please select at least one scan type');
      return;
    }

    onSubmit();
  };

  const scanTypeOptions = [
    {
      key: 'sast',
      title: 'SAST - Static Analysis',
      description: 'Scan source code for security vulnerabilities',
      tool: 'Semgrep',
      icon: Code2,
      color: 'cyan',
      enabled: config.scanTypes.sast
    },
    {
      key: 'sca',
      title: 'SCA - Dependency Analysis',
      description: 'Check dependencies for known vulnerabilities',
      tool: 'Safety / pip-audit',
      icon: Shield,
      color: 'emerald',
      enabled: config.scanTypes.sca
    },
    {
      key: 'dast',
      title: 'DAST - Dynamic Testing',
      description: 'Runtime security testing (requires running app)',
      tool: 'OWASP ZAP',
      icon: Search,
      color: 'purple',
      enabled: config.scanTypes.dast
    }
  ];

  return (
    <div className="space-y-6">
      {/* GitHub OAuth Login */}
      <GitHubLogin onAuthSuccess={handleAuthSuccess} onAuthError={handleAuthError} />

      {/* Main Card */}
      <div className="bg-gradient-to-br from-slate-800/50 via-gray-800/50 to-slate-800/50 rounded-3xl shadow-2xl border border-purple-500/20 p-8 backdrop-blur-sm">
        {/* Header */}
        <div className="flex items-center space-x-4 mb-8">
          <div className="bg-gradient-to-br from-purple-500 via-violet-500 to-indigo-600 p-4 rounded-2xl shadow-lg shadow-purple-500/30">
            <Github className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-violet-400 to-indigo-400 bg-clip-text text-transparent">
              GitHub Repository Scanner
            </h2>
            <p className="text-gray-400 mt-1 text-sm">
              Automatically scan and generate security policies from your GitHub repository
            </p>
          </div>
        </div>

        {/* Repository URL Input */}
        <div className="mb-6">
          <label className="block text-sm font-bold text-gray-200 mb-3">
            Repository URL <span className="text-rose-400">*</span>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Github className="w-5 h-5 text-gray-500" />
            </div>
            <input
              type="text"
              value={config.repoUrl}
              onChange={handleUrlChange}
              placeholder="https://github.com/username/repository"
              className={`
                w-full pl-12 pr-4 py-4 bg-slate-900/50 border-2 rounded-xl
                text-gray-200 placeholder-gray-500 font-mono text-sm
                focus:outline-none focus:ring-2 transition-all duration-200
                ${errors.repoUrl
                  ? 'border-rose-500/50 focus:border-rose-400 focus:ring-rose-400/30'
                  : 'border-purple-500/30 focus:border-purple-400 focus:ring-purple-400/30'
                }
              `}
            />
            {config.repoUrl && !errors.repoUrl && (
              <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
                <Check className="w-5 h-5 text-emerald-400" />
              </div>
            )}
          </div>
          {errors.repoUrl && (
            <div className="flex items-center space-x-2 mt-2 text-rose-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>{errors.repoUrl}</span>
            </div>
          )}
          <p className="text-gray-500 text-xs mt-2">
            Example: https://github.com/facebook/react
          </p>
        </div>

        {/* Branch Selection */}
        <div className="mb-8">
          <label className="block text-sm font-bold text-gray-200 mb-3 flex items-center justify-between">
            <span>Branch</span>
            {loadingBranches && (
              <span className="flex items-center space-x-2 text-xs text-purple-400">
                <RefreshCw className="w-3 h-3 animate-spin" />
                <span>Loading branches...</span>
              </span>
            )}
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
              <GitBranch className="w-5 h-5 text-gray-500" />
            </div>
            {branches.length > 0 ? (
              <select
                value={config.branch}
                onChange={handleBranchChange}
                disabled={loadingBranches}
                className="w-full pl-12 pr-4 py-4 bg-slate-900/50 border-2 border-purple-500/30 rounded-xl text-gray-200 font-mono text-sm focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/30 transition-all duration-200 appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {branches.map(branch => (
                  <option key={branch} value={branch} className="bg-slate-900">
                    {branch}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={config.branch}
                onChange={handleBranchChange}
                placeholder="main"
                disabled={loadingBranches}
                className="w-full pl-12 pr-4 py-4 bg-slate-900/50 border-2 border-purple-500/30 rounded-xl text-gray-200 placeholder-gray-500 font-mono text-sm focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            )}
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
              {branches.length > 0 && (
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              )}
            </div>
          </div>
          {branchError && (
            <div className="flex items-center space-x-2 mt-2 text-amber-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>{branchError}</span>
            </div>
          )}
          {branches.length > 0 ? (
            <p className="text-gray-500 text-xs mt-2">
              Found {branches.length} branch{branches.length !== 1 ? 'es' : ''} in repository
            </p>
          ) : (
            <p className="text-gray-500 text-xs mt-2">
              Enter repository URL above to auto-detect branches
            </p>
          )}
        </div>

        {/* Scan Type Selection */}
        <div className="mb-8">
          <label className="block text-sm font-bold text-gray-200 mb-4">
            Security Scans to Perform <span className="text-rose-400">*</span>
          </label>
          <div className="grid grid-cols-1 gap-4">
            {scanTypeOptions.map((option) => (
              <button
                key={option.key}
                onClick={() => handleScanTypeToggle(option.key)}
                className={`
                  relative p-5 rounded-2xl border-2 transition-all duration-300 text-left
                  ${option.enabled
                    ? `bg-${option.color}-500/10 border-${option.color}-400/50 shadow-lg shadow-${option.color}-500/20`
                    : 'bg-slate-900/30 border-slate-700/50 hover:border-slate-600'
                  }
                `}
              >
                <div className="flex items-start space-x-4">
                  {/* Icon */}
                  <div className={`
                    p-3 rounded-xl ${option.enabled ? `bg-${option.color}-500/20` : 'bg-slate-800/50'}
                  `}>
                    <option.icon className={`w-6 h-6 ${option.enabled ? `text-${option.color}-400` : 'text-gray-500'}`} />
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                      <h3 className={`text-base font-bold ${option.enabled ? `text-${option.color}-300` : 'text-gray-400'}`}>
                        {option.title}
                      </h3>
                      <span className={`
                        px-2 py-0.5 rounded-md text-xs font-semibold
                        ${option.enabled ? `bg-${option.color}-500/20 text-${option.color}-300` : 'bg-slate-700/50 text-gray-500'}
                      `}>
                        {option.tool}
                      </span>
                    </div>
                    <p className={`text-sm ${option.enabled ? 'text-gray-300' : 'text-gray-500'}`}>
                      {option.description}
                    </p>
                  </div>

                  {/* Checkbox */}
                  <div className={`
                    w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all
                    ${option.enabled
                      ? `bg-${option.color}-500 border-${option.color}-400 shadow-lg shadow-${option.color}-500/30`
                      : 'border-slate-600 bg-slate-800/50'
                    }
                  `}>
                    {option.enabled && <Check className="w-4 h-4 text-white" />}
                  </div>
                </div>
              </button>
            ))}
          </div>
          <p className="text-gray-500 text-xs mt-3">
            Select at least one scan type. SAST and SCA are recommended for most projects.
          </p>
        </div>

        {/* DAST URL Input - Show only when DAST is enabled */}
        {config.scanTypes.dast && (
          <div className="mb-8">
            <label className="block text-sm font-bold text-gray-200 mb-3">
              DAST URL (Optional - Tier 1)
            </label>
            <input
              type="url"
              value={config.dastUrl || ''}
              onChange={handleDastUrlChange}
              placeholder="https://your-live-app.com (leave empty for auto-detection)"
              className="
                w-full px-4 py-4 bg-slate-900/50 border-2 border-purple-500/30 rounded-xl
                text-gray-200 placeholder-gray-500 font-mono text-sm
                focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/30
                transition-all duration-200
              "
            />
            <div className="mt-3 bg-purple-500/10 border border-purple-400/30 rounded-xl p-4">
              <p className="text-xs text-purple-300 font-semibold mb-2">4-Tier DAST Approach:</p>
              <ul className="text-xs text-gray-400 space-y-1">
                <li>• <span className="text-purple-400">Tier 1:</span> Scan your live URL (if provided above)</li>
                <li>• <span className="text-purple-400">Tier 2:</span> Auto-detect deployment (GitHub Pages, Vercel, Netlify)</li>
                <li>• <span className="text-purple-400">Tier 3:</span> Docker-based local deployment</li>
                <li>• <span className="text-purple-400">Tier 4:</span> Helpful fallback with instructions</li>
              </ul>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-700/50">
          <div className="text-sm text-gray-400">
            <p className="font-semibold text-gray-300 mb-1">What happens next?</p>
            <ul className="space-y-1 text-xs">
              <li>• Repository will be cloned securely</li>
              <li>• Selected security scans will run automatically</li>
              <li>• AI will generate policies from findings</li>
              <li>• Compliance analysis (NIST CSF + ISO 27001)</li>
            </ul>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !!errors.repoUrl || !config.repoUrl}
            className="
              px-8 py-4 bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-600
              text-white font-bold text-base rounded-xl
              shadow-2xl shadow-purple-500/30
              hover:shadow-purple-500/50 hover:scale-105
              disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
              transition-all duration-300
              flex items-center space-x-3
            "
          >
            <Github className="w-5 h-5" />
            <span>{loading ? 'Scanning...' : 'Scan Repository'}</span>
          </button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/30 border border-cyan-500/20 rounded-2xl p-5 backdrop-blur-sm">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
            <h4 className="text-sm font-bold text-cyan-300">Public Repositories</h4>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            Currently supports public GitHub repositories. OAuth integration for private repos coming soon.
          </p>
        </div>

        <div className="bg-slate-800/30 border border-emerald-500/20 rounded-2xl p-5 backdrop-blur-sm">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
            <h4 className="text-sm font-bold text-emerald-300">Automated Scanning</h4>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            Industry-standard tools (Semgrep, Safety) automatically scan your code for vulnerabilities.
          </p>
        </div>

        <div className="bg-slate-800/30 border border-purple-500/20 rounded-2xl p-5 backdrop-blur-sm">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></div>
            <h4 className="text-sm font-bold text-purple-300">AI-Powered Policies</h4>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            LLaMA 3.3 70B generates comprehensive security policies with compliance mapping.
          </p>
        </div>
      </div>
    </div>
  );
};

export default GitHubMode;
