import React from 'react';
import { FileText, Package, Globe, CheckCircle, Loader } from 'lucide-react';

const ParserStep = ({ updates }) => {
  // Extract parser-specific updates
  const sastUpdates = updates.filter(u => u.data?.current_parser === 'SAST');
  const scaUpdates = updates.filter(u => u.data?.current_parser === 'SCA');
  const dastUpdates = updates.filter(u => u.data?.current_parser === 'DAST');

  const renderParserSection = (parserName, parserUpdates, Icon, colorClass) => {
    if (parserUpdates.length === 0) return null;

    const lastUpdate = parserUpdates[parserUpdates.length - 1];
    const isComplete = lastUpdate.data?.parser_status === 'completed';
    const vulnCount = lastUpdate.data?.vulnerabilities_found || 0;
    const vulnerabilities = lastUpdate.data?.vulnerabilities || [];

    return (
      <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded ${colorClass} bg-opacity-20`}>
              <Icon className={`w-5 h-5 ${colorClass}`} />
            </div>
            <div>
              <h4 className="font-bold text-gray-900">{parserName} Parser</h4>
              <p className="text-xs text-gray-600">
                {lastUpdate.data?.file_name || 'Scanning...'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {isComplete ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <Loader className="w-5 h-5 text-blue-600 animate-spin" />
            )}
            <span className={`text-sm font-bold ${
              isComplete ? 'text-green-700' : 'text-blue-700'
            }`}>
              {isComplete ? `${vulnCount} found` : 'Scanning...'}
            </span>
          </div>
        </div>

        {/* Vulnerability Preview */}
        {isComplete && vulnerabilities.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-medium text-gray-700">Sample Vulnerabilities:</p>
            <div className="space-y-1">
              {vulnerabilities.slice(0, 3).map((vuln, idx) => (
                <div key={idx} className="text-xs bg-gray-50 rounded p-2 border border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900 truncate flex-1">
                      {vuln.title}
                    </span>
                    <span className={`ml-2 px-2 py-0.5 rounded text-xs font-bold flex-shrink-0 ${
                      vuln.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      vuln.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      vuln.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {vuln.severity}
                    </span>
                  </div>
                  {vuln.file && (
                    <p className="text-gray-600 mt-1 font-mono truncate">{vuln.file}</p>
                  )}
                  {vuln.package && (
                    <p className="text-gray-600 mt-1 font-mono truncate">Package: {vuln.package}</p>
                  )}
                  {vuln.url && (
                    <p className="text-gray-600 mt-1 font-mono truncate">{vuln.url}</p>
                  )}
                </div>
              ))}
              {vulnerabilities.length > 3 && (
                <p className="text-xs text-gray-500 italic mt-1">
                  ... and {vulnerabilities.length - 3} more
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-3">
      {renderParserSection('SAST', sastUpdates, FileText, 'text-blue-600')}
      {renderParserSection('SCA', scaUpdates, Package, 'text-green-600')}
      {renderParserSection('DAST', dastUpdates, Globe, 'text-purple-600')}

      {/* Summary */}
      {updates.length > 0 && updates[updates.length - 1].status === 'completed' && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border-2 border-green-200">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-bold text-green-900">Parsing Complete</p>
              <p className="text-sm text-green-700">
                Total: {updates[updates.length - 1].data?.total || 0} vulnerabilities found
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParserStep;
