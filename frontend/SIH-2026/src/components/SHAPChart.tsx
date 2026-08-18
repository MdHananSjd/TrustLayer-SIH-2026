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
  const sortedFeatures = [...features].sort(
    (a, b) => b.importance - a.importance,
  );

  return (
    <div className="bg-white p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-center mb-4 pb-2 border-b border-slate-100">
          <h3 className="text-sm font-mono uppercase tracking-widest text-slate-800 font-bold">
            [03] Global Feature Attribution (SHAP)
          </h3>
          <span className="text-[10px] font-mono text-slate-400">
            MEAN_ABS_SHAP
          </span>
        </div>

        <div className="h-64 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={sortedFeatures}
              margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
              <XAxis 
                type="number" 
                domain={[0, "dataMax + 0.05"]} 
                tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }}
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <YAxis
                dataKey="feature"
                type="category"
                width={85}
                tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }}
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <Tooltip 
                cursor={{ fill: "#f1f5f9" }}
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px' }}
                formatter={(value: any) => {
                  const numValue = typeof value === 'number' ? value : Number(value) || 0;
                  return [numValue.toFixed(3), "Mean |SHAP|"];
                }}
              />
              <Bar
                dataKey="importance"
                name="Mean |SHAP Value|"
                fill="#475569"
                radius={[0, 2, 2, 0]}
                barSize={20}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="mt-4 pt-3 border-t border-slate-100 text-[9px] font-mono text-slate-400">
        * Relates feature attributions to decision impacts across the dataset.
      </div>
    </div>
  );
};
