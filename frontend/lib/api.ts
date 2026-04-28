const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type AnalyzeRequest = {
  date_range_start: string;
  date_range_end: string;
  tasks?: string[];
};

export type RunResult = {
  run_id: string;
  status: string;
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
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
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
