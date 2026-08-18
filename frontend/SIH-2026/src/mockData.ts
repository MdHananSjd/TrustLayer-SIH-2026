import { AuditResponse } from "./types/audit";

export const mockBiasedModel: AuditResponse = {
  model: { name: "LoanApproval_v1", version: "1.0" },
  performance: { accuracy: 0.91, precision: 0.89, recall: 0.88, f1: 0.88 },
  fairness: {
    sensitive_attribute: "gender",
    selection_rates: { group_Male: 0.78, group_Female: 0.52 },
    demographic_parity_gap: 0.26,
    disparate_impact_ratio: 0.67,
    tpr_gap: 0.17,
    status: "FAIL",
  },
  explainability: {
    status: "PASS",
    global_features: [
      { feature: "income", importance: 0.32 },
      { feature: "credit_score", importance: 0.28 },
      { feature: "debt_ratio", importance: 0.15 },
      { feature: "employment_years", importance: 0.11 },
      { feature: "gender", importance: 0.08 },
    ],
    local_explanation: [
      { feature: "income", value: 45000, contribution: -0.12 },
      { feature: "gender", value: "Female", contribution: -0.15 },
    ],
  },
  drift: { status: "NOT_RUN", features: [] },
  decision: {
    status: "BLOCK",
    reasons: [
      "Fairness policy failed: Demographic parity gap (0.26) exceeds maximum threshold (0.15)",
      "Fairness policy failed: Disparate impact ratio (0.67) is below minimum threshold (0.80)",
    ],
  },
};

export const mockMitigatedModel: AuditResponse = {
  model: { name: "LoanApproval_v2", version: "2.0" },
  performance: { accuracy: 0.89, precision: 0.86, recall: 0.87, f1: 0.86 },
  fairness: {
    sensitive_attribute: "gender",
    selection_rates: { group_Male: 0.7, group_Female: 0.65 },
    demographic_parity_gap: 0.05,
    disparate_impact_ratio: 0.93,
    tpr_gap: 0.03,
    status: "PASS",
  },
  explainability: {
    status: "PASS",
    global_features: [
      { feature: "income", importance: 0.35 },
      { feature: "credit_score", importance: 0.31 },
      { feature: "debt_ratio", importance: 0.18 },
      { feature: "employment_years", importance: 0.12 },
      { feature: "gender", importance: 0.01 },
    ],
    local_explanation: [
      { feature: "income", value: 45000, contribution: -0.12 },
      { feature: "gender", value: "Female", contribution: -0.01 },
    ],
  },
  drift: { status: "NOT_RUN", features: [] },
  decision: {
    status: "PASS",
    reasons: ["All core governance policies met."],
  },
};
