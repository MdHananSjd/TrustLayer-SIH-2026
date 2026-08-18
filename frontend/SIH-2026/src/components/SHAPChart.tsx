import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { GlobalFeature } from "../types/audit";

interface SHAPChartProps {
  features: GlobalFeature[];
}

export const SHAPChart: React.FC<SHAPChartProps> = ({ features }) => {
  // Sort features by importance descending
  const sortedFeatures = [...features].sort(
    (a, b) => b.importance - a.importance,
  );

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-800">
          Global Explainability (SHAP)
        </h3>
        <p className="text-sm text-gray-500">
          Top driving features across all predictions.
        </p>
      </div>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={sortedFeatures}
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[0, "dataMax + 0.1"]} />
            <YAxis
              dataKey="feature"
              type="category"
              width={100}
              tick={{ fontSize: 12 }}
            />
            <Tooltip cursor={{ fill: "#f3f4f6" }} />
            <Bar
              dataKey="importance"
              name="Mean |SHAP Value|"
              fill="#0ea5e9"
              radius={[0, 4, 4, 0]}
              barSize={24}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
