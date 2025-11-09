import React, { useState } from 'react';
import { Cpu, CheckCircle, Loader, ChevronDown, ChevronRight, Sparkles } from 'lucide-react';

const LLMGenerationStep = ({ updates }) => {
  const [showAll, setShowAll] = useState(false);

  const lastUpdate = updates[updates.length - 1];
  const isComplete = lastUpdate?.status === 'completed';

  // Filter to get only vulnerability-specific updates (those with current_vuln)
  const vulnUpdates = updates.filter(u => u.data?.current_vuln);

  // Get unique vulnerabilities (completed ones)
  const completedVulns = [];
  const seenTitles = new Set();

  vulnUpdates.forEach(update => {
    if (update.data?.llm_status === 'completed' && update.data?.current_vuln) {
      const title = update.data.current_vuln.title;
      if (!seenTitles.has(title)) {
        seenTitles.add(title);
        completedVulns.push(update);
      }
    }
  });

  // Get current processing vulnerability
  const currentVuln = vulnUpdates.length > 0 ? vulnUpdates[vulnUpdates.length - 1] : null;
  const isGenerating = currentVuln?.data?.llm_status === 'generating';

  // Display limit
  const displayLimit = showAll ? completedVulns.length : 5;
  const displayedVulns = completedVulns.slice(0, displayLimit);

  return (
    <div className="space-y-3">
      {/* LLM Routing Info */}
      {updates[0]?.data?.llm_routing && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border-2 border-green-200">
          <div className="flex items-center space-x-3 mb-3">
            <Sparkles className="w-5 h-5 text-green-600" />
            <h4 className="font-bold text-green-900">AI Model Routing</h4>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            {Object.entries(updates[0].data.llm_routing).map(([type, model]) => (
              <div key={type} className="bg-white rounded p-2 border border-green-200">
                <p className="font-bold text-gray-900">{type}</p>
                <p className="text-gray-600">{model}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current Processing */}
      {isGenerating && currentVuln && (
        <div className="bg-white rounded-lg p-4 border-2 border-blue-500 shadow-md animate-pulse-slow">
          <div className="flex items-center space-x-3 mb-3">
            <Loader className="w-5 h-5 text-blue-600 animate-spin" />
            <div className="flex-1">
              <p className="text-sm font-bold text-gray-900">
                [{currentVuln.data.processed + 1}/{currentVuln.data.total}] {currentVuln.data.current_vuln.title}
              </p>
              <p className="text-xs text-gray-600">
                Model: {currentVuln.data.llm_model} • Type: {currentVuln.data.current_vuln.type}
              </p>
            </div>
            <span className={`px-3 py-1 rounded text-xs font-bold ${
              currentVuln.data.current_vuln.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
              currentVuln.data.current_vuln.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
              currentVuln.data.current_vuln.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {currentVuln.data.current_vuln.severity}
            </span>
          </div>

          {/* Progress Bar */}
          {currentVuln.data.progress_percentage !== undefined && (
            <div className="mt-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Overall Progress</span>
                <span className="text-xs font-bold text-blue-600">
                  {currentVuln.data.progress_percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-300 ease-out"
                  style={{ width: `${currentVuln.data.progress_percentage}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Completed Vulnerabilities */}
      {completedVulns.length > 0 && (
        <div className="bg-white rounded-lg border-2 border-gray-200">
          <div className="p-3 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <h4 className="font-bold text-gray-900 text-sm">
                Generated Policies ({completedVulns.length})
              </h4>
            </div>
            {completedVulns.length > 5 && (
              <button
                onClick={() => setShowAll(!showAll)}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-1"
              >
                {showAll ? (
                  <>
                    <ChevronRight className="w-3 h-3" />
                    <span>Show Less</span>
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3" />
                    <span>Show All</span>
                  </>
                )}
              </button>
            )}
          </div>

          <div className="divide-y divide-gray-200">
            {displayedVulns.map((vuln, idx) => (
              <div key={idx} className="p-3 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1 min-w-0">
                    <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {vuln.data.current_vuln.title}
                      </p>
                      <p className="text-xs text-gray-600 mt-0.5">
                        {vuln.data.llm_model} • {vuln.data.current_vuln.type}
                      </p>
                      {vuln.data.compliance_mapped && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {vuln.data.compliance_mapped.map((control, i) => (
                            <span
                              key={i}
                              className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded font-mono"
                            >
                              {control}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <span className={`ml-2 px-2 py-0.5 rounded text-xs font-bold flex-shrink-0 ${
                    vuln.data.current_vuln.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                    vuln.data.current_vuln.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                    vuln.data.current_vuln.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {vuln.data.current_vuln.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {!showAll && completedVulns.length > displayLimit && (
            <div className="p-2 bg-gray-50 text-center text-xs text-gray-500">
              ... and {completedVulns.length - displayLimit} more policies
            </div>
          )}
        </div>
      )}

      {/* Summary */}
      {isComplete && lastUpdate.data && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border-2 border-green-200">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-bold text-green-900">Policy Generation Complete</p>
              <p className="text-sm text-green-700">
                {lastUpdate.data.total_generated} policies generated using{' '}
                {lastUpdate.data.llm_usage?.llama_70b || 0} LLaMA 70B +{' '}
                {lastUpdate.data.llm_usage?.llama_8b || 0} LLaMA 8B calls
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMGenerationStep;
