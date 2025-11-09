import React, { useState, useEffect } from 'react';
import { Github, Check, AlertCircle, LogOut } from 'lucide-react';
import apiClient from '../utils/api';

const GitHubLogin = ({ onAuthSuccess, onAuthError }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('github_token');
    if (token) {
      validateAndLoadUser(token);
    }
  }, []);

  const validateAndLoadUser = async (token) => {
    try {
      setLoading(true);
      const userData = await apiClient.getGitHubUser(token);
      setUser(userData);
      if (onAuthSuccess) {
        onAuthSuccess(token, userData);
      }
    } catch (err) {
      console.error('Token validation failed:', err);
      localStorage.removeItem('github_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get auth URL from backend
      const authData = await apiClient.getGitHubAuthUrl();

      // Save state for CSRF protection
      localStorage.setItem('github_oauth_state', authData.state);

      // Open GitHub OAuth popup
      const width = 600;
      const height = 700;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;

      const popup = window.open(
        authData.auth_url,
        'GitHub Login',
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no,location=no`
      );

      // Listen for OAuth callback message
      window.addEventListener('message', handleOAuthCallback);

      // Check if popup was closed before completing auth
      const checkPopupClosed = setInterval(() => {
        if (popup && popup.closed) {
          clearInterval(checkPopupClosed);
          setLoading(false);
          window.removeEventListener('message', handleOAuthCallback);
        }
      }, 500);

    } catch (err) {
      console.error('GitHub login error:', err);
      setError(err.message || 'Failed to initiate GitHub login');
      setLoading(false);
      if (onAuthError) {
        onAuthError(err);
      }
    }
  };

  const handleOAuthCallback = async (event) => {
    // Verify origin for security
    if (event.origin !== window.location.origin) return;

    const { token, error: callbackError } = event.data;

    if (callbackError) {
      setError(callbackError);
      setLoading(false);
      if (onAuthError) {
        onAuthError(new Error(callbackError));
      }
      return;
    }

    if (token) {
      try {
        // Store token
        localStorage.setItem('github_token', token);

        // Load user info
        await validateAndLoadUser(token);

        window.removeEventListener('message', handleOAuthCallback);
      } catch (err) {
        setError('Failed to load user information');
        setLoading(false);
        if (onAuthError) {
          onAuthError(err);
        }
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('github_token');
    localStorage.removeItem('github_oauth_state');
    setUser(null);
    if (onAuthSuccess) {
      onAuthSuccess(null, null);
    }
  };

  // Logged In State
  if (user) {
    return (
      <div className="bg-gradient-to-br from-emerald-500/10 via-teal-500/10 to-cyan-500/10 border-2 border-emerald-400/30 rounded-2xl p-5 backdrop-blur-sm shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <img
              src={user.avatar_url}
              alt={user.login}
              className="w-14 h-14 rounded-full border-2 border-emerald-400 shadow-lg"
            />
            <div>
              <div className="flex items-center space-x-2">
                <p className="text-base font-bold text-gray-100">
                  {user.name || user.login}
                </p>
                <Check className="w-5 h-5 text-emerald-400" />
              </div>
              <p className="text-sm text-gray-400">@{user.login}</p>
              <p className="text-xs text-emerald-400 font-semibold mt-1">
                ✓ Private repos accessible
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 rounded-xl transition-colors flex items-center space-x-2 border border-rose-400/30"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm font-semibold">Logout</span>
          </button>
        </div>
      </div>
    );
  }

  // Login Button State
  return (
    <div className="bg-gradient-to-br from-slate-800/50 via-gray-800/50 to-slate-800/50 border-2 border-purple-500/30 rounded-2xl p-6 backdrop-blur-sm shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <Github className="w-6 h-6 text-purple-400" />
            <h3 className="text-lg font-bold text-gray-100">
              GitHub Authentication
            </h3>
          </div>
          <p className="text-sm text-gray-400">
            Connect your GitHub account to access private repositories
          </p>
        </div>
        <button
          onClick={handleLogin}
          disabled={loading}
          className="
            px-6 py-3 bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-600
            hover:from-purple-400 hover:via-violet-400 hover:to-indigo-500
            text-white font-bold rounded-xl transition-all duration-300
            shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50
            disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center space-x-2
          "
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Connecting...</span>
            </>
          ) : (
            <>
              <Github className="w-5 h-5" />
              <span>Connect GitHub</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="mt-4 flex items-center space-x-2 text-rose-400 text-sm bg-rose-500/10 rounded-xl p-3 border border-rose-400/30">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500 bg-slate-900/50 rounded-xl p-3 border border-slate-700/50">
        <p className="font-semibold text-gray-400 mb-1">Required Permissions:</p>
        <ul className="space-y-1">
          <li>• Read access to private repositories</li>
          <li>• User profile information</li>
        </ul>
      </div>
    </div>
  );
};

export default GitHubLogin;
