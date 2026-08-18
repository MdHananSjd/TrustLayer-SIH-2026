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
} from "recharts";
import { FairnessMetrics } from "../types/audit";

interface FairnessChartProps {
  fairness: FairnessMetrics;
}

export const FairnessChart: React.FC<FairnessChartProps> = ({ fairness }) => {
  const chartData = useMemo(() => {
    return Object.entries(fairness.selection_rates).map(([group, rate]) => ({
      group: group.replace("group_", ""),
      selectionRate: rate,
    }));
  }, [fairness.selection_rates]);

  // Current thresholds
  const limitDP = 0.20;
  const limitDI = 0.75;
  const limitTPR = 0.13;

  return (
    <div className="bg-white p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-center mb-4 pb-2 border-b border-slate-100">
          <h3 className="text-sm font-mono uppercase tracking-widest text-slate-800 font-bold">
            [02] Demographic Selection Rates
          </h3>
          <span className="text-[10px] font-mono text-slate-400">
            SENSITIVE_FIELD: {fairness.sensitive_attribute.toUpperCase()}
          </span>
        </div>

        <div className="h-64 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 10, left: -25, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis 
                dataKey="group" 
                tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }} 
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <YAxis
                tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
                domain={[0, 1]}
                tick={{ fill: '#64748b', fontSize: 10, fontFamily: 'monospace' }}
                axisLine={{ stroke: '#cbd5e1' }}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px' }}
                formatter={(value: any) => {
                  const numValue = typeof value === 'number' ? value : Number(value) || 0;
                  return [`${(numValue * 100).toFixed(1)}%`, "Approval Rate"];
                }}
              />
              <Legend verticalAlign="top" height={36} iconType="rect" iconSize={10} wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
              <Bar
                dataKey="selectionRate"
                name="Selection Rate (Approved)"
                fill="#2563eb"
                radius={[2, 2, 0, 0]}
                maxBarSize={50}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-2 text-center border-t border-slate-100 pt-4">
        <div>
          <p className="text-[9px] font-mono text-slate-400 uppercase tracking-wider">
            Demographic Parity
          </p>
          <p
            className={`text-lg font-mono font-bold mt-1 ${
              fairness.demographic_parity_gap > limitDP ? "text-rose-600" : "text-emerald-700"
            }`}
          >
            {fairness.demographic_parity_gap.toFixed(3)}
          </p>
        </div>
        <div>
          <p className="text-[9px] font-mono text-slate-400 uppercase tracking-wider">
            Disparate Impact
          </p>
          <p
            className={`text-lg font-mono font-bold mt-1 ${
              fairness.disparate_impact_ratio < limitDI ? "text-rose-600" : "text-emerald-700"
            }`}
          >
            {fairness.disparate_impact_ratio.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-[9px] font-mono text-slate-400 uppercase tracking-wider">
            Equal Opportunity
          </p>
          <p
            className={`text-lg font-mono font-bold mt-1 ${
              fairness.tpr_gap > limitTPR ? "text-rose-600" : "text-emerald-700"
            }`}
          >
            {fairness.tpr_gap.toFixed(3)}
          </p>
        </div>
      </div>
    </div>
  );
};
