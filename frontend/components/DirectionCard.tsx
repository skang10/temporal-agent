import type { DirectionResult } from "@/lib/api";

interface Props {
  direction: DirectionResult;
}

export function DirectionCard({ direction }: Props) {
  const isUp = direction.direction === "up";
  const pct = (direction.confidence * 100).toFixed(1);

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold tracking-widest text-slate-500 dark:text-slate-400 uppercase">
          WTI Direction
        </span>
        <span className="text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded">
          {pct}%
        </span>
      </div>
      <div className="flex items-center gap-3 mb-3">
        <span
          className={`text-4xl font-bold leading-none ${
            isUp
              ? "text-emerald-500 dark:text-emerald-400"
              : "text-red-500 dark:text-red-400"
          }`}
        >
          {isUp ? "↑" : "↓"}
        </span>
        <span
          className={`text-2xl font-bold ${
            isUp
              ? "text-emerald-600 dark:text-emerald-400"
              : "text-red-600 dark:text-red-400"
          }`}
        >
          {isUp ? "Up" : "Down"}
        </span>
      </div>
      <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full">
        <div
          className={`h-1.5 rounded-full ${
            isUp ? "bg-emerald-500" : "bg-red-500"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-slate-400 dark:text-slate-600 mt-1">
        as of {direction.prediction_date}
      </p>
    </div>
  );
}
