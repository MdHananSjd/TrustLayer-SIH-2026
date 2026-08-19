import React from "react";
import { DriftMetrics } from "../types/audit";

interface DriftSectionProps {
  drift: DriftMetrics;
}

export const DriftSection: React.FC<DriftSectionProps> = ({ drift }) => {
  if (drift.status === "NOT_RUN") return null;

  const isWarning = drift.status === "WARNING" || drift.status === "FAIL";
  
  const statusColorClass = isWarning 
    ? "bg-amber-50 border-amber-300 text-amber-800" 
    : "bg-emerald-50 border-emerald-300 text-emerald-800";

  return (
    <div className={`p-6 border shadow-sm ${statusColorClass} mt-6`}>
      <div className="flex justify-between items-center mb-3 pb-1 border-b border-current/20">
        <h3 className="text-xs font-mono uppercase tracking-widest font-extrabold">
          Production Monitoring: Feature Drift Checks
        </h3>
        <span className="text-[9px] font-mono opacity-80">
          MONITOR_DRIFT
        </span>
      </div>

      {isWarning ? (
        <div className="space-y-3 font-mono text-xs">
          <p className="opacity-90">
            Distribution shifts detected between baseline validation and production data streams:
          </p>
          <ul className="list-none pl-1 space-y-1">
            {drift.features.map((featureItem, idx) => {
              // Gracefully handle both string lists and dictionary lists from different API variants
              const name = typeof featureItem === "object" && featureItem !== null 
                ? (featureItem as any).feature 
                : featureItem;
              return (
                <li key={idx} className="flex items-center text-[11px] font-bold text-amber-900">
                  <span className="mr-2">[-]</span>
                  <span>Feature: {name} (Wasserstein threshold exceeded)</span>
                </li>
              );
            })}
          </ul>
        </div>
      ) : (
        <p className="font-mono text-xs opacity-90">
          [+] No significant feature distribution drift detected in current production monitoring window.
        </p>
      )}
    </div>
  );
};
