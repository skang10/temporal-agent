"use client";

import { useEffect } from "react";
import { useRunStore } from "@/lib/store";
import { useRunStream } from "@/lib/websocket";
import { api } from "@/lib/api";
import { AgentStreamView } from "./AgentStreamView";
import type { AnalysisResult } from "@/lib/api";

export function AgentStream() {
  const { runId, status, setResult, setStatus } = useRunStore();
  const { messages, connected } = useRunStream(runId);

  useEffect(() => {
    const last = messages[messages.length - 1];
    if (last?.type !== "done" || !runId || status === "completed") return;

    api
      .getRun(runId)
      .then((runResult) => {
        if (runResult.result) {
          setResult(runResult.result as AnalysisResult);
        } else {
          setStatus("failed");
        }
      })
      .catch(() => setStatus("failed"));
  }, [messages, runId, status, setResult, setStatus]);

  return (
    <AgentStreamView
      messages={messages}
      connected={connected}
      isRunning={status === "running"}
    />
  );
}
