interface Props {
  summary: string;
}

export function SummaryPanel({ summary }: Props) {
  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 border-l-4 border-l-violet-500 dark:border-l-violet-600">
      <span className="text-xs font-semibold tracking-widest text-slate-500 dark:text-slate-400 uppercase block mb-2">
        Summary
      </span>
      <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
        {summary}
      </p>
    </div>
  );
}
