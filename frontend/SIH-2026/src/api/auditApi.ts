import { AuditResponse } from "../types/audit";
import { mockBiasedModel, mockMitigatedModel } from "../mockData";

const API_BASE = "http://localhost:8000/api/v1";

export const auditApi = {
  /**
   * POST /models/{id}/audit
   * Handles both preloaded models and custom file uploads by integrating with our real FastAPI backend.
   */
  runAudit: async (
    modelFile: File | null,
    dataFile: File | null,
    preloadedId: string,
    targetField?: string,
  ): Promise<AuditResponse> => {
    try {
      let activeModelId = preloadedId;

      // Map demo select values to pre-registered backend IDs
      if (preloadedId === "LoanApproval_v1") {
        activeModelId = "model-loan-01";
      } else if (preloadedId === "LoanApproval_v2") {
        activeModelId = "model-loan-02";
      }

      // If custom files are uploaded, orchestrate registration & artifact upload
      if (!modelFile && !dataFile && activeModelId) {
        // 1. Direct Demo Model Audit
        const response = await fetch(`${API_BASE}/models/${activeModelId}/audit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        if (!response.ok) throw new Error(`Audit execution failed: ${response.status}`);
        return await response.json();
      } else if (modelFile && dataFile) {
        // 2. Custom Model Registration
        const regPayload = {
          name: modelFile.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " "),
          version: "1.0",
          owner: "Auditor Upload",
          target: targetField || "approved",
          sensitive_attributes: ["gender"]
        };

        const regResponse = await fetch(`${API_BASE}/models`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(regPayload)
        });
        if (!regResponse.ok) throw new Error(`Model registration failed: ${regResponse.status}`);
        const regData = await regResponse.json();
        const customModelId = regData.id;

        // 3. Artifacts Upload
        const formData = new FormData();
        formData.append("model_file", modelFile);
        formData.append("eval_csv", dataFile);

        const uploadResponse = await fetch(`${API_BASE}/models/${customModelId}/artifacts`, {
          method: "POST",
          body: formData
        });
        if (!uploadResponse.ok) {
          const errDetail = await uploadResponse.json().catch(() => ({}));
          throw new Error(errDetail.detail || `Artifact upload failed: ${uploadResponse.status}`);
        }

        // 4. Run Audit
        const auditResponse = await fetch(`${API_BASE}/models/${customModelId}/audit`, {
          method: "POST"
        });
        if (!auditResponse.ok) throw new Error(`Custom audit run failed: ${auditResponse.status}`);
        return await auditResponse.json();
      } else {
        throw new Error("Invalid selection: Must select either a demo model or upload both custom model and CSV files.");
      }
    } catch (error: any) {
      // If we are in custom upload mode, we should NOT fallback to mock data!
      if (modelFile || dataFile) {
        throw error;
      }

      console.warn(
        "⚠️ Live API call failed. Falling back to cached demo artifacts for resilience.",
        error,
      );
      // Fallback to local mocks
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(
            preloadedId === "LoanApproval_v2"
              ? mockMitigatedModel
              : mockBiasedModel,
          );
        }, 1200);
      });
    }
  },

  /**
   * GET /models/{id}/audits/{audit_id}
   */
  getAuditResult: async (
    modelId: string,
    auditId: string,
  ): Promise<AuditResponse> => {
    const response = await fetch(`${API_BASE}/models/${modelId}/audits/${auditId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch audit: ${response.status}`);
    }
    return await response.json();
  },

  /**
   * POST /audits/{audit_id}/review
   */
  submitReview: async (
    auditId: string,
    reviewer: string,
    decision: string,
    reason: string
  ): Promise<any> => {
    const response = await fetch(`${API_BASE}/audits/${auditId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewer, decision, reason })
    });
    if (!response.ok) {
      throw new Error(`Review submission failed: ${response.status}`);
    }
    return await response.json();
  }
};
