import type { AlertItem } from "../types";

interface AlertLogProps {
  alerts: AlertItem[];
}

export function AlertLog({ alerts }: AlertLogProps) {
  return (
    <section className="alert-log">
      <div className="panel-header">
        <span className="panel-title">Alert Log</span>
        <span className="panel-hint">{alerts.length} active alerts</span>
      </div>

      <div>
        {alerts.length === 0 ? (
          <div className="empty-state">
            No active drift alerts. The current model slice is within thresholds.
          </div>
        ) : (
          alerts.map((alert) => (
            <div className="alert-item" key={alert.id}>
              <div className={`alert-dot ${alert.level}`} />
              <div>
                <div className="alert-text">
                  <span className="alert-feature">{alert.feature}</span> —{" "}
                  {alert.message}
                </div>
                <div className="alert-time">{alert.timeAgo}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
