import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { describe, it, expect, vi, afterEach } from "vitest";
import { ModelSelector } from "../components/ModelSelector";
import React from "react";

// Wipe the DOM after each test
afterEach(() => {
  cleanup();
});

describe("ModelSelector Component", () => {
  it("triggers onRunAudit with correct preloaded ID when using preloaded mode", () => {
    const handleRunAudit = vi.fn();
    render(<ModelSelector onRunAudit={handleRunAudit} isLoading={false} />);

    const select = screen.getByTestId("preloaded-select");
    fireEvent.change(select, { target: { value: "LoanApproval_v2" } });

    const submitButton = screen.getByText("Run Automated Audit");
    fireEvent.click(submitButton);

    expect(handleRunAudit).toHaveBeenCalledTimes(1);
    expect(handleRunAudit).toHaveBeenCalledWith(null, null, "LoanApproval_v2");
  });

  it("switches to custom mode and requires file uploads", () => {
    const handleRunAudit = vi.fn();
    render(<ModelSelector onRunAudit={handleRunAudit} isLoading={false} />);

    const customButton = screen.getByText("Upload Custom Artifacts");
    fireEvent.click(customButton);

    const modelInput = screen.getByTestId("model-upload");
    const dataInput = screen.getByTestId("data-upload");

    const mockModelFile = new File(["dummy content"], "model.pkl", {
      type: "application/octet-stream",
    });
    const mockDataFile = new File(["csv content"], "data.csv", {
      type: "text/csv",
    });

    fireEvent.change(modelInput, { target: { files: [mockModelFile] } });
    fireEvent.change(dataInput, { target: { files: [mockDataFile] } });

    // THE FIX: Bypass JSDOM's strict HTML5 'required' validation intercept by triggering submit directly on the form
    const submitButton = screen.getByText("Run Automated Audit");
    fireEvent.submit(submitButton.closest("form") as HTMLFormElement);

    expect(handleRunAudit).toHaveBeenCalledTimes(1);
    expect(handleRunAudit).toHaveBeenCalledWith(
      mockModelFile,
      mockDataFile,
      "",
      "approved",
      "gender",
    );
  });

  it("disables submit button and changes text when isLoading is true", () => {
    const handleRunAudit = vi.fn();
    render(<ModelSelector onRunAudit={handleRunAudit} isLoading={true} />);

    const submitButton = screen.getByText("Running Audit Pipeline...");
    expect(submitButton).toBeDefined();
    expect((submitButton as HTMLButtonElement).disabled).toBe(true);
  });
});
