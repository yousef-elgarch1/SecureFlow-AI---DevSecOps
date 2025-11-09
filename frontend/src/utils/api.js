import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

class APIClient {
  constructor() {
    this.ws = null;
    this.messageHandlers = [];
  }

  /**
   * Connect to WebSocket for real-time updates
   */
  connectWebSocket(onMessage, onError) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.ws = new WebSocket(`ws://localhost:8000/ws`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);

        if (onMessage) {
          onMessage(data);
        }

        // Notify all registered handlers
        this.messageHandlers.forEach(handler => handler(data));
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }

  /**
   * Register a message handler for WebSocket messages
   */
  onWebSocketMessage(handler) {
    this.messageHandlers.push(handler);
  }

  /**
   * Disconnect WebSocket
   */
  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.messageHandlers = [];
    }
  }

  /**
   * Send WebSocket message
   */
  sendWebSocketMessage(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket not connected');
    }
  }

  /**
   * Generate policies from uploaded files
   */
  async generatePolicies(files, maxPerType = 5, onProgress, userProfile = null) {
    const formData = new FormData();

    if (files.sast) formData.append('sast_file', files.sast);
    if (files.sca) formData.append('sca_file', files.sca);
    if (files.dast) formData.append('dast_file', files.dast);
    formData.append('max_per_type', maxPerType);

    // Add user profile parameters if provided
    if (userProfile) {
      formData.append('expertise_level', userProfile.expertise_level || 'intermediate');
      formData.append('user_role', userProfile.user_role || 'senior_developer');
      if (userProfile.user_name) {
        formData.append('user_name', userProfile.user_name);
      }
    }

    try {
      // Connect WebSocket for real-time updates
      if (onProgress) {
        this.connectWebSocket(onProgress);
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/generate-policies`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 300000, // 5 minutes timeout
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error generating policies:', error);
      throw error;
    }
  }

  /**
   * Scan GitHub repository
   */
  async scanGitHubRepo(repoUrl, branch = 'main', scanTypes = {sast: true, sca: true, dast: false}, maxPerType = 5, token = null, dastUrl = null, onProgress) {
    try {
      // Connect WebSocket for real-time updates
      if (onProgress) {
        this.connectWebSocket(onProgress);
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/scan-github`,
        {
          repo_url: repoUrl,
          branch,
          scan_types: scanTypes,
          max_per_type: maxPerType,
          token,  // Include GitHub token for private repos
          dast_url: dastUrl,  // Include DAST URL for Tier 1 scanning
        },
        {
          timeout: 1200000, // 20 minutes timeout (increased for large repos)
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error scanning GitHub repo:', error);
      throw error;
    }
  }

  /**
   * Get GitHub OAuth authorization URL
   */
  async getGitHubAuthUrl() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/github`);
      return response.data;
    } catch (error) {
      console.error('Error getting GitHub auth URL:', error);
      throw error;
    }
  }

  /**
   * Exchange GitHub OAuth code for access token
   */
  async exchangeGitHubCode(code, state) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/auth/github/callback`,
        {
          params: { code, state }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error exchanging GitHub code:', error);
      throw error;
    }
  }

  /**
   * Get GitHub user information
   */
  async getGitHubUser(token) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/auth/github/user`,
        {
          params: { token }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting GitHub user:', error);
      throw error;
    }
  }

  /**
   * Validate GitHub access token
   */
  async validateGitHubToken(token) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/auth/github/validate`,
        null,
        {
          params: { token }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error validating GitHub token:', error);
      return { valid: false };
    }
  }

  /**
   * Download generated policy file
   */
  async downloadPolicy(filename) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/download/${filename}`,
        {
          responseType: 'blob',
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Error downloading policy:', error);
      throw error;
    }
  }

  /**
   * Get policy tracking dashboard
   */
  async getPolicyDashboard() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/policies/dashboard`);
      return response.data;
    } catch (error) {
      console.error('Error fetching policy dashboard:', error);
      throw error;
    }
  }

  /**
   * Update policy status
   */
  async updatePolicyStatus(policyId, newStatus, user = null) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/policies/${policyId}/status`,
        null,
        {
          params: { new_status: newStatus, user }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating policy status:', error);
      throw error;
    }
  }

  /**
   * Compare policies - upload reference PDF and compare with generated policies
   */
  async comparePolicies(formData) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/compare-policies`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error comparing policies:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to compare policies'
      );
    }
  }

  /**
   * Check API health
   */
  async checkHealth() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch (error) {
      console.error('Error checking API health:', error);
      return { status: 'error', message: error.message };
    }
  }
}

// Create singleton instance
const apiClient = new APIClient();

export default apiClient;
