import { useEffect, useRef } from "react";
import { Chart } from "./chartSetup";

const labels = [
  "<10",
  "10-20",
  "20-30",
  "30-40",
  "40-50",
  "50-60",
  "60-70",
  "70-80",
  "80-90",
  "90+"
];

interface DistributionChartProps {
  baseline: number[];
  current: number[];
}

export function DistributionChart({
  baseline,
  current
}: DistributionChartProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart<"bar"> | null>(null);

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }

    const dataset = {
      labels,
      datasets: [
        {
          label: "Baseline",
          data: baseline.map((value) => Number((value * 100).toFixed(1))),
          backgroundColor: "rgba(77,159,255,0.35)",
          borderColor: "#4d9fff",
          borderWidth: 1.5,
          borderRadius: 3
        },
        {
          label: "Current",
          data: current.map((value) => Number((value * 100).toFixed(1))),
          backgroundColor: "rgba(255,68,102,0.35)",
          borderColor: "#ff4466",
          borderWidth: 1.5,
          borderRadius: 3
        }
      ]
    };

    if (chartRef.current) {
      chartRef.current.data = dataset;
      chartRef.current.update();
      return;
    }

    chartRef.current = new Chart(canvasRef.current, {
      type: "bar",
      data: dataset,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: "#4d7090",
              font: {
                family: "'JetBrains Mono', monospace",
                size: 10
              },
              boxWidth: 10,
              padding: 12
            }
          }
        },
        scales: {
          x: {
            grid: { color: "#1a2d45" },
            ticks: {
              color: "#4d7090",
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
  }, [baseline, current]);

  return (
    <div className="chart-canvas-wrap">
      <canvas ref={canvasRef} />
    </div>
  );
}
