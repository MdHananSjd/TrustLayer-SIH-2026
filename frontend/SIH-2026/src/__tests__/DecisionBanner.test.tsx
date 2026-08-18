import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { DecisionBanner } from "../components/DecisionBanner";
import { Decision } from "../types/audit";

describe("DecisionBanner Component", () => {
  // Ensure the DOM is cleared after each test
  afterEach(() => {
    cleanup();
  });

  it("renders a BLOCK decision correctly with red styling", () => {
    const mockDecision: Decision = {
      status: "BLOCK",
      reasons: ["Fairness policy failed", "High disparate impact"],
    };

    render(<DecisionBanner decision={mockDecision} />);

    expect(screen.getByText(/Deployment Status: BLOCK/i)).toBeDefined();
    expect(screen.getByText("Fairness policy failed")).toBeDefined();

    const bannerContainer = screen.getByTestId("decision-banner");
    expect(bannerContainer.className).toContain("bg-red-100");
    expect(bannerContainer.className).toContain("text-red-900");
  });

  it("renders a PASS decision correctly with green styling", () => {
    const mockDecision: Decision = {
      status: "PASS",
      reasons: ["All core governance policies met."],
    };

    render(<DecisionBanner decision={mockDecision} />);

    expect(screen.getByText(/Deployment Status: PASS/i)).toBeDefined();
    expect(screen.getByText("All core governance policies met.")).toBeDefined();

    const bannerContainer = screen.getByTestId("decision-banner");
    expect(bannerContainer.className).toContain("bg-green-100");
  });

  it("renders a WARNING decision correctly with yellow styling", () => {
    const mockDecision: Decision = {
      status: "WARNING",
      reasons: ["Minor drift detected in Month 2"],
    };

    render(<DecisionBanner decision={mockDecision} />);

    expect(screen.getByText(/Deployment Status: WARNING/i)).toBeDefined();

    const bannerContainer = screen.getByTestId("decision-banner");
    expect(bannerContainer.className).toContain("bg-yellow-100");
  });
});
