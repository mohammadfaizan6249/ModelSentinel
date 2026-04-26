import type { GlobalStatus } from "../types";

interface TopBarProps {
  modelName: string;
  environment: string;
  status: GlobalStatus;
  clock: string;
  liveMode: boolean;
  onRefresh: () => void;
  onToggleLive: () => void;
  onOpenRetrain: () => void;
  onOpenAi: () => void;
}

export function TopBar(props: TopBarProps) {
  const statusLabel =
    props.status === "critical"
      ? "CRITICAL DRIFT"
      : props.status === "warning"
        ? "DRIFT WARNING"
        : "HEALTHY";

  return (
    <header className="topbar">
      <div className="logo">
        <div className="logo-icon" aria-hidden="true">
          <svg viewBox="0 0 14 14" fill="none">
            <path
              d="M7 1L13 4V10L7 13L1 10V4L7 1Z"
              stroke="#060b12"
              strokeWidth="1.5"
            />
            <circle cx="7" cy="7" r="2" fill="#060b12" />
          </svg>
        </div>
        Model<span>Sentinel</span>
      </div>

      <div className="divider" />

      <div className="model-tag">
        {props.modelName} · {props.environment}
      </div>

      <div className={`status-pill ${props.status}`}>
        <span className={`pulse ${props.status}`} />
        <span>{statusLabel}</span>
      </div>

      <div className="topbar-right">
        <span className="timestamp">{props.clock}</span>
        <button className="btn btn-ghost" onClick={props.onRefresh}>
          ↻ Refresh
        </button>
        <button
          className={`btn btn-live ${props.liveMode ? "active" : ""}`}
          onClick={props.onToggleLive}
        >
          ● Live
        </button>
        <button className="btn btn-retrain" onClick={props.onOpenRetrain}>
          ⚡ Trigger Retraining
        </button>
        <button className="btn btn-ai" onClick={props.onOpenAi}>
          ✦ AI Analysis
        </button>
      </div>
    </header>
  );
}
