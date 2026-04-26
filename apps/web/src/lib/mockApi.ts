import type {
  AiAnalysisResult,
  DashboardSnapshot,
  RetrainingJob
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ??
  `${window.location.protocol}//${window.location.hostname}:8000`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `API request failed for ${path}`);
  }

  return (await response.json()) as T;
}

export async function getDashboardSnapshot(): Promise<DashboardSnapshot> {
  return request<DashboardSnapshot>("/dashboard");
}

export async function refreshSnapshot(): Promise<DashboardSnapshot> {
  return request<DashboardSnapshot>("/dashboard/refresh", {
    method: "POST"
  });
}

export async function simulateLiveUpdate(): Promise<DashboardSnapshot> {
  return request<DashboardSnapshot>("/dashboard/live-tick", {
    method: "POST"
  });
}

export async function getAiAnalysis(): Promise<AiAnalysisResult> {
  return request<AiAnalysisResult>("/analysis", {
    method: "POST"
  });
}

export async function playRetraining(
  onProgress: (step: NonNullable<RetrainingJob["currentStep"]>) => void
): Promise<DashboardSnapshot> {
  const job = await request<RetrainingJob>("/retraining", {
    method: "POST"
  });

  if (job.currentStep) {
    onProgress(job.currentStep);
  }

  while (true) {
    await new Promise((resolve) => {
      window.setTimeout(resolve, 700);
    });

    const status = await request<RetrainingJob>(`/retraining/${job.jobId}`);
    if (status.currentStep) {
      onProgress(status.currentStep);
    }

    if (status.status === "completed" && status.snapshot) {
      return status.snapshot;
    }
  }
}
