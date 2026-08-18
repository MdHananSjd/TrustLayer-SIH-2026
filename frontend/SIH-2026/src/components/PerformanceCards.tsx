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
    { label: "Accuracy", value: metrics.accuracy },
    { label: "Precision", value: metrics.precision },
    { label: "Recall", value: metrics.recall },
    { label: "F1 Score", value: metrics.f1 },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col items-center justify-center"
        >
          <span className="text-gray-500 text-sm font-medium uppercase tracking-wide">
            {card.label}
          </span>
          <span className="text-3xl font-bold text-gray-800 mt-2">
            {formatPercent(card.value)}
          </span>
        </div>
      ))}
    </div>
  );
};
