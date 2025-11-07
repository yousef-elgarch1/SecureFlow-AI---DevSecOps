import React, { useState, useEffect } from 'react';
import {
  Activity,
  ChevronRight,
  CheckCircle,
  Clock,
  Loader,
  AlertCircle,
  FileText,
  Database,
  Cpu,
  Save,
  Shield,
  ArrowRight,
  Zap,
  GitBranch
} from 'lucide-react';

const WorkflowView = ({ progress, inputMode = 'upload' }) => {
  const [selectedStep, setSelectedStep] = useState(null);
  const [currentPhase, setCurrentPhase] = useState(null);

  useEffect(() => {
    if (progress && progress.length > 0) {
      const lastUpdate = progress[progress.length - 1];
      setCurrentPhase(lastUpdate.phase);

      // Auto-select current phase if nothing selected
      if (!selectedStep || selectedStep === lastUpdate.phase) {
        setSelectedStep(lastUpdate.phase);
      }
    }
  }, [progress]);

  // Workflow steps definition with enhanced colors
  const baseSteps = [
    {
      id: 'parsing',
      title: 'Parse Reports',
      description: 'Extract vulnerabilities',
      icon: FileText,
      color: 'cyan',
      gradient: 'from-cyan-500 to-blue-500',
    },
    {
      id: 'rag',
      title: 'RAG Retrieval',
      description: 'Fetch compliance context',
      icon: Database,
      color: 'purple',
      gradient: 'from-purple-500 to-violet-500',
    },
    {
      id: 'llm_generation',
      title: 'AI Generation',
      description: 'Generate policies',
      icon: Cpu,
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-500',
    },
    {
      id: 'saving',
      title: 'Save Results',
      description: 'Save policy files',
      icon: Save,
      color: 'indigo',
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      id: 'compliance_validation',
      title: 'Compliance Check',
      description: 'Validate coverage',
      icon: Shield,
      color: 'amber',
      gradient: 'from-amber-500 to-orange-500',
    },
  ];

  // Add GitHub cloning step if in GitHub mode
  const workflowSteps = inputMode === 'github'
    ? [
        {
          id: 'github_clone',
          title: 'Clone Repository',
          description: 'Clone GitHub repo',
          icon: GitBranch,
          color: 'violet',
          gradient: 'from-violet-500 to-purple-500',
        },
        ...baseSteps
      ]
    : baseSteps;

  // Add step numbers
  workflowSteps.forEach((step, index) => {
    step.number = index + 1;
  });

  // Get status for a step
  const getStepStatus = (stepId) => {
    if (!progress || progress.length === 0) return 'pending';

    const stepUpdates = progress.filter(p => p.phase === stepId);
    if (stepUpdates.length === 0) return 'pending';

    const lastUpdate = stepUpdates[stepUpdates.length - 1];

    // Check if this step is current
    if (currentPhase === stepId && lastUpdate.status === 'in_progress') {
      return 'running';
    }

    return lastUpdate.status || 'pending';
  };

  // Get step updates
  const getStepUpdates = (stepId) => {
    return progress ? progress.filter(p => p.phase === stepId) : [];
  };

  // Status icon component
  const StatusIcon = ({ status, color }) => {
    switch (status) {
      case 'running':
        return <Loader className={`w-6 h-6 text-${color}-400 animate-spin`} />;
      case 'completed':
        return <CheckCircle className={`w-6 h-6 text-${color}-400`} />;
      case 'error':
        return <AlertCircle className="w-6 h-6 text-rose-400" />;
      case 'in_progress':
        return <Loader className={`w-6 h-6 text-${color}-400 animate-spin`} />;
      default:
        return <Clock className="w-6 h-6 text-gray-600" />;
    }
  };

  // Render workflow graph
  const renderWorkflowGraph = () => {
    return (
      <div className="bg-gradient-to-br from-slate-800/50 via-gray-800/50 to-slate-800/50 rounded-3xl border border-cyan-500/20 p-10 backdrop-blur-sm shadow-2xl">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          {workflowSteps.map((step, index) => {
            const status = getStepStatus(step.id);
            const Icon = step.icon;
            const isSelected = selectedStep === step.id;
            const isCurrent = currentPhase === step.id;

            // Enhanced status styling
            const borderColor =
              status === 'completed' ? `border-${step.color}-400/70` :
              status === 'running' || status === 'in_progress' ? `border-${step.color}-400 animate-pulse` :
              status === 'error' ? 'border-rose-500/70' :
              'border-slate-700/50';

            const bgColor =
              status === 'completed' ? `bg-${step.color}-500/10` :
              status === 'running' || status === 'in_progress' ? `bg-${step.color}-500/20` :
              status === 'error' ? 'bg-rose-500/10' :
              'bg-slate-900/40';

            const shadowColor =
              (status === 'running' || status === 'in_progress') ? `shadow-${step.color}-500/30` :
              status === 'completed' ? `shadow-${step.color}-500/20` :
              'shadow-none';

            const ringClass = isCurrent ? `ring-4 ring-${step.color}-400/30` : '';

            return (
              <React.Fragment key={step.id}>
                {/* Step Box */}
                <div
                  onClick={() => setSelectedStep(step.id)}
                  className={`
                    relative cursor-pointer transition-all duration-300 transform
                    ${isSelected ? 'scale-110 z-10' : 'hover:scale-105'}
                  `}
                >
                  <div className={`
                    border-2 rounded-2xl p-5 w-44 ${borderColor} ${bgColor} ${ringClass}
                    ${isSelected ? `shadow-2xl ${shadowColor}` : `shadow-xl hover:shadow-2xl ${shadowColor}`}
                    backdrop-blur-sm
                  `}>
                    {/* Step Number Badge */}
                    <div className={`absolute -top-3 -left-3 w-9 h-9 rounded-xl bg-gradient-to-br ${step.gradient} border-2 border-slate-800 flex items-center justify-center font-bold text-sm text-white shadow-lg`}>
                      {step.number}
                    </div>

                    {/* Icon */}
                    <div className="flex justify-center mb-3">
                      <div className={`p-4 rounded-2xl bg-gradient-to-br ${step.gradient} shadow-lg shadow-${step.color}-500/30`}>
                        <Icon className="w-7 h-7 text-white" />
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className={`text-center font-bold text-sm text-gray-100 mb-1 tracking-wide`}>
                      {step.title}
                    </h3>

                    {/* Description */}
                    <p className="text-center text-xs text-gray-400">
                      {step.description}
                    </p>

                    {/* Status Icon */}
                    <div className="flex justify-center mt-4">
                      <StatusIcon status={status} color={step.color} />
                    </div>

                    {/* Status Text */}
                    <p className={`text-center text-xs font-bold mt-2 uppercase tracking-wider ${
                      status === 'completed' ? `text-${step.color}-300` :
                      status === 'running' || status === 'in_progress' ? `text-${step.color}-300 animate-pulse` :
                      status === 'error' ? 'text-rose-400' :
                      'text-gray-600'
                    }`}>
                      {status === 'pending' ? 'Waiting' :
                       status === 'running' || status === 'in_progress' ? 'Running' :
                       status === 'completed' ? 'Done' :
                       status === 'error' ? 'Failed' : 'Pending'}
                    </p>
                  </div>
                </div>

                {/* Connector Arrow */}
                {index < workflowSteps.length - 1 && (
                  <div className="flex items-center">
                    <ArrowRight className={`w-10 h-10 transition-colors ${
                      status === 'completed' ? `text-${step.color}-400` : 'text-slate-700'
                    }`} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    );
  };

  // Render step details
  const renderStepDetails = () => {
    if (!selectedStep) return null;

    const updates = getStepUpdates(selectedStep);
    const step = workflowSteps.find(s => s.id === selectedStep);

    if (!step) return null;

    const status = getStepStatus(step.id);

    return (
      <div className="bg-gradient-to-br from-slate-800/50 via-gray-800/50 to-slate-800/50 rounded-3xl border border-cyan-500/20 p-8 mt-8 backdrop-blur-sm shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-2xl bg-gradient-to-br ${step.gradient} shadow-lg shadow-${step.color}-500/30`}>
              <step.icon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-100">
                Step {step.number}: {step.title}
              </h3>
              <p className="text-sm text-gray-400 mt-1">{step.description}</p>
            </div>
          </div>
          <StatusIcon status={status} color={step.color} />
        </div>

        {/* Real-time logs */}
        <div className="bg-slate-950/80 rounded-2xl p-6 max-h-96 overflow-y-auto border border-cyan-500/10 shadow-inner">
          <div className="font-mono text-sm space-y-3">
            {updates.length === 0 ? (
              <p className="text-gray-600 flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>Waiting to start...</span>
              </p>
            ) : (
              updates.map((update, idx) => (
                <div key={idx} className="text-gray-300 border-l-2 border-cyan-500/30 pl-4 py-2">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-gray-600 text-xs">[{new Date().toLocaleTimeString()}]</span>
                    <span className={`
                      text-xs font-bold px-2 py-0.5 rounded uppercase
                      ${update.status === 'completed' ? 'bg-emerald-500/20 text-emerald-300' :
                        update.status === 'in_progress' ? 'bg-cyan-500/20 text-cyan-300' :
                        update.status === 'error' ? 'bg-rose-500/20 text-rose-300' :
                        'bg-gray-500/20 text-gray-400'}
                    `}>
                      {update.status}
                    </span>
                  </div>
                  <p className="text-gray-200">{update.message}</p>

                  {/* Show detailed data */}
                  {update.data && Object.keys(update.data).length > 0 && (
                    <div className="ml-2 mt-2 space-y-1 text-xs">
                      {update.data.current_parser && (
                        <div className="text-amber-400 flex items-center space-x-2">
                          <Zap className="w-3 h-3" />
                          <span>Parser: {update.data.current_parser}</span>
                          {update.data.vulnerabilities_found !== undefined &&
                            <span className="text-amber-300">({update.data.vulnerabilities_found} vulns)</span>
                          }
                        </div>
                      )}
                      {update.data.current_vuln && (
                        <div className="text-cyan-400">
                          → Processing: {update.data.current_vuln.title} <span className="text-gray-500">[{update.data.current_vuln.severity}]</span>
                        </div>
                      )}
                      {update.data.llm_model && (
                        <div className="text-purple-400">
                          → Model: {update.data.llm_model}
                        </div>
                      )}
                      {update.data.progress_percentage !== undefined && (
                        <div className="text-blue-400 flex items-center space-x-2">
                          <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full transition-all duration-300"
                              style={{ width: `${update.data.progress_percentage}%` }}
                            />
                          </div>
                          <span className="text-xs">{update.data.progress_percentage}%</span>
                        </div>
                      )}
                      {update.data.total_contexts && (
                        <div className="text-emerald-400">
                          → Retrieved: {update.data.total_contexts} compliance contexts
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Summary Stats */}
        {updates.length > 0 && updates[updates.length - 1].data && (
          <div className="mt-6 grid grid-cols-3 gap-4">
            {updates[updates.length - 1].data.sast_count !== undefined && (
              <div className="bg-cyan-500/10 rounded-2xl p-4 border border-cyan-400/30 backdrop-blur-sm">
                <p className="text-xs text-cyan-400 font-bold uppercase tracking-wider">SAST</p>
                <p className="text-3xl font-bold text-cyan-300 mt-1">
                  {updates[updates.length - 1].data.sast_count}
                </p>
              </div>
            )}
            {updates[updates.length - 1].data.sca_count !== undefined && (
              <div className="bg-emerald-500/10 rounded-2xl p-4 border border-emerald-400/30 backdrop-blur-sm">
                <p className="text-xs text-emerald-400 font-bold uppercase tracking-wider">SCA</p>
                <p className="text-3xl font-bold text-emerald-300 mt-1">
                  {updates[updates.length - 1].data.sca_count}
                </p>
              </div>
            )}
            {updates[updates.length - 1].data.dast_count !== undefined && (
              <div className="bg-purple-500/10 rounded-2xl p-4 border border-purple-400/30 backdrop-blur-sm">
                <p className="text-xs text-purple-400 font-bold uppercase tracking-wider">DAST</p>
                <p className="text-3xl font-bold text-purple-300 mt-1">
                  {updates[updates.length - 1].data.dast_count}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white rounded-3xl p-8 shadow-2xl shadow-cyan-500/30 border border-cyan-400/30">
        <div className="flex items-center space-x-5">
          <div className="p-4 bg-white/20 backdrop-blur-sm rounded-2xl shadow-lg">
            <Activity className="w-10 h-10 animate-pulse" />
          </div>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">AI Security Policy Generation Pipeline</h2>
            <p className="text-cyan-100 mt-2 text-sm tracking-wide">Real-time workflow visualization • Click any step to see detailed logs</p>
          </div>
        </div>
      </div>

      {/* Workflow Graph */}
      {renderWorkflowGraph()}

      {/* Step Details */}
      {renderStepDetails()}

      {/* Debug Info */}
      {progress && progress.length > 0 && (
        <div className="text-xs text-gray-600 text-center bg-slate-900/30 rounded-xl py-2 border border-slate-800">
          Updates received: {progress.length} | Current phase: {currentPhase || 'None'}
        </div>
      )}
    </div>
  );
};

export default WorkflowView;
