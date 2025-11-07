import React from 'react';
import {
  ChevronDown,
  ChevronRight,
  Clock,
  Loader,
  CheckCircle,
  AlertCircle,
  FileText,
  Database,
  Cpu,
  Save
} from 'lucide-react';
import ParserStep from './ParserStep';
import RAGStep from './RAGStep';
import LLMGenerationStep from './LLMGenerationStep';
import SavingStep from './SavingStep';

const PhaseSection = ({ phase, updates, status, expanded, onToggle }) => {
  // Get phase icon
  const getPhaseIcon = () => {
    const iconMap = {
      parsing: FileText,
      rag: Database,
      llm_generation: Cpu,
      saving: Save,
      complete: CheckCircle,
    };
    const Icon = iconMap[phase.id] || FileText;
    return Icon;
  };

  // Get status icon
  const getStatusIcon = () => {
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

  // Get status color
  const getStatusColor = () => {
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

  // Get status text
  const getStatusText = () => {
    switch (status) {
      case 'in_progress':
        return 'Processing...';
      case 'completed':
        return 'Completed';
      case 'error':
        return 'Error';
      default:
        return 'Pending';
    }
  };

  const PhaseIcon = getPhaseIcon();
  const lastUpdate = updates && updates.length > 0 ? updates[updates.length - 1] : null;

  return (
    <div className={`border-2 rounded-lg transition-all ${getStatusColor()} ${status === 'in_progress' ? 'shadow-lg' : ''}`}>
      {/* Phase Header */}
      <div
        onClick={onToggle}
        className="p-4 cursor-pointer hover:bg-opacity-80 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 flex-1">
            {/* Expand/Collapse Icon */}
            <div className="flex-shrink-0">
              {expanded ? (
                <ChevronDown className="w-5 h-5 text-gray-600" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-600" />
              )}
            </div>

            {/* Phase Icon */}
            <div className={`p-3 rounded-lg flex-shrink-0 ${
              phase.id === 'parsing' ? 'bg-blue-100 border border-blue-200' :
              phase.id === 'rag' ? 'bg-purple-100 border border-purple-200' :
              phase.id === 'llm_generation' ? 'bg-green-100 border border-green-200' :
              phase.id === 'saving' ? 'bg-indigo-100 border border-indigo-200' :
              'bg-gray-100 border border-gray-200'
            }`}>
              <PhaseIcon className={`w-6 h-6 ${
                phase.id === 'parsing' ? 'text-blue-600' :
                phase.id === 'rag' ? 'text-purple-600' :
                phase.id === 'llm_generation' ? 'text-green-600' :
                phase.id === 'saving' ? 'text-indigo-600' :
                'text-gray-600'
              }`} />
            </div>

            {/* Phase Title */}
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold text-gray-900">{phase.title}</h3>
              <p className="text-sm text-gray-600">{phase.description}</p>
              {lastUpdate && lastUpdate.message && (
                <p className="text-sm text-gray-500 mt-1 italic">{lastUpdate.message}</p>
              )}
            </div>

            {/* Status */}
            <div className="flex items-center space-x-2 flex-shrink-0">
              {getStatusIcon()}
              <span className="text-sm font-medium text-gray-700 capitalize">
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Phase Content (Expandable) */}
      {expanded && updates && updates.length > 0 && (
        <div className="px-4 pb-4 border-t border-gray-200">
          <div className="mt-4 space-y-3">
            {/* Render phase-specific content */}
            {phase.id === 'parsing' && (
              <ParserStep updates={updates} />
            )}

            {phase.id === 'rag' && (
              <RAGStep updates={updates} />
            )}

            {phase.id === 'llm_generation' && (
              <LLMGenerationStep updates={updates} />
            )}

            {phase.id === 'saving' && (
              <SavingStep updates={updates} />
            )}

            {phase.id === 'complete' && lastUpdate && lastUpdate.data && (
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="space-y-2">
                  <p className="text-sm font-bold text-green-900">
                    Generated {lastUpdate.data.total_policies} security policies
                  </p>
                  {lastUpdate.data.output_file && (
                    <div className="text-xs text-green-700 space-y-1 font-mono">
                      <p>TXT: {lastUpdate.data.output_file}</p>
                      <p>HTML: {lastUpdate.data.html_file}</p>
                      <p>JSON: {lastUpdate.data.json_file}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PhaseSection;
