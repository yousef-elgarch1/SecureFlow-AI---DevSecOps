import React, { useState } from 'react';
import { Shield, CheckCircle, XCircle, Filter, Download, ChevronDown, ChevronRight } from 'lucide-react';

const ComplianceChecklist = ({ analysis, policies }) => {
  const [filter, setFilter] = useState('all'); // 'all', 'covered', 'uncovered'
  const [expandedCategories, setExpandedCategories] = useState(new Set(['ID', 'PR'])); // Expand Identify and Protect by default
  const [selectedControl, setSelectedControl] = useState(null);

  if (!analysis) return null;

  const { nist_csf, iso_27001 } = analysis;

  // NIST CSF Control Definitions
  const nistDefinitions = {
    // Identify (ID)
    'ID.AM-1': 'Physical devices and systems inventoried',
    'ID.AM-2': 'Software platforms and applications inventoried',
    'ID.RA-1': 'Asset vulnerabilities are identified and documented',
    'ID.RA-5': 'Threats, vulnerabilities, likelihoods, and impacts are used to determine risk',
    'PR.AC-1': 'Identities and credentials are issued, managed, verified, revoked',
    'PR.AC-4': 'Access permissions and authorizations are managed',
    'PR.DS-5': 'Protections against data leaks are implemented',
    'DE.CM-1': 'The network is monitored to detect potential cybersecurity events',
    'DE.CM-7': 'Monitoring for unauthorized personnel, connections, devices, and software',
    // Add more as needed
  };

  // ISO 27001 Control Definitions
  const isoDefinitions = {
    'A.9.1.1': 'Access control policy',
    'A.9.4.1': 'Information access restriction',
    'A.12.6.1': 'Management of technical vulnerabilities',
    'A.14.1.2': 'Securing application services on public networks',
    'A.14.2.1': 'Secure development policy',
    'A.14.2.5': 'Secure system engineering principles',
    // Add more as needed
  };

  // Get policies that address a specific control
  const getPoliciesForControl = (control) => {
    if (!policies) return [];

    return policies.filter(policy => {
      if (!policy.compliance_mapping) return false;

      const nistControls = policy.compliance_mapping['NIST CSF'] || [];
      const isoControls = policy.compliance_mapping['ISO 27001'] || [];

      return nistControls.includes(control) || isoControls.includes(control);
    });
  };

  // Toggle category expansion
  const toggleCategory = (category) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  // NIST CSF Categories
  const nistCategories = {
    'ID': { name: 'Identify', color: 'blue' },
    'PR': { name: 'Protect', color: 'green' },
    'DE': { name: 'Detect', color: 'yellow' },
    'RS': { name: 'Respond', color: 'orange' },
    'RC': { name: 'Recover', color: 'purple' }
  };

  // Group NIST controls by function
  const groupNistByFunction = () => {
    const grouped = {};

    [...nist_csf.covered, ...nist_csf.gaps].forEach(control => {
      const func = control.split('.')[0]; // e.g., 'ID' from 'ID.AM-1'
      if (!grouped[func]) {
        grouped[func] = { covered: [], gaps: [] };
      }

      if (nist_csf.covered.includes(control)) {
        grouped[func].covered.push(control);
      } else {
        grouped[func].gaps.push(control);
      }
    });

    return grouped;
  };

  // Group ISO controls by domain
  const groupIsoByDomain = () => {
    const grouped = {};

    [...iso_27001.covered, ...iso_27001.gaps].forEach(control => {
      const domain = control.split('.')[0] + '.' + control.split('.')[1]; // e.g., 'A.9' from 'A.9.1.1'
      if (!grouped[domain]) {
        grouped[domain] = { covered: [], gaps: [] };
      }

      if (iso_27001.covered.includes(control)) {
        grouped[domain].covered.push(control);
      } else {
        grouped[domain].gaps.push(control);
      }
    });

    return grouped;
  };

  const nistGrouped = groupNistByFunction();
  const isoGrouped = groupIsoByDomain();

  // Filter controls
  const shouldShowControl = (isCovered) => {
    if (filter === 'all') return true;
    if (filter === 'covered') return isCovered;
    if (filter === 'uncovered') return !isCovered;
    return true;
  };

  // Render control item
  const renderControl = (control, isCovered, standard) => {
    if (!shouldShowControl(isCovered)) return null;

    const relatedPolicies = getPoliciesForControl(control);
    const definition = standard === 'nist' ? nistDefinitions[control] : isoDefinitions[control];

    return (
      <div
        key={control}
        className={`flex items-center justify-between p-2 rounded hover:bg-gray-50 cursor-pointer ${
          selectedControl === control ? 'bg-blue-50 border-l-4 border-blue-500' : ''
        }`}
        onClick={() => setSelectedControl(selectedControl === control ? null : control)}
      >
        <div className="flex items-center space-x-2 flex-1">
          {isCovered ? (
            <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
          )}
          <div className="flex-1">
            <span className="text-sm font-mono font-medium text-gray-900">{control}</span>
            {definition && (
              <p className="text-xs text-gray-600 mt-1">{definition}</p>
            )}
            {selectedControl === control && relatedPolicies.length > 0 && (
              <div className="mt-2 pl-4 border-l-2 border-gray-300">
                <p className="text-xs font-medium text-gray-700 mb-1">
                  Addressed by {relatedPolicies.length} {relatedPolicies.length === 1 ? 'policy' : 'policies'}:
                </p>
                {relatedPolicies.map((policy, idx) => (
                  <div key={idx} className="text-xs text-gray-600 mb-1">
                    • {policy.vulnerability.title} [{policy.vulnerability.severity}]
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        {isCovered && relatedPolicies.length > 0 && (
          <span className="text-xs font-medium text-gray-500 ml-2">
            {relatedPolicies.length} {relatedPolicies.length === 1 ? 'policy' : 'policies'}
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white bg-opacity-20 rounded-lg">
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Compliance Control Checklist</h2>
              <p className="text-indigo-100">
                Interactive checklist of all NIST CSF and ISO 27001 controls
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <div className="flex space-x-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  filter === 'all'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All Controls
              </button>
              <button
                onClick={() => setFilter('covered')}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  filter === 'covered'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Covered ({nist_csf.covered.length + iso_27001.covered.length})
              </button>
              <button
                onClick={() => setFilter('uncovered')}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                  filter === 'uncovered'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Gaps ({nist_csf.gaps.length + iso_27001.gaps.length})
              </button>
            </div>
          </div>
          <button
            onClick={() => alert('Export functionality coming soon!')}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* NIST CSF Checklist */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-bold text-gray-900">NIST Cybersecurity Framework</h3>
          <p className="text-sm text-gray-600 mt-1">
            {nist_csf.covered.length}/{nist_csf.total_controls} controls covered ({nist_csf.coverage_percentage}%)
          </p>
        </div>

        <div className="p-6 space-y-4">
          {Object.entries(nistGrouped).map(([func, controls]) => {
            const category = nistCategories[func];
            const isExpanded = expandedCategories.has(func);
            const totalControls = controls.covered.length + controls.gaps.length;
            const coveredCount = controls.covered.length;
            const coveragePercent = (coveredCount / totalControls) * 100;

            return (
              <div key={func} className="border border-gray-200 rounded-lg">
                <div
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => toggleCategory(func)}
                >
                  <div className="flex items-center space-x-3 flex-1">
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-gray-600" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-600" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-gray-900">{func}</span>
                        <span className="text-sm text-gray-600">- {category?.name}</span>
                      </div>
                      <div className="mt-1 flex items-center space-x-2">
                        <div className="flex-1 max-w-xs h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              coveragePercent >= 75 ? 'bg-green-500' :
                              coveragePercent >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${coveragePercent}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          {coveredCount}/{totalControls} ({coveragePercent.toFixed(0)}%)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="p-4 pt-0 space-y-1">
                    {controls.covered.map(control => renderControl(control, true, 'nist'))}
                    {controls.gaps.map(control => renderControl(control, false, 'nist'))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ISO 27001 Checklist */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-bold text-gray-900">ISO 27001:2013 Annex A</h3>
          <p className="text-sm text-gray-600 mt-1">
            {iso_27001.covered.length}/{iso_27001.total_controls} controls covered ({iso_27001.coverage_percentage}%)
          </p>
        </div>

        <div className="p-6 space-y-4">
          {Object.entries(isoGrouped).map(([domain, controls]) => {
            const isExpanded = expandedCategories.has(domain);
            const totalControls = controls.covered.length + controls.gaps.length;
            const coveredCount = controls.covered.length;
            const coveragePercent = (coveredCount / totalControls) * 100;

            return (
              <div key={domain} className="border border-gray-200 rounded-lg">
                <div
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => toggleCategory(domain)}
                >
                  <div className="flex items-center space-x-3 flex-1">
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-gray-600" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-gray-600" />
                    )}
                    <div className="flex-1">
                      <span className="font-bold text-gray-900">{domain}</span>
                      <div className="mt-1 flex items-center space-x-2">
                        <div className="flex-1 max-w-xs h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              coveragePercent >= 75 ? 'bg-green-500' :
                              coveragePercent >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${coveragePercent}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          {coveredCount}/{totalControls} ({coveragePercent.toFixed(0)}%)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="p-4 pt-0 space-y-1">
                    {controls.covered.map(control => renderControl(control, true, 'iso'))}
                    {controls.gaps.map(control => renderControl(control, false, 'iso'))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h4 className="text-sm font-bold text-gray-900 mb-2">Legend:</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-gray-700">Control is covered by generated policies</span>
          </div>
          <div className="flex items-center space-x-2">
            <XCircle className="w-4 h-4 text-red-600" />
            <span className="text-gray-700">Control is not covered (gap)</span>
          </div>
        </div>
        <p className="text-xs text-gray-600 mt-2">
          Click on any control to see which policies address it
        </p>
      </div>
    </div>
  );
};

export default ComplianceChecklist;
