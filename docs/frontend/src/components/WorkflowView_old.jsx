import React, { useState, useEffect, useRef } from 'react';
import { Activity, ChevronDown, ChevronUp } from 'lucide-react';
import PhaseSection from './workflow/PhaseSection';

const WorkflowView = ({ progress }) => {
  const [expandedPhases, setExpandedPhases] = useState(new Set(['parsing']));
  const [expandAll, setExpandAll] = useState(false);
  const bottomRef = useRef(null);

  // Auto-scroll to active phase
  useEffect(() => {
    if (progress.length > 0) {
      const lastUpdate = progress[progress.length - 1];
      if (lastUpdate.status === 'in_progress') {
        // Auto-expand current phase
        setExpandedPhases(prev => new Set([...prev, lastUpdate.phase]));
      }
    }
  }, [progress]);

  const togglePhase = (phaseId) => {
    setExpandedPhases(prev => {
      const newSet = new Set(prev);
      if (newSet.has(phaseId)) {
        newSet.delete(phaseId);
      } else {
        newSet.add(phaseId);
      }
      return newSet;
    });
  };

  const toggleExpandAll = () => {
    if (expandAll) {
      setExpandedPhases(new Set());
    } else {
      setExpandedPhases(new Set(['parsing', 'rag', 'llm_generation', 'saving', 'complete']));
    }
    setExpandAll(!expandAll);
  };

  // Group progress updates by phase
  const phaseUpdates = {
    parsing: progress.filter(p => p.phase === 'parsing'),
    rag: progress.filter(p => p.phase === 'rag'),
    llm_generation: progress.filter(p => p.phase === 'llm_generation'),
    saving: progress.filter(p => p.phase === 'saving'),
    complete: progress.filter(p => p.phase === 'complete'),
  };

  // Get phase status
  const getPhaseStatus = (phaseId) => {
    const updates = phaseUpdates[phaseId];
    if (!updates || updates.length === 0) return 'pending';

    const lastUpdate = updates[updates.length - 1];
    return lastUpdate.status || 'pending';
  };

  const phases = [
    {
      id: 'parsing',
      title: 'Phase 1: Parsing Security Reports',
      description: 'Extracting vulnerabilities from uploaded reports',
    },
    {
      id: 'rag',
      title: 'Phase 2: RAG Compliance Retrieval',
      description: 'Fetching compliance context from vector database',
    },
    {
      id: 'llm_generation',
      title: 'Phase 3: AI Policy Generation',
      description: 'Generating policies using LLaMA models',
    },
    {
      id: 'saving',
      title: 'Phase 4: Saving Results',
      description: 'Saving generated policies and reports',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white bg-opacity-20 rounded-lg">
              <Activity className="w-8 h-8 animate-pulse" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">AI Security Policy Generation Pipeline</h2>
              <p className="text-blue-100">Real-time processing with detailed workflow visibility</p>
            </div>
          </div>

          {/* Expand/Collapse All Button */}
          <button
            onClick={toggleExpandAll}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            {expandAll ? (
              <>
                <ChevronUp className="w-4 h-4" />
                <span className="text-sm font-medium">Collapse All</span>
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                <span className="text-sm font-medium">Expand All</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Phases */}
      <div className="space-y-4">
        {phases.map((phase) => (
          <PhaseSection
            key={phase.id}
            phase={phase}
            updates={phaseUpdates[phase.id]}
            status={getPhaseStatus(phase.id)}
            expanded={expandedPhases.has(phase.id)}
            onToggle={() => togglePhase(phase.id)}
          />
        ))}

        {/* Complete Phase */}
        {phaseUpdates.complete.length > 0 && (
          <PhaseSection
            phase={{
              id: 'complete',
              title: 'Pipeline Complete',
              description: 'All policies generated successfully',
            }}
            updates={phaseUpdates.complete}
            status="completed"
            expanded={expandedPhases.has('complete')}
            onToggle={() => togglePhase('complete')}
          />
        )}
      </div>

      {/* Auto-scroll anchor */}
      <div ref={bottomRef} />
    </div>
  );
};

export default WorkflowView;
