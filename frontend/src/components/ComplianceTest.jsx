import React, { useState } from 'react';
import {
  Upload,
  FileText,
  Award,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  FileCheck
} from 'lucide-react';
import apiClient from '../utils/api';

const ComplianceTest = ({ generatedPolicies }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    // Validate PDF
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    setUploadedFile(file);
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('reference_pdf', file);

      const result = await apiClient.comparePolicies(formData);
      setComparison(result);
      setError(null);
    } catch (err) {
      console.error('Comparison error:', err);
      setError(err.message || 'Failed to compare policies');
      setComparison(null);
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (similarity) => {
    if (similarity >= 90) return 'from-green-500 to-emerald-600';
    if (similarity >= 80) return 'from-blue-500 to-cyan-600';
    if (similarity >= 70) return 'from-yellow-500 to-orange-500';
    if (similarity >= 60) return 'from-orange-500 to-red-500';
    return 'from-red-500 to-rose-600';
  };

  const getGradeLetter = (similarity) => {
    if (similarity >= 90) return 'A';
    if (similarity >= 80) return 'B';
    if (similarity >= 70) return 'C';
    if (similarity >= 60) return 'D';
    return 'F';
  };

  const getScoreIcon = (similarity) => {
    if (similarity >= 70) return <CheckCircle className="w-8 h-8" />;
    return <AlertTriangle className="w-8 h-8" />;
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-2xl shadow-2xl p-8 border border-indigo-200">
      <div className="flex items-center space-x-4 mb-6">
        <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl">
          <FileCheck className="w-8 h-8 text-white" />
        </div>
        <div>
          <h3 className="text-2xl font-bold text-gray-900">Compliance Test</h3>
          <p className="text-gray-600 mt-1">
            Upload your manual policy PDF to compare with AI-generated policies
          </p>
        </div>
      </div>

      {/* Upload Area */}
      {!comparison && (
        <div
          className={`mt-6 border-3 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
            dragActive
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-25'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="w-16 h-16 text-indigo-400 mx-auto mb-4" />
          <h4 className="text-xl font-bold text-gray-800 mb-2">
            Drop your PDF here or click to browse
          </h4>
          <p className="text-gray-500 mb-6">
            Upload your manually created security policy (PDF format)
          </p>

          <input
            type="file"
            id="pdf-upload"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
          />
          <label
            htmlFor="pdf-upload"
            className="cursor-pointer bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold px-8 py-4 rounded-xl inline-flex items-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <FileText className="w-5 h-5" />
            <span>Select PDF File</span>
          </label>

          {uploadedFile && !loading && !comparison && (
            <div className="mt-6 bg-indigo-50 border border-indigo-200 rounded-xl p-4">
              <p className="text-indigo-900 font-medium flex items-center justify-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>{uploadedFile.name}</span>
              </p>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="mt-8 bg-white rounded-xl p-12 text-center shadow-lg border border-indigo-100">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600 mx-auto mb-4"></div>
          <p className="text-lg font-semibold text-gray-700">Analyzing your policy...</p>
          <p className="text-sm text-gray-500 mt-2">
            Comparing against AI-generated policies using BLEU and ROUGE metrics
          </p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mt-6 bg-red-50 border-2 border-red-300 rounded-xl p-6">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-6 h-6 text-red-600" />
            <div>
              <h4 className="font-bold text-red-900">Error</h4>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={() => {
              setError(null);
              setUploadedFile(null);
              setComparison(null);
            }}
            className="mt-4 bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Comparison Results */}
      {comparison && comparison.success && (
        <div className="mt-8 space-y-6">
          {/* Overall Grade Card */}
          <div className={`bg-gradient-to-r ${getGradeColor(comparison.summary.overall_similarity)} rounded-2xl p-8 text-white shadow-2xl`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="bg-white bg-opacity-20 rounded-2xl p-6">
                  {getScoreIcon(comparison.summary.overall_similarity)}
                </div>
                <div>
                  <h3 className="text-5xl font-bold mb-2">
                    Grade: {getGradeLetter(comparison.summary.overall_similarity)}
                  </h3>
                  <p className="text-xl opacity-90">{comparison.summary.grade}</p>
                  <p className="text-lg opacity-80 mt-2">
                    {comparison.summary.overall_similarity.toFixed(1)}% Overall Similarity
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm opacity-80">Reference PDF</p>
                <p className="font-semibold text-lg">{comparison.reference_info.filename}</p>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* BLEU Score */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-purple-100">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-100 rounded-xl">
                  <Award className="w-6 h-6 text-purple-600" />
                </div>
                <span className="text-3xl font-bold text-purple-600">
                  {(comparison.summary.bleu_score * 100).toFixed(1)}%
                </span>
              </div>
              <h4 className="font-bold text-gray-900 text-lg">BLEU-4 Score</h4>
              <p className="text-sm text-gray-600 mt-2">
                Measures text similarity using n-gram precision
              </p>
              <div className="mt-4 bg-purple-50 rounded-lg p-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-indigo-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${comparison.summary.bleu_score * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* ROUGE-L Score */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-blue-100">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-100 rounded-xl">
                  <BarChart3 className="w-6 h-6 text-blue-600" />
                </div>
                <span className="text-3xl font-bold text-blue-600">
                  {(comparison.summary.rouge_l_score * 100).toFixed(1)}%
                </span>
              </div>
              <h4 className="font-bold text-gray-900 text-lg">ROUGE-L Score</h4>
              <p className="text-sm text-gray-600 mt-2">
                Longest common subsequence overlap
              </p>
              <div className="mt-4 bg-blue-50 rounded-lg p-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-cyan-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${comparison.summary.rouge_l_score * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Key Terms Coverage */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border border-green-100">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-100 rounded-xl">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <span className="text-3xl font-bold text-green-600">
                  {comparison.summary.key_terms_coverage.toFixed(1)}%
                </span>
              </div>
              <h4 className="font-bold text-gray-900 text-lg">Key Terms Coverage</h4>
              <p className="text-sm text-gray-600 mt-2">
                Security terminology match rate
              </p>
              <div className="mt-4 bg-green-50 rounded-lg p-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${comparison.summary.key_terms_coverage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Document Stats Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
              <h4 className="font-bold text-gray-900 text-lg mb-4">Reference Document</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Word Count:</span>
                  <span className="font-bold text-gray-900">{comparison.reference_info.word_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Sections Found:</span>
                  <span className="font-bold text-gray-900">{comparison.reference_info.sections_found}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
              <h4 className="font-bold text-gray-900 text-lg mb-4">Generated Document</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Word Count:</span>
                  <span className="font-bold text-gray-900">{comparison.generated_info.word_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Sections Found:</span>
                  <span className="font-bold text-gray-900">{comparison.generated_info.sections_found}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Report */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h4 className="font-bold text-gray-900 text-lg flex items-center space-x-2">
                <FileText className="w-5 h-5 text-indigo-600" />
                <span>Detailed Comparison Report</span>
              </h4>
            </div>
            <div className="p-6">
              <pre className="bg-gray-50 rounded-lg p-6 text-sm text-gray-800 overflow-x-auto whitespace-pre-wrap font-mono">
                {comparison.detailed_report}
              </pre>
            </div>
          </div>

          {/* Reset Button */}
          <div className="text-center">
            <button
              onClick={() => {
                setComparison(null);
                setUploadedFile(null);
                setError(null);
              }}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold px-8 py-4 rounded-xl inline-flex items-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Upload className="w-5 h-5" />
              <span>Test Another Policy</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplianceTest;
