import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Trash2, Sparkles, User, Award } from 'lucide-react';

const UploadMode = ({ onFilesChange, onSubmit, loading, onProfileChange }) => {
  const [files, setFiles] = useState({ sast: null, sca: null, dast: null });
  const [dragOver, setDragOver] = useState({ sast: false, sca: false, dast: false });
  const [userProfile, setUserProfile] = useState({
    expertise_level: 'intermediate',
    user_role: 'senior_developer',
    user_name: ''
  });

  const fileInputRefs = {
    sast: useRef(null),
    sca: useRef(null),
    dast: useRef(null),
  };

  const scanTypes = [
    {
      key: 'sast',
      title: 'SAST Report',
      description: 'Static Application Security Testing',
      accept: '.json',
      example: 'semgrep_report.json',
      color: 'cyan',
      gradient: 'from-cyan-500 to-blue-500',
    },
    {
      key: 'sca',
      title: 'SCA Report',
      description: 'Software Composition Analysis',
      accept: '.json',
      example: 'npm_audit.json, trivy_report.json',
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-500',
    },
    {
      key: 'dast',
      title: 'DAST Report',
      description: 'Dynamic Application Security Testing',
      accept: '.xml,.json',
      example: 'zap_report.xml',
      color: 'purple',
      gradient: 'from-purple-500 to-violet-500',
    },
  ];

  const handleFileSelect = (type, file) => {
    const newFiles = { ...files, [type]: file };
    setFiles(newFiles);
    onFilesChange(newFiles);
  };

  const handleFileRemove = (type) => {
    const newFiles = { ...files, [type]: null };
    setFiles(newFiles);
    onFilesChange(newFiles);
  };

  const handleDragOver = (e, type) => {
    e.preventDefault();
    setDragOver({ ...dragOver, [type]: true });
  };

  const handleDragLeave = (e, type) => {
    e.preventDefault();
    setDragOver({ ...dragOver, [type]: false });
  };

  const handleDrop = (e, type) => {
    e.preventDefault();
    setDragOver({ ...dragOver, [type]: false });

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(type, droppedFile);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleProfileChange = (field, value) => {
    const newProfile = { ...userProfile, [field]: value };
    setUserProfile(newProfile);
    if (onProfileChange) {
      onProfileChange(newProfile);
    }
  };

  const hasAnyFile = Object.values(files).some(file => file !== null);

  return (
    <div className="space-y-8">
      {/* Header Card */}
      <div className="bg-gradient-to-r from-slate-800/50 via-cyan-900/30 to-slate-800/50 border border-cyan-500/30 rounded-3xl p-8 backdrop-blur-sm shadow-2xl shadow-cyan-500/10">
        <div className="flex items-center space-x-4 mb-3">
          <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-3 rounded-2xl shadow-lg shadow-cyan-500/30">
            <Upload className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
              Upload Security Reports
            </h2>
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed pl-16">
          Upload your SAST, SCA, and/or DAST security scan reports to generate AI-powered, compliance-aligned policies.
          <span className="text-cyan-400 font-semibold"> At least one report is required.</span>
        </p>
      </div>

      {/* Upload Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {scanTypes.map(({ key, title, description, accept, example, color, gradient }) => {
          const file = files[key];
          const isDragOver = dragOver[key];

          return (
            <div
              key={key}
              onDragOver={(e) => handleDragOver(e, key)}
              onDragLeave={(e) => handleDragLeave(e, key)}
              onDrop={(e) => handleDrop(e, key)}
              className={`
                relative border-2 border-dashed rounded-2xl p-6 transition-all duration-300
                ${isDragOver
                  ? `border-${color}-400 bg-${color}-500/10 scale-105 shadow-2xl shadow-${color}-500/30`
                  : file
                    ? `border-${color}-400/50 bg-${color}-500/5`
                    : 'border-slate-700/50 bg-slate-800/30 hover:border-slate-600 hover:bg-slate-800/50'}
              `}
            >
              <input
                ref={fileInputRefs[key]}
                type="file"
                accept={accept}
                onChange={(e) => handleFileSelect(key, e.target.files[0])}
                className="hidden"
              />

              {file ? (
                <div className="space-y-4">
                  {/* File Uploaded State */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className={`w-8 h-8 text-${color}-400 flex-shrink-0`} />
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-bold text-${color}-300 uppercase tracking-wide`}>{title}</p>
                        <p className="text-xs text-gray-400">{description}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleFileRemove(key)}
                      className="text-rose-400 hover:text-rose-300 transition-colors p-1 hover:bg-rose-500/20 rounded-lg"
                      disabled={loading}
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>

                  {/* File Info */}
                  <div className={`bg-slate-900/50 rounded-xl p-4 border border-${color}-500/20`}>
                    <div className="flex items-center space-x-2 mb-2">
                      <FileText className={`w-5 h-5 text-${color}-400`} />
                      <p className="text-sm font-semibold text-gray-200 truncate">{file.name}</p>
                    </div>
                    <p className="text-xs text-gray-400 font-mono">{formatFileSize(file.size)}</p>
                  </div>

                  {/* Replace Button */}
                  <button
                    onClick={() => fileInputRefs[key].current.click()}
                    className={`w-full text-sm text-${color}-400 hover:text-${color}-300 font-semibold transition-colors`}
                    disabled={loading}
                  >
                    Replace file →
                  </button>
                </div>
              ) : (
                <div className="text-center space-y-4">
                  {/* Empty State */}
                  <div className="flex justify-center">
                    <div className={`p-5 rounded-2xl bg-gradient-to-br ${gradient} opacity-20`}>
                      <Upload className="w-10 h-10 text-white" />
                    </div>
                  </div>

                  <div>
                    <p className={`text-base font-bold text-${color}-300 uppercase tracking-wide mb-1`}>{title}</p>
                    <p className="text-xs text-gray-400">{description}</p>
                  </div>

                  <button
                    onClick={() => fileInputRefs[key].current.click()}
                    className={`
                      w-full bg-gradient-to-r ${gradient} hover:opacity-90
                      text-white font-bold py-3 px-4 rounded-xl transition-all duration-200
                      shadow-lg shadow-${color}-500/30 hover:shadow-${color}-500/50
                      disabled:opacity-50 disabled:cursor-not-allowed
                    `}
                    disabled={loading}
                  >
                    Choose File
                  </button>

                  <p className="text-xs text-gray-500 font-medium">
                    or drag and drop here
                  </p>

                  <div className="text-xs text-gray-500 pt-3 border-t border-slate-700/50">
                    <p className="font-semibold mb-1 text-gray-400">Example:</p>
                    <p className="font-mono text-gray-500">{example}</p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* User Profile Section - NEW FEATURE */}
      <div className="bg-gradient-to-br from-indigo-900/30 via-purple-900/30 to-pink-900/30 border border-indigo-500/30 rounded-3xl p-8 backdrop-blur-sm shadow-2xl shadow-indigo-500/10">
        <div className="flex items-center space-x-4 mb-6">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-3 rounded-2xl shadow-lg shadow-indigo-500/30">
            <User className="w-7 h-7 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Personalize Your Policies
            </h3>
            <p className="text-gray-400 text-sm mt-1">
              Get policies tailored to your expertise level and role
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Expertise Level */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-3">
              <Award className="w-4 h-4 inline mr-2" />
              Expertise Level
            </label>
            <select
              value={userProfile.expertise_level}
              onChange={(e) => handleProfileChange('expertise_level', e.target.value)}
              className="w-full bg-slate-800/50 border border-indigo-500/30 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
            >
              <option value="beginner">🎓 Beginner - Learning focused</option>
              <option value="intermediate">💼 Intermediate - Balanced</option>
              <option value="advanced">🔬 Advanced - Technical deep-dive</option>
            </select>
            <p className="text-xs text-gray-500 mt-2">
              {userProfile.expertise_level === 'beginner' && '→ Includes educational content & learning resources'}
              {userProfile.expertise_level === 'intermediate' && '→ Balanced technical details & remediation steps'}
              {userProfile.expertise_level === 'advanced' && '→ CVSS scores, SIEM rules & compliance mapping'}
            </p>
          </div>

          {/* User Role */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-3">
              <User className="w-4 h-4 inline mr-2" />
              Your Role
            </label>
            <select
              value={userProfile.user_role}
              onChange={(e) => handleProfileChange('user_role', e.target.value)}
              className="w-full bg-slate-800/50 border border-purple-500/30 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
            >
              <option value="junior_developer">Junior Developer</option>
              <option value="senior_developer">Senior Developer</option>
              <option value="security_engineer">Security Engineer</option>
              <option value="devops_engineer">DevOps Engineer</option>
              <option value="compliance_officer">Compliance Officer</option>
              <option value="manager">Manager / CISO</option>
            </select>
          </div>

          {/* User Name (Optional) */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-3">
              Name (Optional)
            </label>
            <input
              type="text"
              value={userProfile.user_name}
              onChange={(e) => handleProfileChange('user_name', e.target.value)}
              placeholder="Your name"
              className="w-full bg-slate-800/50 border border-pink-500/30 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-pink-500/50 focus:border-pink-500 transition-all"
            />
          </div>
        </div>
      </div>

      {/* Submit Section */}
      <div className="bg-gradient-to-br from-slate-800/50 via-slate-700/50 to-slate-800/50 border border-cyan-500/20 rounded-3xl p-8 backdrop-blur-sm shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-100 mb-2">Ready to Generate Policies</h3>
            <p className="text-sm text-gray-400">
              {hasAnyFile
                ? `${Object.values(files).filter(f => f).length} security report(s) uploaded and ready for analysis`
                : 'Upload at least one security scan report to continue'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {files.sast && (
              <span className="px-3 py-1.5 bg-cyan-500/20 text-cyan-300 text-xs font-bold rounded-lg border border-cyan-400/30">
                SAST
              </span>
            )}
            {files.sca && (
              <span className="px-3 py-1.5 bg-emerald-500/20 text-emerald-300 text-xs font-bold rounded-lg border border-emerald-400/30">
                SCA
              </span>
            )}
            {files.dast && (
              <span className="px-3 py-1.5 bg-purple-500/20 text-purple-300 text-xs font-bold rounded-lg border border-purple-400/30">
                DAST
              </span>
            )}
          </div>
        </div>

        <button
          onClick={onSubmit}
          disabled={!hasAnyFile || loading}
          className="
            w-full bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600
            hover:from-cyan-400 hover:via-blue-400 hover:to-indigo-500
            text-white font-bold py-5 px-8 rounded-2xl text-lg
            transition-all duration-300 shadow-2xl shadow-cyan-500/30
            hover:shadow-cyan-500/50 hover:scale-[1.02]
            disabled:opacity-50 disabled:cursor-not-allowed
            disabled:from-gray-700 disabled:to-gray-700 disabled:shadow-none
            disabled:hover:scale-100
            flex items-center justify-center space-x-4
          "
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              <span>Generating Policies...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-6 h-6" />
              <span>Generate Security Policies</span>
              <Sparkles className="w-6 h-6" />
            </>
          )}
        </button>

        {hasAnyFile && (
          <div className="mt-4 text-center text-xs text-gray-400">
            <p>
              AI will analyze vulnerabilities, generate policies, and map to <span className="text-cyan-400">NIST CSF</span> + <span className="text-purple-400">ISO 27001</span> controls
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadMode;
