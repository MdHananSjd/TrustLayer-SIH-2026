import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    A canvas that enables dynamic two-pass page numbering 
    and draws headers/footers consistently on all pages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1e293b"))
            self.drawString(54, 750, "TRUSTLAYER — AI GOVERNANCE REPORT")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(612 - 54, 750, "Responsible AI Evidence Support")
            
            # Header line
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)
            
        # Footer (On all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 55, 612 - 54, 55)
        
        self.setFont("Helvetica-Oblique", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 42, "Disclaimer: TrustLayer surfaces evidence support and review signals. It does not certify legal compliance.")
        
        self.setFont("Helvetica", 8)
        self.drawRightString(612 - 54, 42, f"Page {self._pageNumber} of {page_count}")
        
        self.restoreState()

def generate_pdf_report(audit_data: Dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO()
    
    # Establish document template with 1 inch top/bottom and 0.75 inch side margins
    # Total width = 612, usable width = 612 - 54*2 = 504
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette Styling
    c_primary = colors.HexColor("#1e293b")  # Slate Dark
    c_secondary = colors.HexColor("#64748b")  # Slate Light
    c_border = colors.HexColor("#e2e8f0")
    c_bg_light = colors.HexColor("#f8fafc")
    
    # Status Colors
    c_pass = colors.HexColor("#16a34a")
    c_block = colors.HexColor("#dc2626")
    c_warning = colors.HexColor("#d97706")
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=c_secondary,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBodyText',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=c_primary
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    story = []

    # Safe Extractors with Fallbacks
    model = audit_data.get("model", {})
    performance = audit_data.get("performance", {})
    fairness = audit_data.get("fairness", {})
    explainability = audit_data.get("explainability", {})
    drift = audit_data.get("drift", {})
    decision = audit_data.get("decision", {})
    reviews = audit_data.get("reviews", [])

    # ==========================================
    # PAGE 1: TITLE, METADATA & POLICY DECISION
    # ==========================================
    
    # 1. Document Header
    story.append(Paragraph("TrustLayer — AI Governance Audit Report", title_style))
    story.append(Paragraph("Smart India Hackathon 2026 | Continuous Responsible AI Assurance & Policy Enforcement", subtitle_style))
    
    # 2. Model Metadata Section
    story.append(Paragraph("1. Model Card & Metadata", h1_style))
    
    features_list = model.get("feature_names", [])
    features_str = ", ".join(features_list) if isinstance(features_list, list) else str(features_list)
    sens_list = model.get("sensitive_attributes", [])
    sens_str = ", ".join(sens_list) if isinstance(sens_list, list) else str(sens_list)
    
    metadata_data = [
        [
            Paragraph("Model Name:", bold_body_style), Paragraph(model.get("name", "N/A"), body_style),
            Paragraph("Domain:", bold_body_style), Paragraph(model.get("domain", "N/A"), body_style)
        ],
        [
            Paragraph("Version / ID:", bold_body_style), Paragraph(f"{model.get('version', 'N/A')} ({model.get('id', 'N/A')})", body_style),
            Paragraph("Target Variable:", bold_body_style), Paragraph(model.get("target", "N/A"), body_style)
        ],
        [
            Paragraph("Owner / Team:", bold_body_style), Paragraph(model.get("owner", "N/A"), body_style),
            Paragraph("Sensitive Fields:", bold_body_style), Paragraph(sens_str, body_style)
        ],
        [
            Paragraph("Features:", bold_body_style), Paragraph(features_str, body_style),
            Paragraph("", body_style), Paragraph("", body_style)
        ]
    ]
    
    # Usable width = 504. Column widths: 90, 162, 90, 162
    metadata_table = Table(metadata_data, colWidths=[90, 162, 90, 162])
    metadata_table.setStyle(TableStyle([
        ('SPAN', (1, 3), (3, 3)), # Span the long feature list
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 15))
    
    # 3. Governance Policy Decision
    story.append(Paragraph("2. Policy Engine Verdict", h1_style))
    
    verdict = decision.get("status", "UNKNOWN").upper()
    v_color = c_pass
    v_bg = colors.HexColor("#f0fdf4")
    if verdict == "BLOCK":
        v_color = c_block
        v_bg = colors.HexColor("#fef2f2")
    elif verdict == "WARNING":
        v_color = c_warning
        v_bg = colors.HexColor("#fffbeb")
        
    verdict_label_style = ParagraphStyle(
        'VerdictLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=v_color
    )
    
    decision_box_content = [
        [Paragraph(f"POLICY VERDICT: {verdict}", verdict_label_style)],
        [Spacer(1, 5)]
    ]
    
    reasons = decision.get("reasons", [])
    if reasons:
        for reason in reasons:
            decision_box_content.append([Paragraph(f"• {reason}", bullet_style)])
    else:
        decision_box_content.append([Paragraph("All organizational governance policies passed.", body_style)])
        
    decision_table = Table(decision_box_content, colWidths=[496])
    decision_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), v_bg),
        ('BOX', (0, 0), (-1, -1), 1, v_color),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(decision_table)
    story.append(Spacer(1, 15))
    
    # 4. Human Review Status
    story.append(Paragraph("3. Human Review & Promotions", h1_style))
    
    if reviews:
        review_data = [
            [
                Paragraph("Reviewer", bold_body_style), 
                Paragraph("Decision", bold_body_style), 
                Paragraph("Justification / Comments", bold_body_style)
            ]
        ]
        for r in reviews:
            dec = r.get("decision", "N/A").upper()
            d_color = c_secondary
            if dec == "APPROVED":
                d_color = c_pass
            elif dec == "REJECTED":
                d_color = c_block
            elif dec in ["OVERRIDDEN", "OVERRIDE"]:
                d_color = c_warning
                
            dec_style = ParagraphStyle(
                'DecText',
                parent=body_style,
                fontName='Helvetica-Bold',
                textColor=d_color
            )
            
            review_data.append([
                Paragraph(r.get("reviewer", "N/A"), body_style),
                Paragraph(dec, dec_style),
                Paragraph(r.get("reason", "No justification provided."), body_style)
            ])
            
        review_table = Table(review_data, colWidths=[120, 100, 284])
        review_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
            ('LINEBELOW', (0, 0), (-1, 0), 1, c_primary),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(review_table)
    else:
        review_box_content = [
            [Paragraph("STATUS: PENDING REVIEW", ParagraphStyle('PendLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=c_warning))],
            [Spacer(1, 4)],
            [Paragraph("This model is currently undergoing continuous validation. Promotion to the production cluster remains BLOCKED until a designated human auditor submits a signed override/approval.", body_style)]
        ]
        review_table = Table(review_box_content, colWidths=[496])
        review_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(review_table)

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: METRICS & STANDARDS MAPPING
    # ==========================================
    
    # 5. Core Performance and Fairness Metrics
    story.append(Paragraph("4. Core Audit Metrics Summary", h1_style))
    story.append(Spacer(1, 4))
    
    # 5a. Performance Metrics Table
    story.append(Paragraph("A. Predictive Performance", ParagraphStyle('SubSec', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, spaceAfter=4)))
    
    perf_matrix = performance.get("confusion_matrix", {})
    if isinstance(perf_matrix, dict):
        matrix_str = f"TN: {perf_matrix.get('tn', 0)} | FP: {perf_matrix.get('fp', 0)} | FN: {perf_matrix.get('fn', 0)} | TP: {perf_matrix.get('tp', 0)}"
    else:
        matrix_str = str(perf_matrix)
        
    perf_data = [
        [
            Paragraph("Accuracy", bold_body_style), Paragraph(f"{performance.get('accuracy', 0.0):.3f}", body_style),
            Paragraph("Precision", bold_body_style), Paragraph(f"{performance.get('precision', 0.0):.3f}", body_style)
        ],
        [
            Paragraph("Recall (TPR)", bold_body_style), Paragraph(f"{performance.get('recall', 0.0):.3f}", body_style),
            Paragraph("F1-Score", bold_body_style), Paragraph(f"{performance.get('f1', 0.0):.3f}", body_style)
        ],
        [
            Paragraph("ROC-AUC", bold_body_style), Paragraph(f"{performance.get('roc_auc', 0.0):.3f}" if performance.get('roc_auc') is not None else "N/A", body_style),
            Paragraph("Confusion Matrix", bold_body_style), Paragraph(matrix_str, body_style)
        ]
    ]
    perf_table = Table(perf_data, colWidths=[90, 162, 90, 162])
    perf_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 10))
    
    # 5b. Fairness Metrics Table
    story.append(Paragraph("B. Demographic Group Fairness", ParagraphStyle('SubSec2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=c_primary, spaceAfter=4)))
    
    selection_dict = fairness.get("selection_rates", {})
    selection_str = ", ".join([f"{k}: {v:.1%}" for k, v in selection_dict.items()]) if isinstance(selection_dict, dict) else str(selection_dict)
    
    fair_data = [
        [
            Paragraph("Sensitive Attribute", bold_body_style), Paragraph(fairness.get("sensitive_attribute", "N/A"), body_style),
            Paragraph("Demographic Parity Gap", bold_body_style), Paragraph(f"{fairness.get('demographic_parity_gap', 0.0):.3f}", body_style)
        ],
        [
            Paragraph("Disparate Impact Ratio", bold_body_style), Paragraph(f"{fairness.get('disparate_impact_ratio', 0.0):.3f}", body_style),
            Paragraph("Equal Opportunity Gap (TPR)", bold_body_style), Paragraph(f"{fairness.get('tpr_gap', 0.0):.3f}" if fairness.get('tpr_gap') is not None else "N/A", body_style)
        ],
        [
            Paragraph("Selection Rates", bold_body_style), Paragraph(selection_str, body_style),
            Paragraph("Fairness Status", bold_body_style), Paragraph(fairness.get("status", "N/A"), ParagraphStyle('StText', parent=body_style, fontName='Helvetica-Bold', textColor=c_pass if fairness.get("status") == "PASS" else c_block))
        ]
    ]
    fair_table = Table(fair_data, colWidths=[90, 162, 110, 142])
    fair_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, c_border),
    ]))
    story.append(fair_table)
    story.append(Spacer(1, 15))

    # 6. Explainability (SHAP global feature attribution)
    story.append(Paragraph("5. Explainability & Feature Importances (SHAP)", h1_style))
    story.append(Spacer(1, 2))
    
    shap_features = explainability.get("global_features", [])
    if shap_features:
        shap_headers = [Paragraph("Rank", bold_body_style), Paragraph("Feature Name", bold_body_style), Paragraph("SHAP Importance (Relative)", bold_body_style)]
        shap_rows = [shap_headers]
        
        for idx, feat in enumerate(shap_features[:5]):  # limit to top 5
            imp_val = feat.get("importance", 0.0)
            bar_width = int(imp_val * 25)
            visual_bar = "■" * bar_width + "□" * (25 - bar_width)
            
            shap_rows.append([
                Paragraph(str(idx + 1), body_style),
                Paragraph(feat.get("feature", "N/A"), body_style),
                Paragraph(f"{imp_val:.2f}  {visual_bar}", ParagraphStyle('CodeFont', parent=body_style, fontName='Courier', fontSize=7.5))
            ])
            
        shap_table = Table(shap_rows, colWidths=[40, 150, 314])
        shap_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
            ('LINEBELOW', (0, 0), (-1, 0), 1, c_primary),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(shap_table)
    else:
        story.append(Paragraph("Explainability metrics not computed.", body_style))
    story.append(Spacer(1, 15))

    # 7. Alignment to Standards
    story.append(Paragraph("6. Compliance & Standards Alignment Framework", h1_style))
    story.append(Spacer(1, 2))
    
    compliance_data = [
        [
            Paragraph("Standard Framework", bold_body_style), 
            Paragraph("Mapped TrustLayer Evidence Support", bold_body_style)
        ],
        [
            Paragraph("NIST AI Risk Management Framework (AI RMF 1.0)", ParagraphStyle('BoldB', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("Audit tracks 'Fair' and 'Explainable' pillars. Disparity evaluations (selection rates, TPR gaps) map directly to RMF Measure 1.2 & 2.1.", body_style)
        ],
        [
            Paragraph("ISO/IEC 42001:2023 (AI Management System)", ParagraphStyle('BoldB', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("Continuous verification logs provide documented evidence of system control metrics (Annex A.3 - Impact Assessment).", body_style)
        ],
        [
            Paragraph("Regulatory Directives (EU AI Act / India DPDP Act)", ParagraphStyle('BoldB', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("Preserves immutable model card artifacts and human sign-off history to demonstrate automated decision governance accountability.", body_style)
        ]
    ]
    compliance_table = Table(compliance_data, colWidths=[160, 344])
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('LINEBELOW', (0, 0), (-1, 0), 1, c_primary),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(compliance_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    buffer.seek(0)
    return buffer