import { render, screen } from "@testing-library/react";
import { AgentStreamView } from "../AgentStreamView";
import type { StreamMessage } from "@/lib/websocket";

describe("AgentStreamView", () => {
  it("shows empty state when no run is active", () => {
    render(<AgentStreamView messages={[]} connected={false} isRunning={false} />);
    expect(screen.getByText(/run an analysis/i)).toBeInTheDocument();
  });

  it("shows connecting indicator when running but not yet connected", () => {
    render(<AgentStreamView messages={[]} connected={false} isRunning={true} />);
    expect(screen.getByText(/connecting/i)).toBeInTheDocument();
  });

  it("renders thought messages", () => {
    const messages: StreamMessage[] = [
      { type: "thought", content: "Fetching EIA data" },
    ];
    render(<AgentStreamView messages={messages} connected={true} isRunning={true} />);
    expect(screen.getByText(/Fetching EIA data/)).toBeInTheDocument();
  });

  it("renders tool_call messages with tool name", () => {
    const messages: StreamMessage[] = [
      { type: "tool_call", tool: "run_tabpfn", input: {} },
    ];
    render(<AgentStreamView messages={messages} connected={true} isRunning={true} />);
    expect(screen.getByText(/run_tabpfn/)).toBeInTheDocument();
  });

  it("renders tool_result messages", () => {
    const messages: StreamMessage[] = [
      { type: "tool_result", tool: "run_tabpfn", output: {} },
    ];
    render(<AgentStreamView messages={messages} connected={true} isRunning={true} />);
    expect(screen.getByText(/run_tabpfn/)).toBeInTheDocument();
  });

  it("renders prediction messages with regime and confidence", () => {
    const messages: StreamMessage[] = [
      { type: "prediction", regime: "range_bound", confidence: 0.95 },
    ];
    render(<AgentStreamView messages={messages} connected={true} isRunning={true} />);
    expect(screen.getByText(/range_bound/)).toBeInTheDocument();
    expect(screen.getByText(/95\.0%/)).toBeInTheDocument();
  });

  it("renders done message", () => {
    const messages: StreamMessage[] = [
      { type: "done", summary: "Analysis complete" },
    ];
    render(<AgentStreamView messages={messages} connected={true} isRunning={true} />);
    expect(screen.getByText(/Complete/i)).toBeInTheDocument();
  });

  it("shows connection lost banner when disconnected with messages", () => {
    const messages: StreamMessage[] = [
      { type: "thought", content: "Working..." },
    ];
    render(<AgentStreamView messages={messages} connected={false} isRunning={true} />);
    expect(screen.getByText(/connection lost/i)).toBeInTheDocument();
  });
});
