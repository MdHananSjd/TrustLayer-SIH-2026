import uuid
import io
import os
import sys
import pandas as pd
from typing import Dict, Any, List, Optional

# Append workspace root to path to import governance_engine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from governance_engine.audit_runner import audit_model_from_files
from app.models.schemas import ModelRegisterRequest, PolicyRule
from app.services.policy_engine import evaluate_policies, DEFAULT_POLICIES
from app.config import settings

class AuditStore:
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {
            "model-loan-01": {
                "id": "model-loan-01",
                "name": "Loan Approval Classifier",
                "version": "1.0",
                "owner": "Risk Assessment Team",
                "target": "approved",
                "sensitive_attributes": ["gender", "age"],
                "status": "Under Review",
                "model_filename": "biased_model.pkl",
                "csv_filename": "evaluation.csv"
            },
            "model-loan-02": {
                "id": "model-loan-02",
                "name": "Loan Approval Classifier (Mitigated)",
                "version": "2.0",
                "owner": "Data Team",
                "target": "approved",
                "sensitive_attributes": ["gender", "age"],
                "status": "Under Review",
                "model_filename": "improved_model.pkl",
                "csv_filename": "evaluation.csv"
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

    def list_models(self) -> List[Dict[str, Any]]:
        return list(self.models.values())

    def store_artifacts(
        self,
        model_id: str,
        model_filename: str,
        model_content: bytes,
        csv_filename: str,
        csv_content: bytes
    ) -> Dict[str, Any]:
        model_entry = self.get_model(model_id)
        if not model_entry:
            raise ValueError("Model not found")

        # 1. Parse and validate CSV schema
        try:
            df = pd.read_csv(io.BytesIO(csv_content))
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

        if df.empty:
            raise ValueError("Evaluation dataset is empty.")

        # Auto-detect target column if the specified one is not in the columns
        target = model_entry.get("target", "approved")
        if target not in df.columns:
            common_targets = ["approved", "target", "label", "y", "class", "outcome"]
            found_target = False
            for t in common_targets:
                for col in df.columns:
                    if col.lower() == t:
                        target = col
                        found_target = True
                        break
                if found_target:
                    break
            
            if not found_target:
                raise ValueError(f"Evaluation CSV is missing required columns: target column '{target}' (or any common target column name like 'label', 'target', 'y') was not found")
                
            model_entry["target"] = target

        # Auto-detect sensitive attributes
        sensitive_cols = model_entry.get("sensitive_attributes", ["gender"])
        active_sensitive = []
        for col in sensitive_cols:
            if col in df.columns:
                active_sensitive.append(col)
                
        if not active_sensitive:
            common_attributes = ["gender", "sex", "race", "age", "ethnicity"]
            for attr in common_attributes:
                for col in df.columns:
                    if col.lower() == attr and col != target:
                        active_sensitive.append(col)
                        break
                if active_sensitive:
                    break
                    
        if not active_sensitive:
            raise ValueError(f"Evaluation CSV is missing required columns: sensitive attribute column '{sensitive_cols[0]}' (or any common sensitive column name like 'sex', 'race', 'age') was not found")
                    
        model_entry["sensitive_attributes"] = active_sensitive

        # 2. Write files to local storage under uploads/{model_id}
        model_dir = settings.UPLOAD_DIR / model_id
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / model_filename
        csv_path = model_dir / csv_filename

        with open(model_path, "wb") as f:
            f.write(model_content)

        with open(csv_path, "wb") as f:
            f.write(csv_content)

        # 3. Update database model record
        model_entry["model_path"] = str(model_path)
        model_entry["csv_path"] = str(csv_path)
        model_entry["model_filename"] = model_filename
        model_entry["csv_filename"] = csv_filename

        return {
            "model_id": model_id,
            "model_filename": model_filename,
            "csv_filename": csv_filename,
            "status": "Artifacts stored"
        }

    def execute_audit(self, model_id: str) -> Dict[str, Any]:
        model_meta = self.get_model(model_id)
        if not model_meta:
            # Fallback mock setup if model ID doesn't exist yet
            model_meta = {
                "id": model_id,
                "name": "LoanApproval_v1",
                "version": "1.0",
                "owner": "Risk Assessment Team",
                "target": "approved",
                "sensitive_attributes": ["gender"],
                "model_filename": "biased_model.pkl"
            }

        # 1. Resolve paths for model binary and evaluation CSV
        model_path = model_meta.get("model_path")
        if not model_path:
            filename = model_meta.get("model_filename")
            if not filename:
                filename = "biased_model.pkl" if "loan-01" in model_id.lower() or "v1" in model_meta.get("name", "").lower() else "improved_model.pkl"
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../demo-models", filename))
        else:
            model_path = os.path.abspath(model_path)
            
        csv_path = model_meta.get("csv_path")
        if not csv_path:
            filename = model_meta.get("csv_filename", "evaluation.csv")
            csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../demo-assets", filename))
        else:
            csv_path = os.path.abspath(csv_path)

        production_csv_path = model_meta.get("production_csv_path")
        if not production_csv_path and model_id in ("model-loan-01", "model-loan-02"):
            production_csv_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../demo-assets/production_shifted_01.csv")
            )

        # 2. Dynamically build metadata config dictionary
        target = model_meta.get("target", "approved")
        sensitive_attributes = model_meta.get("sensitive_attributes", ["gender"])
        
        feature_names = []
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                feature_names = [col for col in df.columns if col != target]
            except Exception:
                pass
                
        if not feature_names:
            feature_names = ["age", "gender", "income", "credit_score", "debt_ratio", "employment_years", "region"]

        mapped_meta = {
            "name": model_meta.get("name", "Model"),
            "version": model_meta.get("version", "1.0"),
            "target": target,
            "positive_label": 1,
            "sensitive_attributes": sensitive_attributes,
            "feature_names": feature_names
        }

        # 3. Create temp metadata JSON file and execute audit_runner
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(mapped_meta, f)
            temp_meta_path = f.name
            
        try:
            res = audit_model_from_files(
                model_path=model_path,
                evaluation_csv_path=csv_path,
                metadata_path=temp_meta_path,
                production_csv_path=production_csv_path,
            )
        except Exception as e:
            raise ValueError(f"Orchestrated audit execution failed: {str(e)}")
        finally:
            if os.path.exists(temp_meta_path):
                os.remove(temp_meta_path)

        # 4. Map engine's evaluation results to schema-compliant response structure
        engine_perf = res.get("performance", {})
        cm = engine_perf.get("confusion_matrix", [[0, 0], [0, 0]])
        confusion_matrix_dict = {
            "tn": int(cm[0][0]),
            "fp": int(cm[0][1]),
            "fn": int(cm[1][0]),
            "tp": int(cm[1][1])
        }
        
        performance_data = {
            "accuracy": round(float(engine_perf.get("accuracy", 0.0)), 3),
            "precision": round(float(engine_perf.get("precision", 0.0)), 3),
            "recall": round(float(engine_perf.get("recall", 0.0)), 3),
            "f1": round(float(engine_perf.get("f1", 0.0)), 3),
            "roc_auc": round(float(engine_perf.get("roc_auc")), 3) if engine_perf.get("roc_auc") is not None else None,
            "confusion_matrix": confusion_matrix_dict
        }

        engine_fair = res.get("fairness", {})
        sensitive_attr = engine_fair.get("sensitive_attribute", sensitive_attributes[0])
        
        selection_rates = {}
        for group_name, group_info in engine_fair.get("groups", {}).items():
            selection_rates[str(group_name)] = round(float(group_info.get("selection_rate", 0.0)), 3)
            
        demographic_parity_gap = round(float(engine_fair.get("demographic_parity_gap", 0.0)), 3)
        disparate_impact_ratio = round(float(engine_fair.get("disparate_impact_ratio", 1.0)), 3)
        tpr_gap = round(float(engine_fair.get("tpr_gap", 0.0)), 3)
        
        fairness_status = "FAIL" if (demographic_parity_gap > 0.20 or disparate_impact_ratio < 0.75) else "PASS"
        
        fairness_data = {
            "sensitive_attribute": sensitive_attr,
            "selection_rates": selection_rates,
            "demographic_parity_gap": demographic_parity_gap,
            "disparate_impact_ratio": disparate_impact_ratio,
            "tpr_gap": tpr_gap,
            "status": fairness_status
        }

        engine_explain = res.get("explainability", {})
        explainability_data = {
            "status": engine_explain.get("status", "FAIL"),
            "global_features": engine_explain.get("global_features", []),
            "local_explanation": engine_explain.get("local_explanation", []),
        }

        engine_drift = res.get("drift", {"status": "NOT_RUN", "features": []})
        drift_data = {
            "status": engine_drift.get("status", "NOT_RUN"),
            "features": engine_drift.get("features", []),
        }

        merged_model = {
            **res.get("model", {}),
            **{k: v for k, v in model_meta.items() if k not in res.get("model", {})},
            "id": model_id,
        }

        audit_id = f"audit-{uuid.uuid4().hex[:6]}"

        audit_payload = {
            "audit_id": audit_id,
            "model": merged_model,
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
        
        # Update the model status if we find an audit matching this ID
        audit_data = self.get_audit(audit_id)
        if audit_data:
            model_id = audit_data.get("model", {}).get("id")
            if model_id and model_id in self.models:
                if decision == "APPROVED":
                    self.models[model_id]["status"] = "Approved"
                elif decision == "REJECTED":
                    self.models[model_id]["status"] = "Rejected"
                elif decision == "OVERRIDDEN":
                    self.models[model_id]["status"] = "Overridden (Eligible)"
        return record

audit_store = AuditStore()