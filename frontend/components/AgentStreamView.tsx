import type { StreamMessage } from "@/lib/websocket";

interface Props {
  messages: StreamMessage[];
  connected: boolean;
  isRunning: boolean;
}

export function AgentStreamView({ messages, connected, isRunning }: Props) {
  if (!isRunning && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-slate-500 dark:text-slate-400 text-sm text-center">
          Run an analysis to see the agent&apos;s reasoning.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto p-4 font-mono text-sm gap-1">
      {isRunning && !connected && messages.length === 0 && (
        <p className="text-slate-400 dark:text-slate-500 text-xs animate-pulse">
          Connecting…
        </p>
      )}
      {!connected && messages.length > 0 && (
        <p className="text-amber-500 text-xs mb-2">Connection lost</p>
      )}
      {messages.map((msg, i) => (
        <MessageRow key={i} message={msg} />
      ))}
    </div>
  );
}

function MessageRow({ message }: { message: StreamMessage }) {
  switch (message.type) {
    case "thought":
      return (
        <div className="text-slate-500 dark:text-slate-400">
          🧠 {message.content}
        </div>
      );
    case "tool_call":
      return (
        <div>
          <span className="text-violet-600 dark:text-violet-400 font-semibold">
            ⚙ tool_call
          </span>{" "}
          <span className="text-slate-700 dark:text-slate-300">{message.tool}</span>
        </div>
      );
    case "tool_result":
      return (
        <div className="pl-4 text-slate-400 dark:text-slate-600 text-xs">
          ✓ tool_result {message.tool}
        </div>
      );
    case "prediction":
      return (
        <div className="text-emerald-600 dark:text-emerald-400">
          📊 {message.regime} · {(message.confidence * 100).toFixed(1)}%
        </div>
      );
    case "done":
      return (
        <div className="text-emerald-600 dark:text-emerald-500 font-semibold">
          ✅ Complete
        </div>
      );
  }
}
