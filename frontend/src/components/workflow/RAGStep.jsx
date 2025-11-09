import React from 'react';
import { Database, CheckCircle, Loader, Shield } from 'lucide-react';

const RAGStep = ({ updates }) => {
  const lastUpdate = updates[updates.length - 1];
  const isComplete = lastUpdate?.status === 'completed';

  // Extract NIST and ISO updates
  const nistUpdate = updates.find(u => u.data?.rag_status === 'nist_complete');
  const isoUpdate = updates.find(u => u.data?.rag_status === 'complete');

  return (
    <div className="space-y-3">
      {/* NIST CSF Retrieval */}
      {nistUpdate && (
        <div className="bg-white rounded-lg p-4 border-2 border-purple-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded bg-purple-100">
                <Database className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h4 className="font-bold text-gray-900">NIST Cybersecurity Framework</h4>
                <p className="text-xs text-gray-600">Compliance controls retrieved</p>
              </div>
            </div>
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>

          {nistUpdate.data?.controls && (
            <div className="mt-3 bg-purple-50 rounded p-3 border border-purple-200">
              <p className="text-xs font-medium text-purple-900 mb-2">
                Retrieved {nistUpdate.data.contexts_retrieved} controls:
              </p>
              <div className="flex flex-wrap gap-1">
                {nistUpdate.data.controls.map((control, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-mono rounded"
                  >
                    {control}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ISO 27001 Retrieval */}
      {isoUpdate && (
        <div className="bg-white rounded-lg p-4 border-2 border-indigo-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded bg-indigo-100">
                <Shield className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h4 className="font-bold text-gray-900">ISO 27001:2013</h4>
                <p className="text-xs text-gray-600">Information security controls</p>
              </div>
            </div>
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>

          {isoUpdate.data && (
            <div className="mt-3 bg-indigo-50 rounded p-3 border border-indigo-200">
              <p className="text-xs font-medium text-indigo-900">
                Retrieved {isoUpdate.data.iso_controls} controls from ISO 27001 standard
              </p>
            </div>
          )}
        </div>
      )}

      {/* Summary */}
      {isComplete && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border-2 border-purple-200">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-purple-600" />
            <div>
              <p className="font-bold text-purple-900">Compliance Context Retrieved</p>
              <p className="text-sm text-purple-700">
                {lastUpdate.data?.total_contexts || 0} compliance contexts from{' '}
                {lastUpdate.data?.standards?.join(' and ') || 'vector database'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* In Progress */}
      {!isComplete && lastUpdate && (
        <div className="bg-white rounded-lg p-4 border-2 border-blue-200">
          <div className="flex items-center space-x-3">
            <Loader className="w-6 h-6 text-blue-600 animate-spin" />
            <div>
              <p className="font-medium text-gray-900">{lastUpdate.message}</p>
              <p className="text-sm text-gray-600">
                Fetching compliance controls from {lastUpdate.data?.standard || 'vector database'}...
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RAGStep;
