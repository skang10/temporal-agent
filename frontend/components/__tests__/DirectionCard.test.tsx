import { render, screen } from "@testing-library/react";
import { DirectionCard } from "../DirectionCard";
import type { DirectionResult } from "@/lib/api";

const down: DirectionResult = {
  direction: "down",
  confidence: 0.7046,
  entropy: 0.607,
  prediction_date: "2023-06-30",
  distribution: { down: 20 },
};

const up: DirectionResult = {
  ...down,
  direction: "up",
  confidence: 0.82,
};

describe("DirectionCard", () => {
  it("shows Down label for down direction", () => {
    render(<DirectionCard direction={down} />);
    expect(screen.getByText("Down")).toBeInTheDocument();
  });

  it("shows Up label for up direction", () => {
    render(<DirectionCard direction={up} />);
    expect(screen.getByText("Up")).toBeInTheDocument();
  });

  it("displays confidence as percentage", () => {
    render(<DirectionCard direction={down} />);
    expect(screen.getByText("70.5%")).toBeInTheDocument();
  });

  it("displays prediction date", () => {
    render(<DirectionCard direction={down} />);
    expect(screen.getByText(/2023-06-30/)).toBeInTheDocument();
  });

  it("shows down arrow for down direction", () => {
    render(<DirectionCard direction={down} />);
    expect(screen.getByText("↓")).toBeInTheDocument();
  });

  it("shows up arrow for up direction", () => {
    render(<DirectionCard direction={up} />);
    expect(screen.getByText("↑")).toBeInTheDocument();
  });
});
