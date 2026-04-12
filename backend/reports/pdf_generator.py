import io
import re
import uuid
import logging
import pandas as pd
from pathlib import Path
from core.config import REPORTS_DIR

logger = logging.getLogger("ai_analyst")

def generate_pdf_report(query: str, intent: str, result: str, insight: str, fig_dict: dict | None) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate,
                                     Spacer)

    report_id = str(uuid.uuid4())[:8]
    pdf_path = REPORTS_DIR / f"report_{report_id}.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                  fontSize=20, textColor=colors.HexColor("#1e40af"),
                                  spaceAfter=12)
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"],
                               fontSize=13, textColor=colors.HexColor("#1e40af"),
                               spaceBefore=16, spaceAfter=8)
    body_style = ParagraphStyle("body", parent=styles["Normal"],
                                 fontSize=10, leading=16, spaceAfter=8)
    mono_style = ParagraphStyle("mono", parent=styles["Code"],
                                 fontSize=9, backColor=colors.HexColor("#f1f5f9"),
                                 borderPadding=8, leading=14)

    story = []

    # Header
    story.append(Paragraph("🤖 AI Data Analyst — Report", title_style))
    story.append(Paragraph(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 0.3*cm))

    # Query
    story.append(Paragraph("Query", h2_style))
    story.append(Paragraph(query, body_style))

    # Intent
    story.append(Paragraph("Analysis Type", h2_style))
    story.append(Paragraph(intent.upper() if intent else "GENERAL", body_style))

    # Result
    story.append(Paragraph("Result", h2_style))
    # Clean markdown for PDF
    clean_result = re.sub(r"\*\*(.+?)\*\*", r"\1", str(result))
    story.append(Paragraph(clean_result, mono_style))

    # Insight
    story.append(Paragraph("Key Insight", h2_style))
    clean_insight = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", str(insight))
    story.append(Paragraph(clean_insight, body_style))

    # Chart
    if fig_dict:
        try:
            import plotly.io as pio
            import plotly.graph_objects as go
            fig_obj = go.Figure(fig_dict)
            img_bytes = pio.to_image(fig_obj, format="png", width=700, height=400)
            img_buf = io.BytesIO(img_bytes)
            story.append(Paragraph("Chart", h2_style))
            story.append(Image(img_buf, width=16*cm, height=9*cm))
        except Exception as e:
            logger.warning("Chart embedding failed: %s", e)

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("─── Powered by Autonomous AI Data Analyst ───",
                           ParagraphStyle("footer", parent=styles["Normal"],
                                          fontSize=8, textColor=colors.gray, alignment=1)))

    doc.build(story)
    return pdf_path
