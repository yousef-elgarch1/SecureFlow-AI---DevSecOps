import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  Clock,
  AlertCircle,
  PlayCircle,
  Shield,
  TrendingUp,
  Users,
  Calendar
} from 'lucide-react';
import apiClient from '../utils/api';

const PolicyTracking = () => {
  const [policies, setPolicies] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getPolicyDashboard();
      setPolicies(response.policies);
      setStats(response.stats);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      not_started: 'gray',
      in_progress: 'blue',
      under_review: 'yellow',
      fixed: 'green',
      verified: 'emerald',
      reopened: 'red'
    };
    return colors[status] || 'gray';
  };

  const getStatusIcon = (status) => {
    const icons = {
      not_started: Clock,
      in_progress: PlayCircle,
      under_review: AlertCircle,
      fixed: CheckCircle,
      verified: Shield,
      reopened: AlertCircle
    };
    const Icon = icons[status] || Clock;
    return <Icon className="w-5 h-5" />;
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'from-red-500 to-rose-600',
      high: 'from-orange-500 to-red-500',
      medium: 'from-yellow-500 to-orange-500',
      low: 'from-blue-500 to-cyan-500'
    };
    return colors[severity?.toLowerCase()] || 'from-gray-500 to-slate-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-300 rounded-2xl p-8 m-8">
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-8 h-8 text-red-600" />
          <div>
            <h3 className="font-bold text-red-900">Error Loading Dashboard</h3>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        </div>
        <button
          onClick={fetchDashboard}
          className="mt-4 bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded-lg transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900/50 via-purple-900/50 to-pink-900/50 border border-indigo-500/30 rounded-3xl p-8 backdrop-blur-sm shadow-2xl">
        <div className="flex items-center space-x-4 mb-6">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-3 rounded-2xl shadow-lg">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Policy Tracking Dashboard
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Monitor and track security policy implementation
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-slate-800/50 rounded-xl p-4 border border-indigo-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Total Policies</span>
                <Users className="w-5 h-5 text-indigo-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_policies}</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-4 border border-blue-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">In Progress</span>
                <PlayCircle className="w-5 h-5 text-blue-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.in_progress}</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-4 border border-green-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Verified</span>
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.verified}</p>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-4 border border-purple-500/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Compliance</span>
                <TrendingUp className="w-5 h-5 text-purple-400" />
              </div>
              <p className="text-3xl font-bold text-white">{stats.compliance_percentage.toFixed(1)}%</p>
            </div>
          </div>
        )}
      </div>

      {/* Policies List */}
      {policies.length === 0 ? (
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-3xl p-12 text-center">
          <Shield className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-300 mb-2">No Policies Generated Yet</h3>
          <p className="text-gray-500">
            Generate security policies from scan reports to see them tracked here
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {policies.map((policy) => {
            const statusColor = getStatusColor(policy.status);
            const StatusIcon = getStatusIcon(policy.status);

            return (
              <div
                key={policy.policy_id}
                className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6 hover:border-indigo-500/30 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <span className={`px-3 py-1 bg-gradient-to-r ${getSeverityColor(policy.severity)} text-white text-xs font-bold rounded-lg uppercase`}>
                        {policy.severity}
                      </span>
                      <span className={`px-3 py-1 bg-${statusColor}-500/20 text-${statusColor}-300 text-xs font-bold rounded-lg border border-${statusColor}-400/30 capitalize flex items-center space-x-2`}>
                        {StatusIcon}
                        <span>{policy.status.replace('_', ' ')}</span>
                      </span>
                      <span className="text-xs text-gray-500">{policy.policy_id}</span>
                    </div>

                    <h3 className="text-lg font-bold text-gray-200 mb-2">
                      {policy.vulnerability_title}
                    </h3>

                    <div className="flex items-center space-x-6 text-sm text-gray-400">
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4" />
                        <span>Due: {new Date(policy.due_date).toLocaleDateString()}</span>
                      </div>

                      {policy.assigned_to && (
                        <div className="flex items-center space-x-2">
                          <Users className="w-4 h-4" />
                          <span>Assigned to: {policy.assigned_to}</span>
                        </div>
                      )}

                      <div className="flex items-center space-x-2">
                        <span className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded">
                          {policy.vulnerability_type.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    {(policy.nist_csf_controls.length > 0 || policy.iso27001_controls.length > 0) && (
                      <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                        {policy.nist_csf_controls.length > 0 && (
                          <span>NIST CSF: {policy.nist_csf_controls.slice(0, 3).join(', ')}</span>
                        )}
                        {policy.iso27001_controls.length > 0 && (
                          <span>ISO 27001: {policy.iso27001_controls.slice(0, 3).join(', ')}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default PolicyTracking;
