import { create } from "zustand";
import type { AnalysisResult } from "./api";

type RunStatus = "idle" | "running" | "completed" | "failed";

type RunStore = {
  runId: string | null;
  status: RunStatus;
  result: AnalysisResult | null;
  error: string | null;
  setRun: (runId: string) => void;
  setResult: (result: AnalysisResult) => void;
  setStatus: (status: RunStatus) => void;
  setError: (error: string) => void;
  clearRun: () => void;
};

export const useRunStore = create<RunStore>((set) => ({
  runId: null,
  status: "idle",
  result: null,
  error: null,
  setRun: (runId) => set({ runId, status: "running", result: null, error: null }),
  setResult: (result) => set({ result, status: "completed" }),
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error, status: "failed" }),
  clearRun: () => set({ runId: null, status: "idle", result: null, error: null }),
}));
