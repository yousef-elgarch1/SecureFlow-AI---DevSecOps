import React from 'react';
import { Shield, CheckCircle, AlertTriangle, Award, TrendingUp } from 'lucide-react';

const ComplianceValidation = ({ analysis }) => {
  if (!analysis) return null;

  const { nist_csf, iso_27001, overall_score } = analysis;

  const getScoreColor = (score) => {
    if (score >= 90) return 'green';
    if (score >= 75) return 'blue';
    if (score >= 60) return 'yellow';
    if (score >= 40) return 'orange';
    return 'red';
  };

  const getScoreGrade = (score) => {
    if (score >= 90) return 'A - Excellent';
    if (score >= 75) return 'B - Good';
    if (score >= 60) return 'C - Satisfactory';
    if (score >= 40) return 'D - Needs Improvement';
    return 'F - Insufficient';
  };

  const scoreColor = getScoreColor(overall_score);
  const scoreGrade = getScoreGrade(overall_score);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`bg-gradient-to-r from-${scoreColor}-600 to-${scoreColor}-700 text-white rounded-lg p-6 shadow-lg`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white bg-opacity-20 rounded-lg">
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Compliance Coverage Analysis</h2>
              <p className={`text-${scoreColor}-100`}>
                Automated validation of NIST CSF and ISO 27001 control coverage
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{overall_score}%</div>
            <div className={`text-${scoreColor}-100 text-sm font-medium`}>{scoreGrade}</div>
          </div>
        </div>
      </div>

      {/* Overall Score Card */}
      <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
            <Award className="w-5 h-5 text-purple-600" />
            <span>Overall Compliance Score</span>
          </h3>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full h-8 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r from-${scoreColor}-500 to-${scoreColor}-600 transition-all duration-1000 flex items-center justify-center`}
            style={{ width: `${overall_score}%` }}
          >
            <span className="text-white font-bold text-sm">{overall_score}%</span>
          </div>
        </div>

        <p className="text-sm text-gray-600 mt-2">
          {overall_score >= 90 && "Excellent! Your policies provide comprehensive compliance coverage."}
          {overall_score >= 75 && overall_score < 90 && "Good coverage! Consider addressing the identified gaps to reach full compliance."}
          {overall_score >= 60 && overall_score < 75 && "Satisfactory coverage, but significant gaps remain. Review missing controls."}
          {overall_score >= 40 && overall_score < 60 && "Needs improvement. Many critical controls are not covered."}
          {overall_score < 40 && "Insufficient coverage. Immediate action required to address compliance gaps."}
        </p>
      </div>

      {/* NIST CSF Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-blue-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">NIST Cybersecurity Framework</h3>
            <p className="text-sm text-gray-600">
              {nist_csf.covered_controls} / {nist_csf.total_controls} controls covered
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">{nist_csf.coverage_percentage}%</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full h-6 bg-gray-200 rounded-full overflow-hidden mb-4">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-1000"
            style={{ width: `${nist_csf.coverage_percentage}%` }}
          />
        </div>

        {/* Coverage by Function */}
        <div className="space-y-3">
          <h4 className="text-sm font-bold text-gray-900">Coverage by Function:</h4>
          {nist_csf.by_function && Object.entries(nist_csf.by_function).map(([func, data]) => (
            <div key={func} className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {data.percentage >= 75 ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-yellow-600" />
                )}
                <span className="text-sm font-medium text-gray-700">{func}</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">
                  {data.covered}/{data.total}
                </span>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${data.percentage >= 75 ? 'bg-green-500' : data.percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${data.percentage}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">
                  {data.percentage}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Covered Controls */}
        {nist_csf.covered && nist_csf.covered.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-bold text-green-900 mb-2">✓ Covered Controls ({nist_csf.covered.length})</h4>
            <div className="flex flex-wrap gap-2">
              {nist_csf.covered.slice(0, 20).map((control) => (
                <span key={control} className="px-2 py-1 bg-green-100 text-green-800 text-xs font-mono rounded">
                  {control}
                </span>
              ))}
              {nist_csf.covered.length > 20 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{nist_csf.covered.length - 20} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Gaps */}
        {nist_csf.gaps && nist_csf.gaps.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-bold text-red-900 mb-2">✗ Gaps ({nist_csf.gaps.length})</h4>
            <div className="flex flex-wrap gap-2">
              {nist_csf.gaps.slice(0, 20).map((control) => (
                <span key={control} className="px-2 py-1 bg-red-100 text-red-800 text-xs font-mono rounded">
                  {control}
                </span>
              ))}
              {nist_csf.gaps.length > 20 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{nist_csf.gaps.length - 20} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ISO 27001 Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-purple-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">ISO 27001:2013 Annex A</h3>
            <p className="text-sm text-gray-600">
              {iso_27001.covered_controls} / {iso_27001.total_controls} controls covered
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-purple-600">{iso_27001.coverage_percentage}%</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative w-full h-6 bg-gray-200 rounded-full overflow-hidden mb-4">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-1000"
            style={{ width: `${iso_27001.coverage_percentage}%` }}
          />
        </div>

        {/* Coverage by Domain */}
        <div className="space-y-2">
          <h4 className="text-sm font-bold text-gray-900">Coverage by Domain:</h4>
          <div className="grid grid-cols-2 gap-3">
            {iso_27001.by_domain && Object.entries(iso_27001.by_domain).map(([domain, data]) => (
              <div key={domain} className="flex items-center justify-between bg-gray-50 rounded p-2">
                <div className="flex items-center space-x-2">
                  {data.percentage >= 75 ? (
                    <CheckCircle className="w-3 h-3 text-green-600" />
                  ) : (
                    <AlertTriangle className="w-3 h-3 text-yellow-600" />
                  )}
                  <span className="text-xs font-medium text-gray-700">{domain}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-600">
                    {data.covered}/{data.total}
                  </span>
                  <span className="text-xs font-medium text-gray-900">
                    {data.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Covered Controls */}
        {iso_27001.covered && iso_27001.covered.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-bold text-green-900 mb-2">✓ Covered Controls ({iso_27001.covered.length})</h4>
            <div className="flex flex-wrap gap-2">
              {iso_27001.covered.slice(0, 20).map((control) => (
                <span key={control} className="px-2 py-1 bg-green-100 text-green-800 text-xs font-mono rounded">
                  {control}
                </span>
              ))}
              {iso_27001.covered.length > 20 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{iso_27001.covered.length - 20} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Gaps */}
        {iso_27001.gaps && iso_27001.gaps.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-bold text-red-900 mb-2">✗ Gaps ({iso_27001.gaps.length})</h4>
            <div className="flex flex-wrap gap-2">
              {iso_27001.gaps.slice(0, 20).map((control) => (
                <span key={control} className="px-2 py-1 bg-red-100 text-red-800 text-xs font-mono rounded">
                  {control}
                </span>
              ))}
              {iso_27001.gaps.length > 20 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{iso_27001.gaps.length - 20} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-yellow-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-yellow-600" />
          <span>Recommendations</span>
        </h3>
        <ul className="space-y-2">
          {overall_score < 90 && (
            <li className="flex items-start space-x-2">
              <span className="text-yellow-600 font-bold">•</span>
              <span className="text-sm text-gray-700">
                Address identified gaps in NIST CSF functions: {nist_csf.by_function && Object.entries(nist_csf.by_function)
                  .filter(([_, data]) => data.percentage < 50)
                  .map(([func]) => func)
                  .join(', ')}
              </span>
            </li>
          )}
          {iso_27001.coverage_percentage < 80 && (
            <li className="flex items-start space-x-2">
              <span className="text-yellow-600 font-bold">•</span>
              <span className="text-sm text-gray-700">
                Improve ISO 27001 coverage in domains: {iso_27001.by_domain && Object.entries(iso_27001.by_domain)
                  .filter(([_, data]) => data.percentage < 50)
                  .map(([domain]) => domain)
                  .join(', ')}
              </span>
            </li>
          )}
          <li className="flex items-start space-x-2">
            <span className="text-yellow-600 font-bold">•</span>
            <span className="text-sm text-gray-700">
              Review all policies to ensure compliance controls are properly documented
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-yellow-600 font-bold">•</span>
            <span className="text-sm text-gray-700">
              Consider generating additional policies to cover missing controls
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ComplianceValidation;
