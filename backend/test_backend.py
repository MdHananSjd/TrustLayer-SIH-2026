import os
import shutil
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.audit_service import audit_store
from app.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_uploads():
    # Setup: ensure upload directory is clean
    if settings.UPLOAD_DIR.exists():
        shutil.rmtree(settings.UPLOAD_DIR)
    yield
    # Teardown: cleanup upload directory
    if settings.UPLOAD_DIR.exists():
        shutil.rmtree(settings.UPLOAD_DIR)

def test_model_registration():
    payload = {
        "name": "Custom Credit Classifier",
        "version": "1.0",
        "owner": "Risk Division",
        "target": "approved",
        "sensitive_attributes": ["gender", "age"]
    }
    response = client.post("/api/v1/models", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "Under Review"
    assert data["name"] == "Custom Credit Classifier"

def test_artifact_upload_validation_and_storage():
    # 1. Register a model
    payload = {
        "name": "Upload Test Model",
        "version": "1.0",
        "owner": "Audit Team",
        "target": "approved",
        "sensitive_attributes": ["gender"]
    }
    reg_resp = client.post("/api/v1/models", json=payload)
    model_id = reg_resp.json()["id"]

    # 2. Test malformed CSV upload (invalid format)
    files = {
        "model_file": ("model.pkl", b"dummy_model_bytes", "application/octet-stream"),
        "eval_csv": ("eval.csv", b"not,a,csv\n1,2", "text/csv")
    }
    upload_resp = client.post(f"/api/v1/models/{model_id}/artifacts", files=files)
    assert upload_resp.status_code == 400
    assert "Evaluation CSV is missing required columns" in upload_resp.json()["detail"]

    # 3. Test correct CSV upload with required columns (approved, gender)
    csv_data = b"age,gender,income,credit_score,approved\n30,Female,50000,700,1\n40,Male,80000,750,0"
    files = {
        "model_file": ("model.pkl", b"dummy_model_bytes", "application/octet-stream"),
        "eval_csv": ("eval.csv", csv_data, "text/csv")
    }
    upload_resp = client.post(f"/api/v1/models/{model_id}/artifacts", files=files)
    assert upload_resp.status_code == 200
    assert upload_resp.json()["status"] == "Artifacts stored"

    # Verify files exist on disk
    model_path = settings.UPLOAD_DIR / model_id / "model.pkl"
    csv_path = settings.UPLOAD_DIR / model_id / "eval.csv"
    assert model_path.exists()
    assert csv_path.exists()

def test_deterministic_audit_flows():
    # Test Biased Model Audit Flow (model-loan-01)
    response = client.post("/api/v1/models/model-loan-01/audit")
    assert response.status_code == 200
    data = response.json()
    assert data["decision"]["status"] == "BLOCK"
    assert len(data["decision"]["reasons"]) > 0
    assert data["performance"]["accuracy"] == 0.874
    assert data["fairness"]["demographic_parity_gap"] == 0.328
    assert data["fairness"]["status"] == "FAIL"

    # Test Improved Model Audit Flow (model-loan-02)
    response2 = client.post("/api/v1/models/model-loan-02/audit")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["decision"]["status"] == "WARNING"
    assert data2["performance"]["accuracy"] == 0.858
    assert data2["fairness"]["demographic_parity_gap"] == 0.040
    assert data2["fairness"]["status"] == "PASS"

def test_human_review_promotions():
    audit_id = "audit-demo-123"
    
    # Pre-register audit for testing review
    audit_store.audits[audit_id] = {
        "model": {
            "id": "model-loan-01",
            "name": "Loan Approval Classifier"
        },
        "decision": {"status": "BLOCK"}
    }
    
    # Submit human override
    payload = {
        "reviewer": "Alice Audit",
        "decision": "OVERRIDDEN",
        "reason": "Business requirement override based on manual collateral verification."
    }
    review_resp = client.post(f"/api/v1/audits/{audit_id}/review", json=payload)
    assert review_resp.status_code == 200
    
    # Assert model status updated
    model = audit_store.get_model("model-loan-01")
    assert model["status"] == "Overridden (Eligible)"

def test_pdf_report_generation():
    # Trigger audit to generate a result
    client.post("/api/v1/models/model-loan-01/audit")
    
    # Retrieve PDF report
    response = client.get("/api/v1/audits/model-loan-01/report")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    pdf_bytes = response.content
    assert pdf_bytes.startswith(b"%PDF")
