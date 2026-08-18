import uuid
from typing import Dict, Any, List, Optional
from app.models.schemas import ModelRegisterRequest, PolicyRule
from app.services.policy_engine import evaluate_policies, DEFAULT_POLICIES

class AuditStore:
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {
            "model-loan-01": {
                "id": "model-loan-01",
                "name": "LoanApproval_v1",
                "version": "1.0",
                "owner": "Risk Assessment Team",
                "target": "approved",
                "sensitive_attributes": ["gender", "age"],
                "status": "Under Review"
            }
        }
        self.audits: Dict[str, Dict[str, Any]] = {}
        self.reviews: Dict[str, List[Dict[str, Any]]] = {}
        self.policies: List[PolicyRule] = DEFAULT_POLICIES

    def register_model(self, req: ModelRegisterRequest) -> Dict[str, Any]:
        model_id = f"model-{uuid.uuid4().hex[:6]}"
        entry = {
            "id": model_id,
            "status": "Under Review",
            **req.model_dump()
        }
        self.models[model_id] = entry
        return entry

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self.models.get(model_id)

    def execute_audit(self, model_id: str) -> Dict[str, Any]:
        model_meta = self.get_model(model_id) or {
            "id": model_id,
            "name": "LoanApproval_v1",
            "version": "1.0"
        }

        # Standalone Phase 1 mock fixtures matching Member 3 & 4 contracts
        performance_data = {
            "accuracy": 0.91,
            "precision": 0.89,
            "recall": 0.88,
            "f1": 0.88,
            "roc_auc": 0.93,
            "confusion_matrix": {"tn": 420, "fp": 45, "fn": 55, "tp": 480}
        }
        
        fairness_data = {
            "sensitive_attribute": "gender",
            "selection_rates": {"Male": 0.78, "Female": 0.52},
            "demographic_parity_gap": 0.26,
            "disparate_impact_ratio": 0.67,
            "tpr_gap": 0.17,
            "status": "FAIL"
        }

        explainability_data = {
            "status": "PASS",
            "global_features": [
                {"feature": "credit_score", "importance": 0.38},
                {"feature": "income", "importance": 0.28},
                {"feature": "debt_ratio", "importance": 0.18},
                {"feature": "employment_years", "importance": 0.11},
                {"feature": "age", "importance": 0.05}
            ],
            "local_explanation": [
                {"feature": "credit_score", "value": 720, "contribution": 0.42},
                {"feature": "debt_ratio", "value": 0.45, "contribution": -0.15},
                {"feature": "income", "value": 65000, "contribution": 0.21}
            ]
        }

        drift_data = {
            "status": "NOT_RUN",
            "features": []
        }

        audit_payload = {
            "model": model_meta,
            "performance": performance_data,
            "fairness": fairness_data,
            "explainability": explainability_data,
            "drift": drift_data
        }

        verdict, reasons = evaluate_policies(audit_payload, self.policies)
        
        audit_payload["decision"] = {
            "status": verdict,
            "reasons": reasons
        }

        audit_id = f"audit-{uuid.uuid4().hex[:6]}"
        self.audits[audit_id] = audit_payload
        self.audits[model_id] = audit_payload  # Quick lookup for demo

        # Update model deployment status based on decision
        if model_id in self.models:
            self.models[model_id]["status"] = "Blocked" if verdict == "BLOCK" else "Eligible"

        return audit_payload

    def get_audit(self, identifier: str) -> Optional[Dict[str, Any]]:
        return self.audits.get(identifier)

    def record_review(self, audit_id: str, reviewer: str, decision: str, reason: str):
        record = {
            "audit_id": audit_id,
            "reviewer": reviewer,
            "decision": decision,
            "reason": reason
        }
        self.reviews.setdefault(audit_id, []).append(record)
        return record

audit_store = AuditStore()