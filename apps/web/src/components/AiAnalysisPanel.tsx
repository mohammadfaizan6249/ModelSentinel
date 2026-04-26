import { formatAnalysisTime } from "../lib/dashboard";
import type { AiAnalysisResult } from "../types";

interface AiAnalysisPanelProps {
  open: boolean;
  loading: boolean;
  analysis: AiAnalysisResult | null;
  onClose: () => void;
  onRun: () => void;
}

export function AiAnalysisPanel({
  open,
  loading,
  analysis,
  onClose,
  onRun
}: AiAnalysisPanelProps) {
  return (
    <aside className={`ai-panel ${open ? "open" : ""}`}>
      <div className="ai-panel-header">
        <span className="ai-panel-title">✦ AI Drift Analysis</span>
        <button className="ai-close" onClick={onClose} aria-label="Close panel">
          ✕
        </button>
      </div>

      <div className="ai-panel-body">
        {!analysis && !loading ? (
          <>
            <p className="ai-placeholder">
              Run a mock ML incident analysis to generate root-cause reasoning,
              business impact, and recommended next actions from the current
              drift profile.
            </p>
            <button className="btn btn-ai ai-run-btn" onClick={onRun}>
              Run Analysis ↗
            </button>
          </>
        ) : null}

        {loading ? (
          <div className="ai-loading">
            <div className="ai-spinner" />
            <span>Analyzing drift patterns...</span>
          </div>
        ) : null}

        {analysis ? (
          <div>
            <div className="ai-meta">
              ModelSentinel mock analysis · {formatAnalysisTime(analysis.generatedAt)}
            </div>
            <div className="ai-content">
              {analysis.sections.map((section) => (
                <div key={section.title}>
                  <h3>{section.title}</h3>
                  <p>{section.body}</p>
                </div>
              ))}
            </div>
            <div className="ai-note">{analysis.note}</div>
            <button className="btn btn-ai ai-run-btn" onClick={onRun}>
              ↻ Re-analyze
            </button>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
