const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const REQUEST_TIMEOUT_MS = 30_000;

export type RunStatus = "pending" | "running" | "completed" | "failed";

export type AnalyzeRequest = {
  date_range_start: string;
  date_range_end: string;
  tasks?: string[];
};

export type RunResult = {
  run_id: string;
  status: RunStatus;
  result: Record<string, unknown> | null;
};

export type DerivativesPriceRequest = {
  regime: string;
  spot: number;
  strike: number;
  tenor_days: number;
  option_type?: "call" | "put";
  style?: "european" | "american";
  n_paths?: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...init,
    });
    if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
    return res.json() as Promise<T>;
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  analyze: (body: AnalyzeRequest) =>
    request<{ run_id: string }>("/api/analyze", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getRun: (runId: string) =>
    request<RunResult>(`/api/runs/${runId}`),

  getHistory: () =>
    request<RunResult[]>("/api/history"),

  priceDerivative: (body: DerivativesPriceRequest) =>
    request("/api/derivatives/price", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
