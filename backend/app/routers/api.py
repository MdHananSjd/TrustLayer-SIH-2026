from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from app.models.schemas import (
    ModelRegisterRequest,
    ReviewRequest,
    PolicyRule,
    AuditResultResponse
)
from app.services.audit_service import audit_store
from app.services.report_generator import generate_pdf_report

router = APIRouter()

@router.get("/models")
def list_models():
    return audit_store.list_models()

@router.post("/models")
def register_model(payload: ModelRegisterRequest):
    return audit_store.register_model(payload)

@router.post("/models/{model_id}/artifacts")
async def upload_artifacts(
    model_id: str,
    model_file: UploadFile = File(...),
    eval_csv: UploadFile = File(...)
):
    model = audit_store.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        model_content = await model_file.read()
        csv_content = await eval_csv.read()
        
        return audit_store.store_artifacts(
            model_id=model_id,
            model_filename=model_file.filename,
            model_content=model_content,
            csv_filename=eval_csv.filename,
            csv_content=csv_content
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/models/{model_id}/audit", response_model=AuditResultResponse)
def run_audit(model_id: str):
    return audit_store.execute_audit(model_id)

@router.get("/models/{model_id}/audits/{audit_id}")
def get_audit(model_id: str, audit_id: str):
    result = audit_store.get_audit(audit_id) or audit_store.get_audit(model_id)
    if not result:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return result

@router.post("/audits/{audit_id}/review")
def record_review(audit_id: str, payload: ReviewRequest):
    return audit_store.record_review(
        audit_id=audit_id,
        reviewer=payload.reviewer,
        decision=payload.decision,
        reason=payload.reason
    )

@router.post("/policies")
def set_policies(payload: List[PolicyRule]):
    audit_store.policies = payload
    return {"status": "Policies updated", "rules_count": len(payload)}

@router.get("/audits/{audit_id}/report")
def get_report(audit_id: str):
    audit_data = audit_store.get_audit(audit_id)
    if not audit_data:
        # Fallback to executing the audit on the requested ID
        audit_data = audit_store.execute_audit(audit_id)
        
    reviews = audit_store.reviews.get(audit_id, [])
    audit_copy = dict(audit_data)
    audit_copy["reviews"] = reviews
        
    pdf_buffer = generate_pdf_report(audit_copy)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=TrustLayer_Audit_{audit_id}.pdf"}
    )