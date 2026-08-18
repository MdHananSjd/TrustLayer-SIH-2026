import React, { useState } from "react";
import { auditApi } from "../api/auditApi";
import { AuditResponse } from "../types/audit";
import { ModelSelector } from "../components/ModelSelector";
import { DecisionBanner } from "../components/DecisionBanner";
import { PerformanceCards } from "../components/PerformanceCards";
import { FairnessChart } from "../components/FairnessChart";
import { SHAPChart } from "../components/SHAPChart";

export const AuditDashboard: React.FC = () => {
  const [auditData, setAuditData] = useState<AuditResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAudit = async (
    modelFile: File | null,
    dataFile: File | null,
    preloadedId: string,
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await auditApi.runAudit(
        modelFile,
        dataFile,
        preloadedId,
      );
      setAuditData(response);
    } catch (err) {
      setError(
        "Audit failed. Please verify the backend is running and file formats are correct.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-end pb-4 border-b border-gray-200">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              TrustLayer Governance Pipeline
            </h1>
            <p className="text-gray-500 mt-1">
              Continuous Responsible AI Assurance Platform
            </p>
          </div>
          {auditData && (
            <button className="px-4 py-2 text-sm font-medium rounded-md bg-gray-800 text-white shadow-sm hover:bg-gray-700 transition-colors">
              Export Audit PDF
            </button>
          )}
        </div>

        {/* Input Configuration */}
        <ModelSelector onRunAudit={handleRunAudit} isLoading={isLoading} />

        {/* Status Handling */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-md">
            <p className="text-sm text-red-700 font-medium">{error}</p>
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
            <p className="text-gray-600 font-medium animate-pulse">
              Running governance checks (Performance, Fairness, SHAP)...
            </p>
          </div>
        )}

        {/* Audit Results Presentation */}
        {!isLoading && auditData && (
          <div className="animate-fade-in-up">
            <div className="mb-6">
              <h2 className="text-xl font-bold">
                Audit Results:{" "}
                <span className="text-indigo-600">
                  {auditData.model.name} (v{auditData.model.version})
                </span>
              </h2>
            </div>

            <DecisionBanner decision={auditData.decision} />

            <div>
              <h2 className="text-lg font-bold mb-4 text-gray-800">
                Overall Performance
              </h2>
              <PerformanceCards metrics={auditData.performance} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <FairnessChart fairness={auditData.fairness} />
              <SHAPChart features={auditData.explainability.global_features} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditDashboard;
