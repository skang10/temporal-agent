"use client";

import { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { useRunStore } from "@/lib/store";
import { api } from "@/lib/api";

export function TopBar() {
  const [start, setStart] = useState("2023-01-01");
  const [end, setEnd] = useState("2023-06-30");
  const [mode, setMode] = useState<"quick" | "full">("quick");
  const [topbarError, setTopbarError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();

  useEffect(() => setMounted(true), []);
  const { runId, status, setRun, clearRun } = useRunStore();

  const isRunning = status === "running";

  const handleRun = async () => {
    setTopbarError(null);
    try {
      const { run_id } = await api.analyze({
        date_range_start: start,
        date_range_end: end,
        analysis_mode: mode,
      });
      setRun(run_id);
    } catch (e) {
      setTopbarError(e instanceof Error ? e.message : "Failed to start analysis");
    }
  };

  const handleCancel = async () => {
    if (!runId) return;
    try {
      await api.cancelRun(runId);
    } finally {
      clearRun();
    }
  };

  const inputClass =
    "rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 " +
    "text-slate-900 dark:text-slate-100 text-sm px-2 py-1 focus:outline-none focus:ring-1 " +
    "focus:ring-violet-500";

  const pillBase = "text-sm px-3 py-1 rounded-full border transition-colors";
  const pillActive =
    "border-violet-500 bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-300 font-semibold";
  const pillInactive =
    "border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:border-slate-400";

  return (
    <header className="sticky top-0 z-10 flex items-center gap-3 px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f0f1a] flex-wrap">
      <span className="font-bold text-slate-900 dark:text-white text-base mr-1">
        TemporalAgent
      </span>

      <input
        type="date"
        value={start}
        onChange={(e) => setStart(e.target.value)}
        className={inputClass}
        disabled={isRunning}
      />
      <span className="text-slate-400 text-sm">→</span>
      <input
        type="date"
        value={end}
        onChange={(e) => setEnd(e.target.value)}
        className={inputClass}
        disabled={isRunning}
      />

      <div className="flex gap-1">
        <button
          onClick={() => setMode("quick")}
          className={`${pillBase} ${mode === "quick" ? pillActive : pillInactive}`}
          disabled={isRunning}
        >
          Quick
        </button>
        <button
          onClick={() => setMode("full")}
          className={`${pillBase} ${mode === "full" ? pillActive : pillInactive}`}
          disabled={isRunning}
        >
          Full
        </button>
      </div>

      <div className="flex gap-2 ml-auto items-center">
        {topbarError && (
          <span className="text-xs text-red-500">{topbarError}</span>
        )}
        {isRunning ? (
          <button
            onClick={handleCancel}
            className="text-sm px-4 py-1.5 rounded bg-red-500 hover:bg-red-600 text-white font-semibold transition-colors"
          >
            ✕ Cancel
          </button>
        ) : (
          <button
            onClick={handleRun}
            className="text-sm px-4 py-1.5 rounded bg-violet-600 hover:bg-violet-700 text-white font-semibold transition-colors"
          >
            ▶ Run
          </button>
        )}
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-1.5 rounded border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
          aria-label="Toggle theme"
        >
          {mounted ? (theme === "dark" ? "☀" : "🌙") : "☀"}
        </button>
      </div>
    </header>
  );
}
