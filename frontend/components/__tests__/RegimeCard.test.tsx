import { render, screen } from "@testing-library/react";
import { RegimeCard } from "../RegimeCard";
import type { RegimeResult } from "@/lib/api";

const rangebound: RegimeResult = {
  regime: "range_bound",
  confidence: 0.9503,
  entropy: 0.187,
  distribution: { range_bound: 24 },
};

describe("RegimeCard", () => {
  it("displays the regime label formatted", () => {
    render(<RegimeCard regime={rangebound} />);
    expect(screen.getByText("Range Bound")).toBeInTheDocument();
  });

  it("displays confidence as percentage", () => {
    render(<RegimeCard regime={rangebound} />);
    expect(screen.getByText("95.0%")).toBeInTheDocument();
  });

  it("displays entropy value", () => {
    render(<RegimeCard regime={rangebound} />);
    expect(screen.getByText(/0\.187/)).toBeInTheDocument();
  });

  it("renders bull_supercycle label formatted", () => {
    const bull: RegimeResult = { ...rangebound, regime: "bull_supercycle" };
    render(<RegimeCard regime={bull} />);
    expect(screen.getByText("Bull Supercycle")).toBeInTheDocument();
  });

  it("renders geopolitical_spike label formatted", () => {
    const spike: RegimeResult = { ...rangebound, regime: "geopolitical_spike" };
    render(<RegimeCard regime={spike} />);
    expect(screen.getByText("Geopolitical Spike")).toBeInTheDocument();
  });
});
