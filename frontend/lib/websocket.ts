"use client";

import { useEffect, useRef, useState } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export type StreamMessage =
  | { type: "thought"; content: string }
  | { type: "tool_call"; tool: string; input: unknown }
  | { type: "tool_result"; tool: string; output: unknown }
  | { type: "prediction"; regime: string; confidence: number }
  | { type: "done"; summary: string };

export function useRunStream(runId: string | null) {
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!runId) return;

    ws.current = new WebSocket(`${WS_URL}/ws/runs/${runId}/stream`);

    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => setConnected(false);
    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data as string) as StreamMessage;
      setMessages((prev) => [...prev, msg]);
    };

    return () => ws.current?.close();
  }, [runId]);

  return { messages, connected };
}
