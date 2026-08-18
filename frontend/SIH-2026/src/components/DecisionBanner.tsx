import React from "react";
import { Decision } from "../types/audit";

interface DecisionBannerProps {
  decision: Decision;
}

export const DecisionBanner: React.FC<DecisionBannerProps> = ({ decision }) => {
  const getBannerStyles = () => {
    switch (decision.status) {
      case "PASS":
        return "bg-green-100 text-green-900 border-green-500";
      case "WARNING":
        return "bg-yellow-100 text-yellow-900 border-yellow-500";
      case "BLOCK":
        return "bg-red-100 text-red-900 border-red-500";
      default:
        return "bg-gray-100 text-gray-900 border-gray-500";
    }
  };

  return (
    <div
      className={`p-6 mb-6 rounded-lg border-l-8 shadow-sm ${getBannerStyles()}`}
      data-testid="decision-banner"
    >
      <h2 className="text-2xl font-bold tracking-tight uppercase">
        Deployment Status: {decision.status}
      </h2>
      <div className="mt-3">
        <span className="font-semibold block mb-1">
          Governance Policy Engine Output:
        </span>
        <ul className="list-disc pl-5 space-y-1">
          {decision.reasons.map((reason, index) => (
            <li key={index} className="text-sm font-medium">
              {reason}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
