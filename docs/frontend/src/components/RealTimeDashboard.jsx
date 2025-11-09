import React from 'react';
import {
  Activity,
  FileText,
  Database,
  Cpu,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader
} from 'lucide-react';

const RealTimeDashboard = ({ progress }) => {
  const phases = [
    {
      id: 'parsing',
      title: 'Phase 1: Parsing Reports',
      icon: FileText,
      description: 'Extracting vulnerabilities from uploaded reports',
      color: 'blue',
    },
    {
      id: 'rag',
      title: 'Phase 2: RAG Retrieval',
      icon: Database,
      description: 'Fetching compliance context from vector database',
      color: 'purple',
    },
    {
      id: 'llm_generation',
      title: 'Phase 3: AI Policy Generation',
      icon: Cpu,
      description: 'Generating policies using LLaMA models',
      color: 'green',
    },
    {
      id: 'saving',
      title: 'Phase 4: Saving Results',
      icon: CheckCircle,
      description: 'Saving generated policies and reports',
      color: 'indigo',
    },
  ];

  const getPhaseStatus = (phaseId) => {
    const phaseProgress = progress.find(p => p.phase === phaseId);
    if (!phaseProgress) return 'pending';
    return phaseProgress.status;
  };

  const getPhaseMessage = (phaseId) => {
    const phaseProgress = progress.find(p => p.phase === phaseId);
    return phaseProgress?.message || '';
  };

  const getPhaseData = (phaseId) => {
    const phaseProgress = progress.find(p => p.phase === phaseId);
    return phaseProgress?.data || {};
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'in_progress':
        return <Loader className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'in_progress':
        return 'border-blue-500 bg-blue-50';
      case 'completed':
        return 'border-green-500 bg-green-50';
      case 'error':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-6 shadow-lg">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-white bg-opacity-20 rounded-lg">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Real-Time Processing Dashboard</h2>
            <p className="text-blue-100">Monitor AI policy generation in real-time</p>
          </div>
        </div>
      </div>

      {progress.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <Loader className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Initializing processing pipeline...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {phases.map((phase, index) => {
            const status = getPhaseStatus(phase.id);
            const message = getPhaseMessage(phase.id);
            const data = getPhaseData(phase.id);
            const Icon = phase.icon;

            return (
              <div
                key={phase.id}
                className={`
                  border-2 rounded-lg p-6 transition-all
                  ${getStatusColor(status)}
                  ${status === 'in_progress' ? 'shadow-lg' : ''}
                `}
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg bg-${phase.color}-100 border border-${phase.color}-200 flex-shrink-0`}>
                    <Icon className={`w-6 h-6 text-${phase.color}-600`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-bold text-gray-900">{phase.title}</h3>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(status)}
                        <span className="text-sm font-medium text-gray-600 capitalize">
                          {status === 'in_progress' ? 'Processing...' : status}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mb-3">{phase.description}</p>

                    {message && (
                      <div className="bg-white rounded-lg p-3 mb-3 border border-gray-200">
                        <p className="text-sm text-gray-700">{message}</p>
                      </div>
                    )}

                    {/* Phase-specific data display */}
                    {phase.id === 'parsing' && data.vulnerabilities && (
                      <div className="grid grid-cols-3 gap-4 mt-3">
                        {data.sast_count !== undefined && (
                          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                            <p className="text-xs text-blue-600 font-medium mb-1">SAST</p>
                            <p className="text-2xl font-bold text-blue-900">{data.sast_count}</p>
                            <p className="text-xs text-blue-600">vulnerabilities</p>
                          </div>
                        )}
                        {data.sca_count !== undefined && (
                          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                            <p className="text-xs text-green-600 font-medium mb-1">SCA</p>
                            <p className="text-2xl font-bold text-green-900">{data.sca_count}</p>
                            <p className="text-xs text-green-600">vulnerabilities</p>
                          </div>
                        )}
                        {data.dast_count !== undefined && (
                          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                            <p className="text-xs text-purple-600 font-medium mb-1">DAST</p>
                            <p className="text-2xl font-bold text-purple-900">{data.dast_count}</p>
                            <p className="text-xs text-purple-600">vulnerabilities</p>
                          </div>
                        )}
                      </div>
                    )}

                    {phase.id === 'rag' && data.contexts_retrieved && (
                      <div className="bg-purple-50 rounded-lg p-3 border border-purple-200 mt-3">
                        <p className="text-sm font-medium text-purple-900">
                          Retrieved {data.contexts_retrieved} compliance contexts from vector database
                        </p>
                        {data.standards && (
                          <p className="text-xs text-purple-700 mt-1">
                            Standards: {data.standards.join(', ')}
                          </p>
                        )}
                      </div>
                    )}

                    {phase.id === 'llm_generation' && data.current_vuln && (
                      <div className="space-y-2 mt-3">
                        <div className="bg-white rounded-lg p-3 border border-gray-200">
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-sm font-medium text-gray-900">
                              Processing: {data.current_vuln.title}
                            </p>
                            <span className={`
                              px-2 py-1 text-xs font-medium rounded
                              ${data.current_vuln.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' : ''}
                              ${data.current_vuln.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' : ''}
                              ${data.current_vuln.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' : ''}
                              ${data.current_vuln.severity === 'LOW' ? 'bg-blue-100 text-blue-800' : ''}
                            `}>
                              {data.current_vuln.severity}
                            </span>
                          </div>
                          <p className="text-xs text-gray-600">
                            LLM: {data.llm_model} | Progress: {data.processed}/{data.total}
                          </p>
                        </div>
                        {data.progress_percentage !== undefined && (
                          <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-green-600 h-full transition-all duration-300"
                              style={{ width: `${data.progress_percentage}%` }}
                            />
                          </div>
                        )}
                      </div>
                    )}

                    {phase.id === 'saving' && data.files_saved && (
                      <div className="bg-green-50 rounded-lg p-3 border border-green-200 mt-3">
                        <p className="text-sm font-medium text-green-900 mb-2">
                          Saved {data.files_saved.length} file(s):
                        </p>
                        <ul className="space-y-1">
                          {data.files_saved.map((file, idx) => (
                            <li key={idx} className="text-xs text-green-700 flex items-center space-x-2">
                              <CheckCircle className="w-3 h-3" />
                              <span className="font-mono">{file}</span>
                            </li>
                          ))}
                        </ul>
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

export default RealTimeDashboard;
