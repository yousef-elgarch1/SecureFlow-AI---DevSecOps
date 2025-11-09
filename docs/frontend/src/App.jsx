import React, { useState, useEffect } from 'react';
import { Upload, Activity, CheckCircle, Github, Code2, Shield } from 'lucide-react';
import UploadMode from './components/UploadMode';
import GitHubMode from './components/GitHubMode';
import PolicyTracking from './components/PolicyTracking';
import WorkflowView from './components/WorkflowView';
import ResultsView from './components/ResultsView';
import apiClient from './utils/api';

function App() {
  const [inputMode, setInputMode] = useState('upload'); // 'upload', 'github', or 'tracking'
  const [files, setFiles] = useState({ sast: null, sca: null, dast: null });
  const [githubConfig, setGithubConfig] = useState({
    repoUrl: '',
    branch: '', // Empty default - will be auto-detected by GitHubMode
    scanTypes: { sast: true, sca: true, dast: false },
    dastUrl: ''
  });
  const [userProfile, setUserProfile] = useState({
    expertise_level: 'intermediate',
    user_role: 'senior_developer',
    user_name: ''
  });
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const health = await apiClient.checkHealth();
      if (health.status === 'healthy') {
        setBackendStatus('connected');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('error');
      console.error('Backend health check failed:', error);
    }
  };

  const handleFilesChange = (newFiles) => {
    setFiles(newFiles);
  };

  const handleGeneratePolicies = async () => {
    // Validate based on mode
    if (inputMode === 'upload') {
      const hasFiles = files.sast || files.sca || files.dast;
      if (!hasFiles) {
        alert('Please upload at least one security report');
        return;
      }
    } else if (inputMode === 'github') {
      if (!githubConfig.repoUrl) {
        alert('Please enter a GitHub repository URL');
        return;
      }
      const hasAnyScanType = Object.values(githubConfig.scanTypes).some(v => v);
      if (!hasAnyScanType) {
        alert('Please select at least one scan type');
        return;
      }
    }

    setProcessing(true);
    setProgress([]);
    setResults(null);
    setError(null);

    // Flag to track if WebSocket provided results
    let websocketComplete = false;

    try {
      // Set up WebSocket progress handler
      const handleProgress = (data) => {
        console.log('Progress update:', data);
        // Append all updates for detailed workflow view
        setProgress(prev => [...prev, data]);

        // Check if processing is complete
        if (data.phase === 'complete') {
          console.log('WebSocket complete data:', data.data);
          console.log('WebSocket results array:', data.data?.results);
          console.log('WebSocket compliance_analysis:', data.data?.compliance_analysis);
          websocketComplete = true;  // Set flag immediately
          setResults(data.data);
          setProcessing(false);
          apiClient.disconnectWebSocket();
        }
      };

      let result;

      // Call appropriate API based on mode
      if (inputMode === 'upload') {
        result = await apiClient.generatePolicies(files, 5, handleProgress, userProfile);
      } else if (inputMode === 'github') {
        result = await apiClient.scanGitHubRepo(
          githubConfig.repoUrl,
          githubConfig.branch,
          githubConfig.scanTypes,
          5,
          githubConfig.token,  // Pass GitHub OAuth token
          githubConfig.dastUrl,  // Pass DAST URL for Tier 1 scanning
          handleProgress
        );
      }

      // Set final results ONLY if we didn't already get them from WebSocket
      // The WebSocket 'complete' message contains the full data with compliance_analysis
      // The HTTP response might be empty or incomplete
      if (result && !websocketComplete) {
        console.log('Using HTTP response as fallback:', result);
        setResults(result);
        setProcessing(false);
        apiClient.disconnectWebSocket();
      } else {
        console.log('Already received results from WebSocket, ignoring HTTP response');
      }
    } catch (error) {
      console.error('Policy generation error:', error);
      setError(error.message || 'Failed to generate policies');
      setProcessing(false);
      apiClient.disconnectWebSocket();
    }
  };

  const handleReset = () => {
    setFiles({ sast: null, sca: null, dast: null });
    setProcessing(false);
    setProgress([]);
    setResults(null);
    setError(null);
    apiClient.disconnectWebSocket();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900">
      {/* Header */}
      <header className="bg-gradient-to-r from-slate-900 via-gray-900 to-slate-900 shadow-2xl border-b border-cyan-500/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img src="/logo.png" alt="SecurAI Logo" className="w-16 h-16" />
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent tracking-tight">
                  SecurAI - AI Security Policy
                </h1>
                <p className="text-sm text-cyan-300/70 font-medium mt-1 tracking-wide">
                   Keep It Halal · LLaMA 3.3 70B · RAG · NIST CSF · ISO 27001
                </p>
              </div>
            </div>

            {/* Backend Status Indicator */}
            <div className="flex items-center space-x-3 bg-slate-800/50 px-4 py-2 rounded-xl border border-cyan-500/20">
              <div className={`
                w-3 h-3 rounded-full
                ${backendStatus === 'connected' ? 'bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50' : ''}
                ${backendStatus === 'checking' ? 'bg-amber-400 animate-pulse shadow-lg shadow-amber-400/50' : ''}
                ${backendStatus === 'error' ? 'bg-rose-500 shadow-lg shadow-rose-500/50' : ''}
              `} />
              <span className="text-sm text-gray-300 font-medium">
                {backendStatus === 'connected' && 'Backend Connected'}
                {backendStatus === 'checking' && 'Checking Backend...'}
                {backendStatus === 'error' && 'Backend Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Backend Error Warning */}
        {backendStatus === 'error' && (
          <div className="bg-gradient-to-r from-rose-900/30 via-red-900/30 to-rose-900/30 border-2 border-rose-500/50 rounded-2xl p-5 mb-6 backdrop-blur-sm shadow-2xl shadow-rose-500/20">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <svg className="w-7 h-7 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-rose-300">Backend Connection Error</h3>
                <p className="text-sm text-gray-300 mt-1 leading-relaxed">
                  Unable to connect to the backend API at <span className="text-cyan-400 font-mono">http://localhost:8000</span>.
                  Please make sure the FastAPI backend is running.
                </p>
                <button
                  onClick={checkBackendHealth}
                  className="mt-3 px-4 py-2 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-400/50 rounded-lg text-sm font-semibold text-rose-300 transition-all duration-200"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tab Switcher - Only show when not processing and no results */}
        {!results && !processing && !error && (
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={() => setInputMode('upload')}
                className={`
                  flex items-center space-x-3 px-8 py-4 rounded-2xl font-bold text-base transition-all duration-300 shadow-xl
                  ${inputMode === 'upload'
                    ? 'bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 text-white shadow-cyan-500/50 scale-105 ring-2 ring-cyan-400/50'
                    : 'bg-slate-800/50 text-gray-400 hover:text-gray-200 hover:bg-slate-700/50 border border-slate-700/50'
                  }
                `}
              >
                <Upload className="w-6 h-6" />
                <span>Upload Reports</span>
              </button>

              <button
                onClick={() => setInputMode('github')}
                className={`
                  flex items-center space-x-3 px-8 py-4 rounded-2xl font-bold text-base transition-all duration-300 shadow-xl
                  ${inputMode === 'github'
                    ? 'bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-600 text-white shadow-purple-500/50 scale-105 ring-2 ring-purple-400/50'
                    : 'bg-slate-800/50 text-gray-400 hover:text-gray-200 hover:bg-slate-700/50 border border-slate-700/50'
                  }
                `}
              >
                <Github className="w-6 h-6" />
                <span>GitHub Scan</span>
              </button>

              <button
                onClick={() => setInputMode('tracking')}
                className={`
                  flex items-center space-x-3 px-8 py-4 rounded-2xl font-bold text-base transition-all duration-300 shadow-xl
                  ${inputMode === 'tracking'
                    ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-600 text-white shadow-indigo-500/50 scale-105 ring-2 ring-indigo-400/50'
                    : 'bg-slate-800/50 text-gray-400 hover:text-gray-200 hover:bg-slate-700/50 border border-slate-700/50'
                  }
                `}
              >
                <Shield className="w-6 h-6" />
                <span>Policy Tracking</span>
              </button>
            </div>
          </div>
        )}

        {/* Status Banner */}
        {!results && !processing && !error && (
          <div className="mb-6">
            <div className="bg-gradient-to-r from-slate-800/50 via-slate-700/50 to-slate-800/50 rounded-2xl shadow-2xl border border-cyan-500/20 p-5 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {inputMode === 'upload' ? (
                    <Upload className="w-6 h-6 text-cyan-400" />
                  ) : (
                    <Code2 className="w-6 h-6 text-purple-400" />
                  )}
                  <span className="text-base font-semibold text-gray-200">
                    {inputMode === 'upload'
                      ? 'Ready to process security scan reports'
                      : 'Ready to scan GitHub repository'}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <span className={`
                    px-4 py-2 text-sm font-bold rounded-xl
                    ${inputMode === 'upload'
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                      : 'bg-purple-500/20 text-purple-300 border border-purple-400/30'
                    }
                  `}>
                    {inputMode === 'upload' ? 'Upload Mode' : 'GitHub Mode'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {processing && (
          <div className="mb-6">
            <div className="bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 rounded-2xl shadow-2xl shadow-cyan-500/30 border border-cyan-400/30 p-5">
              <div className="flex items-center space-x-4">
                <Activity className="w-6 h-6 text-white animate-pulse" />
                <span className="text-base font-bold text-white tracking-wide">
                  Processing in progress... AI models are generating security policies
                </span>
              </div>
            </div>
          </div>
        )}

        {results && (
          <div className="mb-6">
            <div className="bg-gradient-to-r from-emerald-600 via-green-600 to-teal-600 rounded-2xl shadow-2xl shadow-emerald-500/30 border border-emerald-400/30 p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <CheckCircle className="w-6 h-6 text-white" />
                  <span className="text-base font-bold text-white tracking-wide">
                    Processing Complete! Generated {results.total_policies || results.total_vulns} policies
                  </span>
                </div>
                <button
                  onClick={handleReset}
                  className="bg-white/90 hover:bg-white text-emerald-700 font-bold px-5 py-2.5 rounded-xl text-sm transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  Process New Reports
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-6">
            <div className="bg-gradient-to-r from-rose-900/30 via-red-900/30 to-rose-900/30 border-2 border-rose-500/50 rounded-2xl p-5 shadow-2xl shadow-rose-500/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <svg className="w-7 h-7 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h3 className="text-base font-bold text-rose-300">Processing Error</h3>
                    <p className="text-sm text-gray-300 mt-1">{error}</p>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="bg-rose-500/20 hover:bg-rose-500/30 border border-rose-400/50 text-rose-300 font-bold px-5 py-2.5 rounded-xl text-sm transition-all duration-200"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="space-y-6">
          {!processing && !results && (
            <>
              {inputMode === 'upload' && (
                <UploadMode
                  onFilesChange={handleFilesChange}
                  onSubmit={handleGeneratePolicies}
                  loading={processing}
                  onProfileChange={setUserProfile}
                />
              )}
              {inputMode === 'github' && (
                <GitHubMode
                  config={githubConfig}
                  onConfigChange={setGithubConfig}
                  onSubmit={handleGeneratePolicies}
                  loading={processing}
                />
              )}
              {inputMode === 'tracking' && (
                <PolicyTracking />
              )}
            </>
          )}

          {processing && (
            <WorkflowView progress={progress} inputMode={inputMode} />
          )}

          {results && (
            <ResultsView results={results} />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-slate-900 via-gray-900 to-slate-900 border-t border-cyan-500/20 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              SecurAI v1.0
            </p>
            <p className="text-sm text-gray-400 mt-2 tracking-wide">
              Powered by <span className="text-cyan-400">Groq API</span> · <span className="text-blue-400">LLaMA 3.3 70B</span> · <span className="text-indigo-400">ChromaDB RAG</span> · <span className="text-purple-400">NIST CSF</span> · <span className="text-violet-400">ISO 27001</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
