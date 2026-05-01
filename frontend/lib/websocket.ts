"use client";

import { useEffect, useRef, useState } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
const MAX_MESSAGES = 200;

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

    const socket = new WebSocket(`${WS_URL}/ws/runs/${runId}/stream`);
    ws.current = socket;

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data as string) as StreamMessage;
      setMessages((prev) =>
        prev.length >= MAX_MESSAGES
          ? [...prev.slice(1), msg]
          : [...prev, msg]
      );
    };

    return () => {
      socket.close();
      setMessages([]);
    };
  }, [runId]);

  return { messages, connected };
}
