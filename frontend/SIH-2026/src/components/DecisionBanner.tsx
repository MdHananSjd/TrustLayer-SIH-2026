import React from "react";
import { Decision } from "../types/audit";

interface DecisionBannerProps {
  decision: Decision;
  demographicParityGap?: number;
  disparateImpactRatio?: number;
  tprGap?: number;
  accuracy?: number;
}

export const DecisionBanner: React.FC<DecisionBannerProps> = ({
  decision,
  demographicParityGap = 0,
  disparateImpactRatio = 1.0,
  tprGap = 0,
  accuracy = 1.0
}) => {
  const isPass = decision.status === "PASS";
  const isWarning = decision.status === "WARNING";
  
  // Current thresholds based on backend updates
  const threshDP = 0.20;
  const threshDI = 0.75;
  const threshTPR = 0.13;
  const threshAcc = 0.85;

  // Use the exact class styles expected by the unit tests to remain green
  const statusColorClass = isPass 
    ? "bg-green-100 text-green-950 border-green-500" 
    : isWarning 
      ? "bg-yellow-100 text-yellow-950 border-yellow-500" 
      : "bg-red-100 text-red-900 border-red-500";

  const lightColorClass = isPass 
    ? "bg-emerald-500" 
    : isWarning 
      ? "bg-amber-500 animate-pulse" 
      : "bg-rose-500";

  // Calculate widths for gauges
  const getGaugePercent = (val: number, max: number) => {
    return Math.min(100, Math.max(0, (val / max) * 100));
  };

  return (
    <div 
      className={`p-6 border-l-8 shadow-sm ${statusColorClass} mb-6`} 
      data-testid="decision-banner"
    >
      {/* Header with status light */}
      <div className="flex items-center justify-between pb-3 border-b border-current/20 mb-4">
        <div className="flex items-center space-x-3">
          <span className={`w-3 h-3 rounded-full ${lightColorClass}`} />
          <h2 className="text-sm font-mono uppercase tracking-widest font-extrabold">
            Deployment Status: {decision.status}
          </h2>
        </div>
        <span className="text-[10px] font-mono opacity-80">
          POLICIES_EVALUATED
        </span>
      </div>

      {/* Signature Element: Interactive Policy Gate Calibrator Gauges */}
      <div className="bg-white/90 p-4 border border-current/10 mb-5 space-y-4 text-slate-800">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-700 font-bold mb-2">
          GATE CALIBRATION METERS:
        </h3>
        
        {/* 1. Demographic Parity Gauge */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] font-mono text-slate-600">
            <span>Demographic Parity Gap (Limit: &lt;= {threshDP.toFixed(2)})</span>
            <span className={demographicParityGap > threshDP ? "text-rose-600 font-bold" : "text-emerald-700"}>
              {demographicParityGap.toFixed(3)}
            </span>
          </div>
          <div className="relative h-2 bg-slate-200 border border-slate-300">
            {/* Limit Marker */}
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-rose-500 z-10"
              style={{ left: `${(threshDP / 0.5) * 100}%` }}
              title="Threshold Limit"
            />
            {/* Value Indicator Bar */}
            <div 
              className={`h-full ${demographicParityGap > threshDP ? "bg-rose-50" : "bg-emerald-500"}`}
              style={{ width: `${getGaugePercent(demographicParityGap, 0.5)}%` }}
            />
          </div>
        </div>

        {/* 2. Disparate Impact Gauge */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] font-mono text-slate-600">
            <span>Disparate Impact Ratio (Limit: &gt;= {threshDI.toFixed(2)})</span>
            <span className={disparateImpactRatio < threshDI ? "text-rose-600 font-bold" : "text-emerald-700"}>
              {disparateImpactRatio.toFixed(3)}
            </span>
          </div>
          <div className="relative h-2 bg-slate-200 border border-slate-300">
            {/* Limit Marker */}
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-emerald-600 z-10"
              style={{ left: `${threshDI * 100}%` }}
              title="Threshold Limit"
            />
            {/* Value Indicator Bar */}
            <div 
              className={`h-full ${disparateImpactRatio < threshDI ? "bg-rose-50" : "bg-emerald-500"}`}
              style={{ width: `${getGaugePercent(disparateImpactRatio, 1.0)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Rules list */}
      <div>
        <span className="font-mono text-xs uppercase tracking-wide block mb-2 font-bold">
          Policy Gate Violations &amp; Triggers:
        </span>
        {decision.reasons.length > 0 ? (
          <ul className="list-none space-y-1.5 font-mono text-xs">
            {decision.reasons.map((reason, index) => (
              <li key={index} className="flex items-start">
                <span className="mr-2">[-]</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="font-mono text-xs">
            [+] All organizational governance check gates passed. Model promoting eligible.
          </p>
        )}
      </div>
    </div>
  );
};
