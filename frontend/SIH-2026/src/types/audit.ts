export interface ModelMetadata {
  name: string;
  version: string;
}

export interface PerformanceMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}

export interface FairnessMetrics {
  sensitive_attribute: string;
  selection_rates: Record<string, number>;
  demographic_parity_gap: number;
  disparate_impact_ratio: number;
  tpr_gap: number;
  status: "PASS" | "WARNING" | "FAIL";
}

export interface GlobalFeature {
  feature: string;
  importance: number;
}

export interface LocalExplanation {
  feature: string;
  value: number | string;
  contribution: number;
}

export interface ExplainabilityMetrics {
  status: "PASS" | "WARNING" | "FAIL";
  global_features: GlobalFeature[];
  local_explanation: LocalExplanation[];
}

export interface DriftMetrics {
  status: "NOT_RUN" | "PASS" | "WARNING" | "FAIL";
  features: string[];
}

export interface Decision {
  status: "PASS" | "WARNING" | "BLOCK";
  reasons: string[];
}

export interface AuditResponse {
  model: ModelMetadata;
  performance: PerformanceMetrics;
  fairness: FairnessMetrics;
  explainability: ExplainabilityMetrics;
  drift: DriftMetrics;
  decision: Decision;
}
