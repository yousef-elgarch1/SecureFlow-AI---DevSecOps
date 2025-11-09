import React, { useState } from 'react';
import {
  Download,
  FileText,
  Shield,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  CheckCircle,
  Award,
  BarChart3
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import StatsCard from './StatsCard';
import ComplianceValidation from './ComplianceValidation';
import ComplianceChecklist from './ComplianceChecklist';
import ComplianceTest from './ComplianceTest';
import apiClient from '../utils/api';

const ResultsView = ({ results }) => {
  const [expandedPolicies, setExpandedPolicies] = useState(new Set());

  // Debug: Log what we receive
  console.log('ResultsView received results:', results);

  // Check if results is valid
  if (!results) {
    return <div className="p-6 text-center text-red-600">No results data received</div>;
  }

  if (!results.results || !Array.isArray(results.results)) {
    console.error('Invalid results structure:', results);
    return <div className="p-6 text-center text-red-600">Invalid results structure received</div>;
  }

  const togglePolicy = (index) => {
    const newExpanded = new Set(expandedPolicies);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedPolicies(newExpanded);
  };

  const handleDownload = async (format) => {
    try {
      // Get the filename from results.output_files or fallback to timestamp
      let filename;

      if (results.output_files && results.output_files[format]) {
        filename = results.output_files[format];
      } else if (results.timestamp) {
        // Generate filename based on timestamp
        const timestamp = results.timestamp.replace(/[:.]/g, '-').substring(0, 19).replace('T', '_');
        filename = `security_policy_${timestamp}.${format}`;
      } else {
        filename = `security_policy.${format}`;
      }

      // Remove 'outputs/' prefix if present
      filename = filename.replace('outputs/', '');

      console.log(`Downloading ${format} file: ${filename}`);
      await apiClient.downloadPolicy(filename);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file: ' + error.message);
    }
  };

  // Calculate statistics
  const severityStats = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
  };

  const typeStats = {
    SAST: 0,
    SCA: 0,
    DAST: 0,
  };

  results.results.forEach(policy => {
    if (policy.vulnerability.severity) {
      severityStats[policy.vulnerability.severity]++;
    }
    if (policy.type) {
      typeStats[policy.type]++;
    }
  });

  const severityChartData = Object.entries(severityStats)
    .filter(([_, count]) => count > 0)
    .map(([severity, count]) => ({ severity, count }));

  const typeChartData = Object.entries(typeStats)
    .filter(([_, count]) => count > 0)
    .map(([type, count]) => ({ type, count }));

  const COLORS = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MEDIUM: '#eab308',
    LOW: '#3b82f6',
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'red';
      case 'HIGH': return 'yellow';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'blue';
      default: return 'blue';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'SAST': return 'blue';
      case 'SCA': return 'green';
      case 'DAST': return 'purple';
      default: return 'blue';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white bg-opacity-20 rounded-lg">
              <CheckCircle className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Policies Generated Successfully!</h2>
              <p className="text-green-100">
                Generated {results.total_vulns} security policies with compliance mappings
              </p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => handleDownload('txt')}
              className="bg-white text-green-600 hover:bg-green-50 px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors shadow-md hover:shadow-lg"
              title="Download as plain text"
            >
              <Download className="w-4 h-4" />
              <span>TXT</span>
            </button>
            <button
              onClick={() => handleDownload('html')}
              className="bg-white text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors shadow-md hover:shadow-lg"
              title="Download as formatted HTML"
            >
              <Download className="w-4 h-4" />
              <span>HTML</span>
            </button>
            <button
              onClick={() => handleDownload('pdf')}
              className="bg-white text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors shadow-md hover:shadow-lg"
              title="Download as PDF"
            >
              <Download className="w-4 h-4" />
              <span>PDF</span>
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Total Policies"
          value={results.total_vulns}
          icon={FileText}
          color="blue"
        />
        <StatsCard
          title="Critical & High"
          value={severityStats.CRITICAL + severityStats.HIGH}
          icon={AlertTriangle}
          color="red"
        />
        <StatsCard
          title="AI Models Used"
          value={new Set(results.results.map(r => r.llm_used)).size}
          icon={Award}
          color="purple"
        />
        <StatsCard
          title="Compliance Mapped"
          value="100%"
          icon={Shield}
          color="green"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <span>Severity Distribution</span>
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={severityChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="severity" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6">
                {severityChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.severity]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-green-600" />
            <span>Scan Type Distribution</span>
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={typeChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ type, count }) => `${type}: ${count}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {typeChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={
                    entry.type === 'SAST' ? '#3b82f6' :
                    entry.type === 'SCA' ? '#10b981' :
                    '#a855f7'
                  } />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Evaluation Metrics */}
      {results.evaluation && (
        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Award className="w-5 h-5 text-purple-600" />
            <span>Policy Quality Metrics</span>
          </h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
              <p className="text-sm text-purple-600 font-medium mb-1">Average BLEU-4</p>
              <p className="text-2xl font-bold text-purple-900">
                {(results.evaluation.avg_bleu * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-600 font-medium mb-1">Average ROUGE-L</p>
              <p className="text-2xl font-bold text-blue-900">
                {(results.evaluation.avg_rouge * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <p className="text-sm text-green-600 font-medium mb-1">Quality Score</p>
              <p className="text-2xl font-bold text-green-900">
                {((results.evaluation.avg_bleu + results.evaluation.avg_rouge) * 50).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Compliance Validation Section */}
      {results.compliance_analysis && (
        <ComplianceValidation analysis={results.compliance_analysis} />
      )}

      {/* Compliance Checklist Section */}
      {results.compliance_analysis && (
        <ComplianceChecklist
          analysis={results.compliance_analysis}
          policies={results.results}
        />
      )}

      {/* Compliance Test Section - Upload PDF for Comparison */}
      <ComplianceTest generatedPolicies={results.results} />

      {/* Policies List */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
            <Shield className="w-6 h-6 text-blue-600" />
            <span>Generated Security Policies</span>
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Click on any policy to expand and view details
          </p>
        </div>

        <div className="divide-y divide-gray-200">
          {results.results.map((policy, index) => {
            const isExpanded = expandedPolicies.has(index);
            const severityColor = getSeverityColor(policy.vulnerability.severity);
            const typeColor = getTypeColor(policy.type);

            return (
              <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
                <div
                  className="cursor-pointer"
                  onClick={() => togglePolicy(index)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className={`px-3 py-1 bg-${typeColor}-100 text-${typeColor}-800 text-xs font-bold rounded-full`}>
                          {policy.type}
                        </span>
                        <span className={`px-3 py-1 bg-${severityColor}-100 text-${severityColor}-800 text-xs font-bold rounded-full`}>
                          {policy.vulnerability.severity}
                        </span>
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">
                          {policy.llm_used}
                        </span>
                      </div>
                      <h4 className="text-lg font-bold text-gray-900 mb-1">
                        {policy.vulnerability.title}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {policy.vulnerability.category}
                        {policy.vulnerability.cwe_id && ` • CWE-${policy.vulnerability.cwe_id}`}
                      </p>
                    </div>
                    <button className="text-gray-400 hover:text-gray-600 transition-colors">
                      {isExpanded ? (
                        <ChevronUp className="w-6 h-6" />
                      ) : (
                        <ChevronDown className="w-6 h-6" />
                      )}
                    </button>
                  </div>

                  {!isExpanded && (
                    <p className="text-sm text-gray-500 line-clamp-2">
                      {policy.policy.substring(0, 150)}...
                    </p>
                  )}
                </div>

                {isExpanded && (
                  <div className="mt-4 space-y-4 pl-4 border-l-4 border-blue-500">
                    {/* Vulnerability Details */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="text-sm font-bold text-gray-900 mb-2">Vulnerability Details</h5>
                      <p className="text-sm text-gray-700 mb-2">{policy.vulnerability.description}</p>
                      {policy.vulnerability.file_path && (
                        <p className="text-xs text-gray-600">
                          <span className="font-medium">Location:</span>{' '}
                          {policy.vulnerability.file_path}
                          {policy.vulnerability.line_number && `:${policy.vulnerability.line_number}`}
                        </p>
                      )}
                    </div>

                    {/* Generated Policy */}
                    <div>
                      <h5 className="text-sm font-bold text-gray-900 mb-2">Generated Security Policy</h5>
                      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm whitespace-pre-wrap font-mono">
                        {policy.policy}
                      </pre>
                    </div>

                    {/* Compliance Mapping */}
                    {policy.compliance_mapping && Object.keys(policy.compliance_mapping).length > 0 && (
                      <div>
                        <h5 className="text-sm font-bold text-gray-900 mb-2 flex items-center space-x-2">
                          <Shield className="w-4 h-4 text-green-600" />
                          <span>Compliance Mappings</span>
                        </h5>
                        <div className="grid grid-cols-2 gap-3">
                          {Object.entries(policy.compliance_mapping).map(([standard, controls]) => (
                            <div key={standard} className="bg-green-50 rounded-lg p-3 border border-green-200">
                              <p className="text-xs font-bold text-green-900 mb-1">{standard}</p>
                              <p className="text-xs text-green-700 font-mono">{controls.join(', ')}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Evaluation Scores */}
                    {policy.scores && (
                      <div className="flex space-x-4">
                        <div className="bg-blue-50 rounded-lg p-3 border border-blue-200 flex-1">
                          <p className="text-xs text-blue-600 font-medium mb-1">BLEU-4 Score</p>
                          <p className="text-lg font-bold text-blue-900">
                            {(policy.scores.bleu * 100).toFixed(1)}%
                          </p>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-3 border border-purple-200 flex-1">
                          <p className="text-xs text-purple-600 font-medium mb-1">ROUGE-L Score</p>
                          <p className="text-lg font-bold text-purple-900">
                            {(policy.scores.rouge * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ResultsView;
