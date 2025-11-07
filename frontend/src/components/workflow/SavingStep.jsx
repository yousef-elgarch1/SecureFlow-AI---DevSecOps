import React from 'react';
import { Save, CheckCircle, FileText, Code, File } from 'lucide-react';

const SavingStep = ({ updates }) => {
  const lastUpdate = updates[updates.length - 1];
  const isComplete = lastUpdate?.status === 'completed';

  return (
    <div className="space-y-3">
      {isComplete && lastUpdate.data?.files_saved ? (
        <>
          {/* Files Saved */}
          <div className="bg-white rounded-lg p-4 border-2 border-indigo-200">
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded bg-indigo-100">
                <Save className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h4 className="font-bold text-gray-900">Files Saved Successfully</h4>
                <p className="text-xs text-gray-600">
                  {lastUpdate.data.files_saved.length} file(s) in {lastUpdate.data.output_directory}/
                </p>
              </div>
            </div>

            <div className="space-y-2">
              {lastUpdate.data.files_saved.map((file, idx) => {
                const ext = file.split('.').pop();
                const Icon = ext === 'txt' ? FileText : ext === 'json' ? Code : File;
                const colorClass = ext === 'txt' ? 'text-blue-600' :
                                  ext === 'html' ? 'text-orange-600' :
                                  'text-green-600';

                return (
                  <div
                    key={idx}
                    className="flex items-center space-x-3 bg-gray-50 rounded p-2 border border-gray-200"
                  >
                    <Icon className={`w-4 h-4 ${colorClass}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-mono text-gray-900 truncate">{file}</p>
                    </div>
                    <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Success Summary */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border-2 border-indigo-200">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-6 h-6 text-indigo-600" />
              <div>
                <p className="font-bold text-indigo-900">Results Saved</p>
                <p className="text-sm text-indigo-700">
                  All policy documents have been saved to the outputs directory
                </p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg p-4 border-2 border-blue-200">
          <div className="flex items-center space-x-3">
            <div className="animate-spin">
              <Save className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">{lastUpdate?.message || 'Saving files...'}</p>
              <p className="text-sm text-gray-600">
                Generating TXT, HTML, and JSON reports...
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavingStep;
