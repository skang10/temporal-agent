import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useRunStream } from "../websocket";

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  closed = false;

  constructor(public url: string) {
    MockWebSocket.instances.push(this);
  }

  close() {
    this.closed = true;
    this.onclose?.();
  }

  emit(data: object) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
}

beforeEach(() => {
  MockWebSocket.instances = [];
  vi.stubGlobal("WebSocket", MockWebSocket);
});

describe("useRunStream", () => {
  it("does not connect when runId is null", () => {
    renderHook(() => useRunStream(null));
    expect(MockWebSocket.instances).toHaveLength(0);
  });

  it("connects when runId is provided", () => {
    renderHook(() => useRunStream("run-1"));
    expect(MockWebSocket.instances).toHaveLength(1);
    expect(MockWebSocket.instances[0].url).toContain("run-1");
  });

  it("sets connected true on open", () => {
    const { result } = renderHook(() => useRunStream("run-1"));
    act(() => MockWebSocket.instances[0].onopen?.());
    expect(result.current.connected).toBe(true);
  });

  it("sets connected false on close", () => {
    const { result } = renderHook(() => useRunStream("run-1"));
    act(() => MockWebSocket.instances[0].onopen?.());
    act(() => MockWebSocket.instances[0].onclose?.());
    expect(result.current.connected).toBe(false);
  });

  it("appends incoming messages", () => {
    const { result } = renderHook(() => useRunStream("run-1"));
    act(() =>
      MockWebSocket.instances[0].emit({ type: "thought", content: "Thinking..." })
    );
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toEqual({ type: "thought", content: "Thinking..." });
  });

  it("resets messages when runId changes", () => {
    const { result, rerender } = renderHook(({ id }) => useRunStream(id), {
      initialProps: { id: "run-1" },
    });
    act(() =>
      MockWebSocket.instances[0].emit({ type: "thought", content: "msg from run-1" })
    );
    expect(result.current.messages).toHaveLength(1);

    rerender({ id: "run-2" });
    expect(result.current.messages).toHaveLength(0);
  });

  it("caps messages at MAX_MESSAGES (200)", () => {
    const { result } = renderHook(() => useRunStream("run-1"));
    act(() => {
      for (let i = 0; i < 210; i++) {
        MockWebSocket.instances[0].emit({ type: "thought", content: `msg ${i}` });
      }
    });
    expect(result.current.messages).toHaveLength(200);
    // oldest messages should be evicted
    expect(result.current.messages[0]).toEqual({ type: "thought", content: "msg 10" });
  });

  it("closes socket on unmount", () => {
    const { unmount } = renderHook(() => useRunStream("run-1"));
    const socket = MockWebSocket.instances[0];
    unmount();
    expect(socket.closed).toBe(true);
  });
});
