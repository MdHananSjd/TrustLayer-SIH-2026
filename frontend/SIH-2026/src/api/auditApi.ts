import { AuditResponse } from "../types/audit";
import { mockBiasedModel, mockMitigatedModel } from "../mockData";

const API_BASE = "http://localhost:8000";

export const auditApi = {
  /**
   * POST /audit
   * Uploads model and data files, or triggers an audit for a pre-loaded model.
   * Includes a graceful fallback to mock data to guarantee a working demo[cite: 1, 2].
   */
  runAudit: async (
    modelFile: File | null,
    dataFile: File | null,
    preloadedId: string,
  ): Promise<AuditResponse> => {
    try {
      const formData = new FormData();
      if (modelFile) formData.append("model_file", modelFile);
      if (dataFile) formData.append("evaluation_data", dataFile);
      if (preloadedId) formData.append("preloaded_model_id", preloadedId);

      const response = await fetch(`${API_BASE}/audit`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend returned status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.warn(
        "⚠️ Backend connection failed. Falling back to cached demo artifacts for resilience.",
        error,
      );
      // Resilience Fallback: Ensure the live demo never fails[cite: 2]
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(
            preloadedId === "LoanApproval_v2"
              ? mockMitigatedModel
              : mockBiasedModel,
          );
        }, 1200); // Simulate network delay for the demo illusion
      });
    }
  },

  /**
   * GET /models/{id}/audits/{audit_id}
   * Fetches a specific persisted audit result[cite: 2].
   */
  getAuditResult: async (
    modelId: string,
    auditId: string,
  ): Promise<AuditResponse> => {
    try {
      const response = await fetch(
        `${API_BASE}/models/${modelId}/audits/${auditId}`,
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch audit: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to fetch historical audit:", error);
      throw error;
    }
  },
};
