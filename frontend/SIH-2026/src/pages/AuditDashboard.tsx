import React, { useState } from "react";
import { auditApi } from "../api/auditApi";
import { AuditResponse } from "../types/audit";
import { ModelSelector } from "../components/ModelSelector";
import { DecisionBanner } from "../components/DecisionBanner";
import { PerformanceCards } from "../components/PerformanceCards";
import { FairnessChart } from "../components/FairnessChart";
import { SHAPChart } from "../components/SHAPChart";
import { DriftSection } from "../components/DriftSection";
import { ReportAction } from "../components/ReportAction";

export const AuditDashboard: React.FC = () => {
  const [auditData, setAuditData] = useState<AuditResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>("IDLE");
  const [error, setError] = useState<string | null>(null);
  const [preloadedId, setPreloadedId] = useState<string>("LoanApproval_v1");
  
  // Auditor Override Form States
  const [reviewerName, setReviewerName] = useState<string>("");
  const [reviewDecision, setReviewDecision] = useState<string>("APPROVED");
  const [reviewReason, setReviewReason] = useState<string>("");
  const [overrideStatus, setOverrideStatus] = useState<string | null>(null);
  const [submittingReview, setSubmittingReview] = useState<boolean>(false);

  const simulateLoadingSteps = async () => {
    const steps = [
      "CONNECTING_TO_MODEL_REGISTRY",
      "PARSING_EVALUATION_DATASET",
      "RUNNING_PREDICTION_COMPUTATION",
      "EVALUATING_PERFORMANCE_METRICS",
      "CALCULATING_DEMOGRAPHIC_PARITY_GAP",
      "SCANNING_PROXY_FEATURES",
      "GENERATING_SHAP_ATTRIBUTIONS",
      "COMPILING_POLICY_ENGINE_VERDICT"
    ];
    
    for (const step of steps) {
      setLoadingStep(step);
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  };

  const handleRunAudit = async (
    modelFile: File | null,
    dataFile: File | null,
    selectedId: string,
    targetField?: string,
    sensitiveField?: string,
  ) => {
    setPreloadedId(selectedId || "custom");
    setIsLoading(true);
    setError(null);
    setOverrideStatus(null);
    setReviewerName("");
    setReviewReason("");

    try {
      // Run visual step log first
      await simulateLoadingSteps();
      
      const response = await auditApi.runAudit(
        modelFile,
        dataFile,
        selectedId,
        targetField,
        sensitiveField,
      );
      setAuditData(response);
    } catch (err: any) {
      setError(
        err.message || "Audit pipeline failed. Please verify the backend is running."
      );
    } finally {
      setIsLoading(false);
      setLoadingStep("IDLE");
    }
  };

  const handleOverrideSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!auditData || !auditData.model.id) return;
    
    setSubmittingReview(true);
    setOverrideStatus(null);
    
    try {
      const result = await auditApi.submitReview(
        auditData.model.id,
        reviewerName,
        reviewDecision,
        reviewReason
      );
      
      // Successfully registered override in the backend
      setOverrideStatus(`OVERRIDE_RECORDED: Model promo eligibility set to ${reviewDecision}.`);
      
      // Update local status for responsive visual confirmation
      setAuditData(prev => {
        if (!prev) return null;
        return {
          ...prev,
          decision: {
            ...prev.decision,
            status: reviewDecision === "APPROVED" ? "PASS" : reviewDecision === "REJECTED" ? "BLOCK" : "WARNING",
            reasons: [
              `Reviewer override applied: ${reviewDecision} by ${reviewerName}`,
              `Justification: ${reviewReason}`
            ]
          }
        };
      });
    } catch (err: any) {
      setError("Failed to register auditor review: " + err.message);
    } finally {
      setSubmittingReview(false);
    }
  };

  // Policy Threshold references
  const policiesList = [
    { name: "fairness.demographic_parity_gap", op: "<=", limit: 0.20, severity: "BLOCK" },
    { name: "fairness.disparate_impact_ratio", op: ">=", limit: 0.75, severity: "BLOCK" },
    { name: "fairness.tpr_gap", op: "<=", limit: 0.13, severity: "WARNING" },
    { name: "performance.accuracy", op: ">=", limit: 0.85, severity: "BLOCK" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-6 selection:bg-blue-100">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Navigation / Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b border-slate-200">
          <div>
            <div className="text-[10px] font-mono tracking-widest text-blue-600 font-bold mb-1">
              TRUSTLAYER // continuous compliance
            </div>
            <h1 className="text-2xl font-black tracking-tight text-slate-950 font-display uppercase">
              AI Governance Pipeline Control Panel
            </h1>
          </div>
          <div className="mt-3 md:mt-0 flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-mono text-slate-600">CLUSTER: ACTIVE_INTEGRITY</span>
            </div>
            {auditData && auditData.model.id && (
              <ReportAction modelId={auditData.model.id} auditId={auditData.model.id} />
            )}
          </div>
        </div>

        {/* Dashboard Split Panel Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Panel: Configuration & Policies (4 Cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Model & File Selection */}
            <ModelSelector onRunAudit={handleRunAudit} isLoading={isLoading} />

            {/* Policy Inspector Panel */}
            <div className="bg-white p-6 border border-slate-200 shadow-sm">
              <div className="flex justify-between items-center mb-4 pb-2 border-b border-slate-100">
                <h3 className="text-sm font-mono uppercase tracking-widest text-slate-800 font-bold">
                  [04] Active Policy Schema
                </h3>
                <span className="text-[10px] font-mono text-slate-400">
                  SYSTEM_RULES
                </span>
              </div>
              <p className="text-xs text-slate-500 mb-4 font-mono">
                The gates evaluate incoming classifiers against active regulatory thresholds:
              </p>
              <div className="space-y-3">
                {policiesList.map((p, idx) => (
                  <div key={idx} className="bg-slate-50 p-2.5 border border-slate-100 font-mono text-[10px] space-y-1">
                    <div className="flex justify-between text-slate-700 font-bold">
                      <span>{p.name}</span>
                      <span className={p.severity === "BLOCK" ? "text-rose-600" : "text-amber-600"}>
                        {p.severity}
                      </span>
                    </div>
                    <div className="text-slate-400 flex justify-between">
                      <span>Operator: {p.op}</span>
                      <span>Limit: {p.limit.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Right Panel: Executive Audit Presentation (8 Cols) */}
          <div className="lg:col-span-8">
            
            {/* Error alerts */}
            {error && (
              <div className="bg-rose-50 border border-rose-300 text-rose-800 p-4 mb-6 font-mono text-xs">
                <div className="font-bold mb-1">AUDIT_PIPELINE_ERROR:</div>
                <p>{error}</p>
              </div>
            )}

            {/* Console Log Loading State */}
            {isLoading && (
              <div className="bg-slate-950 text-slate-200 border border-slate-800 p-8 shadow-sm flex flex-col justify-center min-h-[400px]">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="font-mono text-xs text-blue-400 animate-pulse uppercase tracking-wider">
                    Governance pipeline is active...
                  </span>
                </div>
                <div className="space-y-2 font-mono text-[11px] text-slate-400">
                  <p className="text-slate-500">&gt; npm run governance --target={preloadedId || "custom"}</p>
                  <p className={loadingStep !== "IDLE" ? "text-slate-200" : ""}>
                    [STATUS] CURRENT_RUNNING_CHECK: <span className="text-blue-400 font-bold">{loadingStep}</span>
                  </p>
                  <p>&gt; Ingesting model cards and alignment files...</p>
                  <p>&gt; Executing calibration tests over test sample...</p>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && !auditData && (
              <div className="bg-white border border-slate-200 p-12 text-center flex flex-col items-center justify-center min-h-[400px] shadow-sm">
                <div className="w-12 h-12 border border-dashed border-slate-400 flex items-center justify-center mb-4 text-slate-500 font-mono text-xs">
                  OFFLINE
                </div>
                <h3 className="text-sm font-mono uppercase tracking-widest text-slate-800 font-bold mb-2">
                  Validation Queue Empty
                </h3>
                <p className="text-xs text-slate-500 max-w-sm">
                  Select a preloaded demonstration model or upload binary model files and data sets on the left control panel to trigger automated audits.
                </p>
              </div>
            )}

            {/* Audit Presentation */}
            {!isLoading && auditData && (
              <div className="space-y-6 animate-fade-in-up">
                
                {/* Model Title Card */}
                <div className="flex justify-between items-center pb-2 border-b border-slate-200">
                  <h2 className="text-sm font-mono uppercase tracking-wider text-slate-800 font-bold">
                    Audit Output: <span className="text-blue-600 font-black">{auditData.model.name} (v{auditData.model.version})</span>
                  </h2>
                  <span className="text-[9px] font-mono text-slate-400 uppercase bg-slate-100 py-1 px-2 rounded-sm">
                    ID: {auditData.model.id}
                  </span>
                </div>

                {/* Verdict banner with Calibration Gauges */}
                <DecisionBanner 
                  decision={auditData.decision} 
                  demographicParityGap={auditData.fairness.demographic_parity_gap}
                  disparateImpactRatio={auditData.fairness.disparate_impact_ratio}
                  tprGap={auditData.fairness.tpr_gap}
                  accuracy={auditData.performance.accuracy}
                />

                {/* Performance Grid */}
                <div>
                  <PerformanceCards metrics={auditData.performance} />
                </div>

                {/* Recharts Side-by-Side Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FairnessChart fairness={auditData.fairness} />
                  <SHAPChart features={auditData.explainability.global_features} />
                </div>

                {/* Production Monitoring Drift Section */}
                <DriftSection drift={auditData.drift} />

                {/* Auditor Overrides / Human Override Card */}
                {(auditData.decision.status === "BLOCK" || auditData.decision.status === "WARNING") && (
                  <div className="bg-white p-6 border border-slate-200 shadow-sm mt-6">
                    <div className="flex justify-between items-center mb-4 pb-2 border-b border-slate-100">
                      <h3 className="text-sm font-mono uppercase tracking-widest text-slate-800 font-bold">
                        [05] Human Review &amp; Promotability override
                      </h3>
                      <span className="text-[10px] font-mono text-slate-400">
                        AUDITOR_SIGN_OFF
                      </span>
                    </div>

                    {overrideStatus && (
                      <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 p-3 mb-4 font-mono text-[11px]">
                        {overrideStatus}
                      </div>
                    )}

                    <form onSubmit={handleOverrideSubmit} className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">
                            Auditor Sign-off Name
                          </label>
                          <input
                            type="text"
                            required
                            value={reviewerName}
                            onChange={(e) => setReviewerName(e.target.value)}
                            placeholder="e.g. Lead Auditor Alice"
                            className="block w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs py-2 px-3 focus:outline-none focus:border-blue-600"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">
                            Override Verdict
                          </label>
                          <select
                            value={reviewDecision}
                            onChange={(e) => setReviewDecision(e.target.value)}
                            className="block w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs py-2 px-3 focus:outline-none focus:border-blue-600"
                          >
                            <option value="APPROVED">APPROVE &amp; FORCE PROMOTION</option>
                            <option value="REJECTED">REJECT &amp; DISALLOW DEPLOYMENT</option>
                            <option value="OVERRIDDEN">RECORD EXCEPTION (ELIGIBLE)</option>
                          </select>
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">
                          Auditor Policy Justification
                        </label>
                        <textarea
                          required
                          rows={3}
                          value={reviewReason}
                          onChange={(e) => setReviewReason(e.target.value)}
                          placeholder="Provide regulatory justification or mitigation comments explaining the override context..."
                          className="block w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs p-3 focus:outline-none focus:border-blue-600"
                        />
                      </div>

                      <div className="flex justify-end pt-2">
                        <button
                          type="submit"
                          disabled={submittingReview}
                          className="px-4 py-2 text-xs font-mono uppercase tracking-wider bg-slate-900 border border-slate-900 hover:bg-slate-800 text-white font-bold transition-colors"
                        >
                          {submittingReview ? "Registering Override..." : "Submit Override Signature"}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

              </div>
            )}

          </div>

        </div>

      </div>
    </div>
  );
};

export default AuditDashboard;
