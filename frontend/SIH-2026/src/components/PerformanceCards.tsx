import React from "react";
import { PerformanceMetrics } from "../types/audit";

interface PerformanceCardsProps {
  metrics: PerformanceMetrics;
}

export const PerformanceCards: React.FC<PerformanceCardsProps> = ({
  metrics,
}) => {
  const formatPercent = (val: number) => `${(val * 100).toFixed(1)}%`;

  const cards = [
    { label: "Accuracy", value: metrics.accuracy, key: "acc" },
    { label: "Precision", value: metrics.precision, key: "prec" },
    { label: "Recall (TPR)", value: metrics.recall, key: "rec" },
    { label: "F1 Score", value: metrics.f1, key: "f1" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-white p-5 border border-slate-200 shadow-sm flex flex-col justify-between"
        >
          <span className="text-slate-400 font-mono text-[10px] uppercase tracking-wider block">
            {card.label}
          </span>
          <span className="text-3xl font-mono font-bold text-slate-800 mt-2 block tracking-tight">
            {formatPercent(card.value)}
          </span>
          <div className="mt-2 pt-1 border-t border-slate-100 flex justify-between text-[8px] font-mono text-slate-400">
            <span>METRIC_VAL</span>
            <span>[{card.key.toUpperCase()}]</span>
          </div>
        </div>
      ))}
    </div>
  );
};
