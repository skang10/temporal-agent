"use client";

import { useRunStore } from "@/lib/store";
import { RegimeCard } from "./RegimeCard";
import { DirectionCard } from "./DirectionCard";
import { SummaryPanel } from "./SummaryPanel";

export function ResultsPanel() {
  const { status, result, error } = useRunStore();

  if (status === "idle") {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-sm text-slate-500 dark:text-slate-400 text-center">
          Results will appear here after analysis completes.
        </p>
      </div>
    );
  }

  if (status === "running" && !result) {
    return (
      <div
        data-testid="results-skeleton"
        className="flex flex-col gap-3 p-4 animate-pulse"
      >
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 rounded-lg bg-slate-100 dark:bg-slate-800"
          />
        ))}
      </div>
    );
  }

  if (status === "failed") {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="text-center">
          <p className="text-sm text-red-500 dark:text-red-400 mb-2">
            {error ?? "Analysis failed"}
          </p>
        </div>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div className="flex flex-col gap-3 p-4 overflow-y-auto">
      {result.regime && <RegimeCard regime={result.regime} />}
      {result.direction && <DirectionCard direction={result.direction} />}
      {result.summary && <SummaryPanel summary={result.summary} />}
    </div>
  );
}
