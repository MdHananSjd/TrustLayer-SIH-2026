#this file defines schemas for api requests
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ModelRegisterRequest(BaseModel):
    name: str
    version: str
    owner: str
    target: str = "approved"
    sensitive_attributes: List[str] = ["gender"]

class ReviewRequest(BaseModel):
    reviewer: str
    decision: str  # APPROVED, REJECTED, OVERRIDDEN
    reason: str

class PolicyRule(BaseModel):
    metric: str
    operator: str
    threshold: float
    severity: str

class PerformanceMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None
    confusion_matrix: Optional[Dict[str, int]] = None

class FairnessMetrics(BaseModel):
    sensitive_attribute: str
    selection_rates: Dict[str, float]
    demographic_parity_gap: float
    disparate_impact_ratio: float
    tpr_gap: float
    status: str

class ExplainabilityMetrics(BaseModel):
    status: str
    global_features: List[Dict[str, Any]]
    local_explanation: List[Dict[str, Any]]

class DriftMetrics(BaseModel):
    status: str
    features: List[Dict[str, Any]]

class DecisionResult(BaseModel):
    status: str
    reasons: List[str]

class AuditResultResponse(BaseModel):
    model: Dict[str, Any]
    performance: PerformanceMetrics
    fairness: FairnessMetrics
    explainability: ExplainabilityMetrics
    drift: DriftMetrics
    decision: DecisionResult