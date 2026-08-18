import React, { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { FairnessMetrics } from "../types/audit";

interface FairnessChartProps {
  fairness: FairnessMetrics;
}

export const FairnessChart: React.FC<FairnessChartProps> = ({ fairness }) => {
  // Transform Record<string, number> into Recharts array format
  const chartData = useMemo(() => {
    return Object.entries(fairness.selection_rates).map(([group, rate]) => ({
      group: group.replace("group_", ""),
      selectionRate: rate,
    }));
  }, [fairness.selection_rates]);

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-800">Fairness Metrics</h3>
        <p className="text-sm text-gray-500">
          Sensitive Attribute:{" "}
          <span className="font-semibold text-gray-700">
            {fairness.sensitive_attribute}
          </span>
        </p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="group" />
            <YAxis
              tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
              domain={[0, 1]}
            />
            <Tooltip
              formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
            />
            <Legend />
            <Bar
              dataKey="selectionRate"
              name="Selection Rate (Approval)"
              fill="#4F46E5"
              radius={[4, 4, 0, 0]}
              maxBarSize={60}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4 text-center border-t border-gray-100 pt-4">
        <div>
          <p className="text-xs text-gray-500 uppercase">
            Demographic Parity Gap
          </p>
          <p
            className={`text-lg font-bold ${fairness.demographic_parity_gap > 0.15 ? "text-red-600" : "text-green-600"}`}
          >
            {fairness.demographic_parity_gap.toFixed(3)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase">Disparate Impact</p>
          <p
            className={`text-lg font-bold ${fairness.disparate_impact_ratio < 0.8 ? "text-red-600" : "text-green-600"}`}
          >
            {fairness.disparate_impact_ratio.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase">
            Equal Opportunity Gap
          </p>
          <p
            className={`text-lg font-bold ${fairness.tpr_gap > 0.15 ? "text-red-600" : "text-green-600"}`}
          >
            {fairness.tpr_gap.toFixed(3)}
          </p>
        </div>
      </div>
    </div>
  );
};
