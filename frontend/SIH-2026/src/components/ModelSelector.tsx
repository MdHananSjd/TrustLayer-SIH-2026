import React, { useState } from "react";

interface ModelSelectorProps {
  onRunAudit: (
    modelFile: File | null,
    dataFile: File | null,
    preloadedId: string,
    targetField?: string,
  ) => void;
  isLoading: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  onRunAudit,
  isLoading,
}) => {
  const [mode, setMode] = useState<"preloaded" | "custom">("preloaded");
  const [preloadedId, setPreloadedId] = useState<string>("LoanApproval_v1");
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [dataFile, setDataFile] = useState<File | null>(null);
  const [targetColumn, setTargetColumn] = useState<string>("approved");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "preloaded") {
      onRunAudit(null, null, preloadedId);
    } else {
      onRunAudit(modelFile, dataFile, "", targetColumn);
    }
  };

  return (
    <div className="bg-white p-6 border border-slate-200 shadow-sm">
      <div className="flex justify-between items-center mb-6 pb-2 border-b border-slate-100">
        <h2 className="text-sm font-mono uppercase tracking-widest text-slate-800 font-bold">
          [01] Ingestion Configuration
        </h2>
        <span className="text-[10px] font-mono text-slate-400">
          MODE_SELECT
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-6">
        <button
          type="button"
          onClick={() => setMode("preloaded")}
          className={`py-2 px-3 text-xs font-mono uppercase tracking-wider transition-colors border text-center ${
            mode === "preloaded"
              ? "bg-slate-900 border-slate-900 text-white font-bold"
              : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900"
          }`}
        >
          Use Pre-loaded Demo Models
        </button>
        <button
          type="button"
          onClick={() => setMode("custom")}
          className={`py-2 px-3 text-xs font-mono uppercase tracking-wider transition-colors border text-center ${
            mode === "custom"
              ? "bg-slate-900 border-slate-900 text-white font-bold"
              : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900"
          }`}
        >
          Upload Custom Artifacts
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {mode === "preloaded" ? (
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-slate-500 mb-2">
              Select Target Model
            </label>
            <select
              value={preloadedId}
              onChange={(e) => setPreloadedId(e.target.value)}
              className="block w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm font-medium py-2 px-3 focus:outline-none focus:border-blue-600"
              data-testid="preloaded-select"
            >
              <option value="LoanApproval_v1">
                LoanApproval_v1 (Biased Baseline)
              </option>
              <option value="LoanApproval_v2">
                LoanApproval_v2 (Mitigated Classifier)
              </option>
            </select>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-500 mb-2">
                Model Pipeline (.pkl / .joblib)
              </label>
              <input
                type="file"
                accept=".pkl,.joblib"
                onChange={(e) => setModelFile(e.target.files?.[0] || null)}
                className="block w-full text-xs text-slate-500 border border-slate-200 bg-slate-50 p-2 focus:outline-none focus:border-blue-600
                  file:mr-4 file:py-1 file:px-3 file:border file:border-slate-300 file:font-mono file:text-[10px] file:uppercase file:bg-white file:text-slate-700 hover:file:bg-slate-100"
                data-testid="model-upload"
                required={mode === "custom"}
              />
            </div>
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-500 mb-2">
                Evaluation Dataset (.csv)
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setDataFile(e.target.files?.[0] || null)}
                className="block w-full text-xs text-slate-500 border border-slate-200 bg-slate-50 p-2 focus:outline-none focus:border-blue-600
                  file:mr-4 file:py-1 file:px-3 file:border file:border-slate-300 file:font-mono file:text-[10px] file:uppercase file:bg-white file:text-slate-700 hover:file:bg-slate-100"
                data-testid="data-upload"
                required={mode === "custom"}
              />
            </div>
            <div>
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-500 mb-2">
                Target Column Name
              </label>
              <input
                type="text"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                placeholder="e.g. approved"
                className="block w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs py-2 px-3 focus:outline-none focus:border-blue-600"
                required={mode === "custom"}
              />
            </div>
          </div>
        )}

        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-2.5 px-4 text-xs font-mono uppercase tracking-widest text-white transition-colors border shadow-sm ${
              isLoading
                ? "bg-slate-700 border-slate-600 cursor-not-allowed text-slate-300 animate-pulse"
                : "bg-blue-600 border-blue-600 hover:bg-blue-700 font-bold"
            }`}
          >
            {isLoading ? "Running Audit Pipeline..." : "Run Automated Audit"}
          </button>
        </div>
      </form>
    </div>
  );
};
