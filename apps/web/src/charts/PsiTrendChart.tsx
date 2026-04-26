import { useEffect, useRef } from "react";
import type { FeatureStatus } from "../types";
import { Chart } from "./chartSetup";

const labels = Array.from({ length: 24 }, (_, index) =>
  `${String(index).padStart(2, "0")}:00`
);

interface PsiTrendChartProps {
  status: FeatureStatus;
  series: number[];
}

function getSeriesColors(status: FeatureStatus) {
  if (status === "critical") {
    return {
      stroke: "#ff4466",
      fill: "rgba(255,68,102,0.08)"
    };
  }
  if (status === "warning") {
    return {
      stroke: "#ffaa00",
      fill: "rgba(255,170,0,0.08)"
    };
  }
  return {
    stroke: "#00e5a0",
    fill: "rgba(0,229,160,0.08)"
  };
}

export function PsiTrendChart({ status, series }: PsiTrendChartProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart<"line"> | null>(null);

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }

    const colors = getSeriesColors(status);
    const dataset = {
      labels,
      datasets: [
        {
          data: series,
          borderColor: colors.stroke,
          backgroundColor: colors.fill,
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4,
          fill: true,
          tension: 0.4
        },
        {
          data: Array(24).fill(0.25),
          borderColor: "rgba(255,68,102,0.5)",
          borderWidth: 1,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false
        },
        {
          data: Array(24).fill(0.1),
          borderColor: "rgba(255,170,0,0.5)",
          borderWidth: 1,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false
        }
      ]
    };

    if (chartRef.current) {
      chartRef.current.data = dataset;
      chartRef.current.update();
      return;
    }

    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: dataset,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: "#1a2d45" },
            ticks: {
              color: "#4d7090",
              autoSkip: true,
              maxTicksLimit: 8,
              font: {
                family: "'JetBrains Mono', monospace",
                size: 9
              }
            }
          },
          y: {
            grid: { color: "#1a2d45" },
            ticks: {
              color: "#4d7090",
              font: {
                family: "'JetBrains Mono', monospace",
                size: 9
              }
            }
          }
        }
      }
    });

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [series, status]);

  return (
    <div className="chart-canvas-wrap chart-canvas-wrap-short">
      <canvas ref={canvasRef} />
    </div>
  );
}
