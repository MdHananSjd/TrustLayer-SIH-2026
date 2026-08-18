import React from "react";
import { DriftMetrics } from "../types/audit";

interface DriftSectionProps {
  drift: DriftMetrics;
}

export const DriftSection: React.FC<DriftSectionProps> = ({ drift }) => {
  if (drift.status === "NOT_RUN") return null;

  const isWarning = drift.status === "WARNING" || drift.status === "FAIL";

  return (
    <div
      className={`p-6 mt-8 rounded-lg border shadow-sm ${isWarning ? "bg-yellow-50 border-yellow-300" : "bg-green-50 border-green-300"}`}
    >
      <h3
        className={`text-lg font-bold mb-2 ${isWarning ? "text-yellow-800" : "text-green-800"}`}
      >
        Production Monitoring: Data Drift Detected
      </h3>
      {isWarning ? (
        <>
          <p className="text-sm text-yellow-700 mb-3">
            Distribution shifts detected between reference evaluation data and
            Month 2 production batches[cite: 2].
          </p>
          <ul className="list-disc pl-5">
            {drift.features.map((feature, idx) => (
              <li key={idx} className="text-sm font-semibold text-yellow-900">
                Feature: {feature} (Wasserstein Distance threshold exceeded)
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className="text-sm text-green-700">
          No significant feature drift detected in the current production
          window.
        </p>
      )}
    </div>
  );
};
