import { render, screen } from "@testing-library/react";
import { ResultsPanel } from "../ResultsPanel";
import { useRunStore } from "@/lib/store";
import type { AnalysisResult } from "@/lib/api";

const mockResult: AnalysisResult = {
  regime: {
    regime: "range_bound",
    confidence: 0.9503,
    entropy: 0.187,
    distribution: { range_bound: 24 },
  },
  direction: {
    direction: "down",
    confidence: 0.7046,
    entropy: 0.607,
    prediction_date: "2023-06-30",
    distribution: { down: 20 },
  },
  drift: null,
  feature_importance: null,
  backtest: null,
  summary: "Range-bound regime with high confidence.",
  usage: { input_tokens: 1000, output_tokens: 100, estimated_cost_usd: 0.01 },
  data_manifest: {},
};

beforeEach(() => {
  useRunStore.setState({ runId: null, status: "idle", result: null, error: null });
});

describe("ResultsPanel", () => {
  it("shows skeleton when status is running and result is null", () => {
    useRunStore.setState({ status: "running", result: null });
    render(<ResultsPanel />);
    expect(screen.getByTestId("results-skeleton")).toBeInTheDocument();
  });

  it("shows empty state when idle", () => {
    render(<ResultsPanel />);
    expect(screen.getByText(/results will appear/i)).toBeInTheDocument();
  });

  it("renders RegimeCard with regime label when result is set", () => {
    useRunStore.setState({ status: "completed", result: mockResult });
    render(<ResultsPanel />);
    expect(screen.getByText("Range Bound")).toBeInTheDocument();
  });

  it("renders DirectionCard when result is set", () => {
    useRunStore.setState({ status: "completed", result: mockResult });
    render(<ResultsPanel />);
    expect(screen.getByText("Down")).toBeInTheDocument();
  });

  it("renders SummaryPanel text when result is set", () => {
    useRunStore.setState({ status: "completed", result: mockResult });
    render(<ResultsPanel />);
    expect(screen.getByText("Range-bound regime with high confidence.")).toBeInTheDocument();
  });

  it("shows error state when status is failed", () => {
    useRunStore.setState({ status: "failed", error: "Network error" });
    render(<ResultsPanel />);
    expect(screen.getByText(/Network error/i)).toBeInTheDocument();
  });
});
