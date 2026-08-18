import React, { useState } from "react";

interface ModelSelectorProps {
  onRunAudit: (
    modelFile: File | null,
    dataFile: File | null,
    preloadedId: string,
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "preloaded") {
      onRunAudit(null, null, preloadedId);
    } else {
      onRunAudit(modelFile, dataFile, "");
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        Audit Configuration
      </h2>

      <div className="flex space-x-4 mb-6">
        <button
          type="button"
          onClick={() => setMode("preloaded")}
          className={`px-4 py-2 text-sm font-medium rounded-md ${mode === "preloaded" ? "bg-indigo-50 text-indigo-700 border border-indigo-200" : "bg-white text-gray-600 border border-gray-300 hover:bg-gray-50"}`}
        >
          Use Pre-loaded Demo Models
        </button>
        <button
          type="button"
          onClick={() => setMode("custom")}
          className={`px-4 py-2 text-sm font-medium rounded-md ${mode === "custom" ? "bg-indigo-50 text-indigo-700 border border-indigo-200" : "bg-white text-gray-600 border border-gray-300 hover:bg-gray-50"}`}
        >
          Upload Custom Artifacts
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {mode === "preloaded" ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Demo Model
            </label>
            <select
              value={preloadedId}
              onChange={(e) => setPreloadedId(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
              data-testid="preloaded-select"
            >
              <option value="LoanApproval_v1">
                LoanApproval_v1 (Biased Baseline)
              </option>
              <option value="LoanApproval_v2">
                LoanApproval_v2 (Mitigated)
              </option>
            </select>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model File (.pkl)
              </label>
              <input
                type="file"
                accept=".pkl,.joblib"
                onChange={(e) => setModelFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                data-testid="model-upload"
                required={mode === "custom"}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Evaluation Data (.csv)
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setDataFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                data-testid="data-upload"
                required={mode === "custom"}
              />
            </div>
          </div>
        )}

        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className={`px-6 py-2 text-sm font-bold rounded-md text-white shadow-sm transition-colors ${isLoading ? "bg-indigo-400 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700"}`}
          >
            {isLoading ? "Running Audit Pipeline..." : "Run Automated Audit"}
          </button>
        </div>
      </form>
    </div>
  );
};
