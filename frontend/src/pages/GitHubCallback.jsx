import React, { useEffect, useState } from 'react';
import { Github, Check, AlertCircle, Loader } from 'lucide-react';
import apiClient from '../utils/api';

const GitHubCallback = () => {
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Completing GitHub authentication...');

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      // Get code and state from URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const error = urlParams.get('error');
      const errorDescription = urlParams.get('error_description');

      // Check for OAuth errors
      if (error) {
        throw new Error(errorDescription || error);
      }

      // Verify code exists
      if (!code) {
        throw new Error('No authorization code received from GitHub');
      }

      // Verify state for CSRF protection
      const savedState = localStorage.getItem('github_oauth_state');
      if (state !== savedState) {
        throw new Error('Invalid state parameter - possible CSRF attack');
      }

      setMessage('Exchanging authorization code for access token...');

      // Exchange code for access token
      const tokenData = await apiClient.exchangeGitHubCode(code, state);

      if (!tokenData.access_token) {
        throw new Error('No access token received');
      }

      setMessage('Verifying access token...');

      // Verify token works by fetching user info
      const userData = await apiClient.getGitHubUser(tokenData.access_token);

      // Success!
      setStatus('success');
      setMessage(`Successfully authenticated as @${userData.login}`);

      // Send token to parent window (opener)
      if (window.opener) {
        window.opener.postMessage(
          {
            token: tokenData.access_token,
            user: userData
          },
          window.location.origin
        );

        // Close popup after short delay
        setTimeout(() => {
          window.close();
        }, 1500);
      } else {
        // Not in popup - redirect to home with token
        localStorage.setItem('github_token', tokenData.access_token);
        setTimeout(() => {
          window.location.href = '/';
        }, 1500);
      }

    } catch (err) {
      console.error('OAuth callback error:', err);
      setStatus('error');
      setMessage(err.message || 'Authentication failed');

      // Send error to parent window
      if (window.opener) {
        window.opener.postMessage(
          {
            error: err.message
          },
          window.location.origin
        );

        // Close popup after delay
        setTimeout(() => {
          window.close();
        }, 3000);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="bg-gradient-to-br from-slate-800/50 via-gray-800/50 to-slate-800/50 rounded-3xl border border-purple-500/30 p-10 backdrop-blur-sm shadow-2xl shadow-purple-500/20">

          {/* Icon */}
          <div className="flex justify-center mb-6">
            {status === 'processing' && (
              <div className="p-5 bg-purple-500/20 rounded-full">
                <Loader className="w-16 h-16 text-purple-400 animate-spin" />
              </div>
            )}
            {status === 'success' && (
              <div className="p-5 bg-emerald-500/20 rounded-full animate-pulse">
                <Check className="w-16 h-16 text-emerald-400" />
              </div>
            )}
            {status === 'error' && (
              <div className="p-5 bg-rose-500/20 rounded-full">
                <AlertCircle className="w-16 h-16 text-rose-400" />
              </div>
            )}
          </div>

          {/* Title */}
          <h2 className={`text-2xl font-bold text-center mb-3 ${
            status === 'success' ? 'text-emerald-300' :
            status === 'error' ? 'text-rose-300' :
            'text-purple-300'
          }`}>
            {status === 'processing' && 'Authenticating...'}
            {status === 'success' && 'Success!'}
            {status === 'error' && 'Authentication Failed'}
          </h2>

          {/* Message */}
          <p className="text-center text-gray-300 text-sm mb-6">
            {message}
          </p>

          {/* GitHub Logo */}
          <div className="flex justify-center opacity-50">
            <Github className="w-10 h-10 text-gray-400" />
          </div>

          {/* Progress indicator */}
          {status === 'processing' && (
            <div className="mt-6">
              <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-purple-500 to-violet-500 animate-pulse" style={{ width: '70%' }}></div>
              </div>
            </div>
          )}

          {/* Auto-close message */}
          {(status === 'success' || status === 'error') && (
            <p className="text-center text-xs text-gray-500 mt-6">
              This window will close automatically...
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default GitHubCallback;
