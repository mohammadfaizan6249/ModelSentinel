import type { FeatureMetric, RetrainProgress } from "../types";

interface RetrainModalProps {
  open: boolean;
  features: FeatureMetric[];
  progress: RetrainProgress | null;
  running: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function RetrainModal({
  open,
  features,
  progress,
  running,
  onClose,
  onConfirm
}: RetrainModalProps) {
  const critical = features
    .filter((feature) => feature.status === "critical")
    .map((feature) => feature.name);
  const warning = features
    .filter((feature) => feature.status === "warning")
    .map((feature) => feature.name);

  return (
    <div className={`modal-overlay ${open ? "open" : ""}`}>
      <div className="modal">
        <div className="modal-title">⚡ Trigger Model Retraining</div>
        <div className="modal-body">
          You are about to schedule a full retraining job for{" "}
          <strong>CreditRisk_v2.x</strong>. This refresh will use the most recent
          90 days of production data as the next reference window.
        </div>

        <div className="modal-info">
          Drifted features detected:
          <br />
          {critical.length > 0 ? `  CRITICAL: ${critical.join(", ")}` : "  CRITICAL: none"}
          <br />
          {warning.length > 0 ? `  WARNING:  ${warning.join(", ")}` : "  WARNING:  none"}
          <br />
          <br />
          Estimated retraining time: ~18 minutes
          <br />
          Data window: 90 days (mock snapshot for Phase 1)
        </div>

        {running && progress ? (
          <div className="retrain-progress show">
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress.progress}%` }}
              />
            </div>
            <div className="progress-label">{progress.label}</div>
          </div>
        ) : null}

        {!running ? (
          <div className="modal-row">
            <button className="btn btn-ghost btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button className="btn btn-confirm btn-retrain" onClick={onConfirm}>
              Confirm Retraining
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
