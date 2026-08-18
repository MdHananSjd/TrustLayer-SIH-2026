import React from "react";
import { AuditResponse } from "../types/audit";

interface ModelComparisonViewProps {
  modelV1: AuditResponse;
  modelV2: AuditResponse;
}

export const ModelComparisonView: React.FC<ModelComparisonViewProps> = ({
  modelV1,
  modelV2,
}) => {
  const getBannerStyles = (status: string) => {
    switch (status) {
      case "PASS":
        return "bg-green-100 text-green-900 border-green-500";
      case "BLOCK":
        return "bg-red-100 text-red-900 border-red-500";
      default:
        return "bg-gray-100 text-gray-900 border-gray-500";
    }
  };

  const calculateDelta = (
    v1: number,
    v2: number,
    invertGoodness: boolean = false,
  ) => {
    const diff = v2 - v1;
    const isPositive = diff > 0;
    const isImprovement = invertGoodness ? !isPositive : isPositive;

    const colorClass = isImprovement ? "text-green-600" : "text-red-600";
    const sign = isPositive ? "+" : "";

    return (
      <span className={`font-bold ${colorClass}`}>
        {sign}
        {diff.toFixed(3)}
      </span>
    );
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mb-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Model Comparison: Accuracy vs Fairness Trade-off
      </h2>

      {/* Governance Status Side-by-Side */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div
          className={`p-4 rounded-lg border-l-8 ${getBannerStyles(modelV1.decision.status)}`}
        >
          <p className="text-sm uppercase font-bold text-gray-500 mb-1">
            {modelV1.model.name} (v{modelV1.model.version})
          </p>
          <h3 className="text-xl font-bold">
            Status: {modelV1.decision.status}
          </h3>
        </div>
        <div
          className={`p-4 rounded-lg border-l-8 ${getBannerStyles(modelV2.decision.status)}`}
        >
          <p className="text-sm uppercase font-bold text-gray-500 mb-1">
            {modelV2.model.name} (v{modelV2.model.version})
          </p>
          <h3 className="text-xl font-bold">
            Status: {modelV2.decision.status}
          </h3>
        </div>
      </div>

      {/* Trade-off Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">
                Metric
              </th>
              <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">
                V1 (Biased)
              </th>
              <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">
                V2 (Mitigated)
              </th>
              <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase tracking-wider">
                Delta
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                Accuracy
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {(modelV1.performance.accuracy * 100).toFixed(1)}%
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {(modelV2.performance.accuracy * 100).toFixed(1)}%
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {calculateDelta(
                  modelV1.performance.accuracy,
                  modelV2.performance.accuracy,
                )}
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                Demographic Parity Gap
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {modelV1.fairness.demographic_parity_gap.toFixed(3)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {modelV2.fairness.demographic_parity_gap.toFixed(3)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {calculateDelta(
                  modelV1.fairness.demographic_parity_gap,
                  modelV2.fairness.demographic_parity_gap,
                  true,
                )}
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                Equal Opportunity Gap
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {modelV1.fairness.tpr_gap.toFixed(3)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {modelV2.fairness.tpr_gap.toFixed(3)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {calculateDelta(
                  modelV1.fairness.tpr_gap,
                  modelV2.fairness.tpr_gap,
                  true,
                )}
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                Disparate Impact Ratio
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {modelV1.fairness.disparate_impact_ratio.toFixed(3)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {modelV2.fairness.disparate_impact_ratio.toFixed(3)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {calculateDelta(
                  modelV1.fairness.disparate_impact_ratio,
                  modelV2.fairness.disparate_impact_ratio,
                )}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
