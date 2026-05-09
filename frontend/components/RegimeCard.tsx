import type { RegimeResult } from "@/lib/api";

interface Props {
  regime: RegimeResult;
}

const REGIME_COLORS: Record<string, string> = {
  range_bound: "text-violet-600 dark:text-violet-400",
  bull_supercycle: "text-emerald-600 dark:text-emerald-400",
  bust: "text-red-600 dark:text-red-400",
  geopolitical_spike: "text-amber-600 dark:text-amber-400",
};

const REGIME_BAR: Record<string, string> = {
  range_bound: "bg-violet-500",
  bull_supercycle: "bg-emerald-500",
  bust: "bg-red-500",
  geopolitical_spike: "bg-amber-500",
};

function formatRegime(regime: string): string {
  return regime
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function RegimeCard({ regime }: Props) {
  const pct = (regime.confidence * 100).toFixed(1);
  const color = REGIME_COLORS[regime.regime] ?? "text-slate-600 dark:text-slate-400";
  const barColor = REGIME_BAR[regime.regime] ?? "bg-slate-500";

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold tracking-widest text-slate-500 dark:text-slate-400 uppercase">
          Regime
        </span>
        <span className="text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded">
          {pct}%
        </span>
      </div>
      <p className={`text-2xl font-bold mb-3 ${color}`}>{formatRegime(regime.regime)}</p>
      <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full">
        <div
          className={`h-1.5 rounded-full ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-slate-400 dark:text-slate-600 mt-1 text-right">
        entropy {regime.entropy.toFixed(3)}
      </p>
    </div>
  );
}
