import { useEffect, useMemo, useState } from "react";
import { AlertLog } from "./components/AlertLog";
import { AiAnalysisPanel } from "./components/AiAnalysisPanel";
import { ChartsPanel } from "./components/ChartsPanel";
import { FeatureTable } from "./components/FeatureTable";
import { RetrainModal } from "./components/RetrainModal";
import { SummaryCards } from "./components/SummaryCards";
import { TopBar } from "./components/TopBar";
import { calculateSummaryFromSnapshot, formatClock } from "./lib/dashboard";
import {
  getAiAnalysis,
  getDashboardSnapshot,
  playRetraining,
  refreshSnapshot,
  simulateLiveUpdate
} from "./lib/mockApi";
import type {
  AiAnalysisResult,
  DashboardSnapshot,
  RetrainProgress
} from "./types";

function App() {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedFeatureIndex, setSelectedFeatureIndex] = useState(0);
  const [clock, setClock] = useState(formatClock(new Date().toISOString()));
  const [liveMode, setLiveMode] = useState(false);
  const [aiOpen, setAiOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<AiAnalysisResult | null>(null);
  const [retrainOpen, setRetrainOpen] = useState(false);
  const [retrainRunning, setRetrainRunning] = useState(false);
  const [retrainProgress, setRetrainProgress] = useState<RetrainProgress | null>(
    null
  );

  useEffect(() => {
    void getDashboardSnapshot()
      .then((nextSnapshot) => {
        setSnapshot(nextSnapshot);
        setLoadError(null);
      })
      .catch((error: Error) => {
        setLoadError(error.message);
      });
  }, []);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setClock(formatClock(new Date().toISOString()));
    }, 1000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);

  useEffect(() => {
    if (!liveMode) {
      return;
    }

    let active = true;
    let inFlight = false;
    const intervalId = window.setInterval(() => {
      if (inFlight) {
        return;
      }
      inFlight = true;
      void simulateLiveUpdate()
        .then((nextSnapshot) => {
          if (active) {
            setSnapshot(nextSnapshot);
          }
        })
        .finally(() => {
          inFlight = false;
        });
    }, 2200);

    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, [liveMode]);

  const summary = useMemo(
    () => {
      if (!snapshot) {
        return null;
      }
      const criticalCount = snapshot.features.filter(
        (feature) => feature.status === "critical"
      ).length;
      const warningCount = snapshot.features.filter(
        (feature) => feature.status === "warning"
      ).length;
      const avgPsi =
        snapshot.features.reduce((total, feature) => total + feature.psi, 0) /
        snapshot.features.length;

      return calculateSummaryFromSnapshot(
        snapshot.features.length,
        criticalCount,
        warningCount,
        avgPsi,
        snapshot.healthPercent,
        snapshot.healthDeltaText
      );
    },
    [snapshot]
  );

  const selectedFeature = snapshot?.features[selectedFeatureIndex] ?? null;

  async function handleRefresh() {
    try {
      const next = await refreshSnapshot();
      setSnapshot(next);
      setLoadError(null);
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : "Refresh failed.");
    }
  }

  async function handleRunAnalysis() {
    if (!snapshot) {
      return;
    }
    setAiAnalysis(null);
    setAiLoading(true);
    const analysis = await getAiAnalysis();
    setAiAnalysis(analysis);
    setAiLoading(false);
  }

  async function handleConfirmRetraining() {
    if (!snapshot) {
      return;
    }

    setRetrainRunning(true);
    const recovered = await playRetraining((step) => {
      setRetrainProgress(step);
    });
    setSnapshot(recovered);
    setRetrainRunning(false);
    setRetrainProgress(null);
    window.setTimeout(() => {
      setRetrainOpen(false);
    }, 900);
  }

  if (!snapshot || !summary || !selectedFeature) {
    if (loadError) {
      return (
        <div className="app-loading app-error">
          <div className="error-card">
            <h1>ModelSentinel Could Not Load</h1>
            <p>
              The frontend is running, but it could not reach the API at{" "}
              <code>{`${window.location.protocol}//${window.location.hostname}:8000`}</code>.
            </p>
            <p className="error-detail">{loadError}</p>
            <p>Start the API in another terminal with:</p>
            <pre>make run-api</pre>
            <button
              className="btn btn-ai error-btn"
              onClick={() => {
                setLoadError(null);
                void getDashboardSnapshot()
                  .then((nextSnapshot) => {
                    setSnapshot(nextSnapshot);
                  })
                  .catch((error: Error) => {
                    setLoadError(error.message);
                  });
              }}
            >
              Retry Connection
            </button>
          </div>
        </div>
      );
    }
    return <div className="app-loading">Booting ModelSentinel dashboard...</div>;
  }

  return (
    <div className="app-shell">
      <TopBar
        modelName={snapshot.modelName}
        environment={snapshot.environment}
        status={summary.globalStatus}
        clock={clock}
        liveMode={liveMode}
        onRefresh={() => void handleRefresh()}
        onToggleLive={() => setLiveMode((current) => !current)}
        onOpenRetrain={() => setRetrainOpen(true)}
        onOpenAi={() => setAiOpen(true)}
      />

      <main className="main">
        <SummaryCards
          summary={summary}
          monitoredFeaturesDelta={snapshot.monitoredFeaturesDelta}
        />

        <div className="main-grid section-gap">
          <FeatureTable
            features={snapshot.features}
            selectedIndex={selectedFeatureIndex}
            onSelect={setSelectedFeatureIndex}
          />
          <ChartsPanel feature={selectedFeature} />
        </div>

        <AlertLog alerts={snapshot.alerts} />
      </main>

      <AiAnalysisPanel
        open={aiOpen}
        loading={aiLoading}
        analysis={aiAnalysis}
        onClose={() => setAiOpen(false)}
        onRun={() => void handleRunAnalysis()}
      />

      <RetrainModal
        open={retrainOpen}
        features={snapshot.features}
        progress={retrainProgress}
        running={retrainRunning}
        onClose={() => {
          if (!retrainRunning) {
            setRetrainOpen(false);
          }
        }}
        onConfirm={() => void handleConfirmRetraining()}
      />
    </div>
  );
}

export default App;
