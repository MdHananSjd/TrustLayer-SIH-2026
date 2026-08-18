import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from typing import Dict, Any

def generate_pdf_report(audit_data: Dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title & Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "TrustLayer — AI Governance Audit Report")
    
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.gray)
    p.drawString(50, height - 68, "Smart India Hackathon 2026 | Responsible AI Evidence Support")
    p.setStrokeColor(colors.lightgrey)
    p.line(50, height - 75, width - 50, height - 75)

    # Model Metadata Section
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 100, "1. Model Metadata")
    
    model = audit_data.get("model", {})
    p.setFont("Helvetica", 10)
    p.drawString(60, height - 120, f"Model Name: {model.get('name', 'N/A')}")
    p.drawString(60, height - 135, f"Version: {model.get('version', 'N/A')}")
    p.drawString(60, height - 150, f"Model ID: {model.get('id', 'N/A')}")

    # Decision Summary
    decision = audit_data.get("decision", {})
    verdict = decision.get("status", "UNKNOWN")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 180, "2. Governance Policy Decision")

    if verdict == "BLOCK":
        p.setFillColor(colors.red)
    elif verdict == "WARNING":
        p.setFillColor(colors.orange)
    else:
        p.setFillColor(colors.green)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(60, height - 200, f"VERDICT: {verdict}")

    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    y = height - 220
    for reason in decision.get("reasons", []):
        p.drawString(70, y, f"• {reason}")
        y -= 15

    # Performance & Fairness Highlights
    y -= 15
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "3. Core Governance Metrics")
    y -= 20
    
    perf = audit_data.get("performance", {})
    fair = audit_data.get("fairness", {})
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Accuracy: {perf.get('accuracy', 'N/A')}  |  F1-Score: {perf.get('f1', 'N/A')}  |  ROC-AUC: {perf.get('roc_auc', 'N/A')}")
    y -= 15
    p.drawString(60, y, f"Demographic Parity Gap: {fair.get('demographic_parity_gap', 'N/A')}  |  Disparate Impact: {fair.get('disparate_impact_ratio', 'N/A')}")

    # Footer Disclaimer
    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(colors.gray)
    p.drawString(50, 40, "Disclaimer: TrustLayer surfaces evidence support and review signals. It does not certify legal compliance.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer