import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ModelComparisonView } from "../components/ModelComparisonView";
import { mockBiasedModel, mockMitigatedModel } from "../mockData";

describe("ModelComparisonView Component", () => {
  it("renders side-by-side banners with correct statuses", () => {
    render(
      <ModelComparisonView
        modelV1={mockBiasedModel}
        modelV2={mockMitigatedModel}
      />,
    );

    // Check titles
    expect(screen.getByText("LoanApproval_v1 (v1.0)")).toBeDefined();
    expect(screen.getByText("LoanApproval_v2 (v2.0)")).toBeDefined();

    // Check exact statuses
    expect(screen.getByText("Status: BLOCK")).toBeDefined();
    expect(screen.getByText("Status: PASS")).toBeDefined();
  });

  it("renders trade-off metrics and calculates delta correctly", () => {
    render(
      <ModelComparisonView
        modelV1={mockBiasedModel}
        modelV2={mockMitigatedModel}
      />,
    );

    // Use getAllByText since table labels appear multiple times
    expect(screen.getAllByText("Accuracy").length).toBeGreaterThan(0);
    expect(
      screen.getAllByText("Demographic Parity Gap").length,
    ).toBeGreaterThan(0);

    // Assert visual deltas exist using getAllByText to handle multiple matching DOM elements safely
    const deltas = screen.getAllByText("-0.210");
    expect(deltas.length).toBeGreaterThan(0);

    // Ensure the improved parity gap delta has the green text class
    expect(deltas[0].className).toContain("text-green-600");
  });
});
