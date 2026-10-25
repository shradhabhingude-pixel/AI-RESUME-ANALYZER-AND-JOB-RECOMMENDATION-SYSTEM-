"""Create a downloadable PDF analysis report in memory."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _safe(value: object) -> str:
    """Escape content and replace characters unsupported by built-in PDF fonts."""
    text = str(value).encode("latin-1", "replace").decode("latin-1")
    return escape(text).replace("\n", "<br/>")


def create_analysis_pdf(report: dict, cleaned_resume_text: str) -> bytes:
    """Return a concise PDF containing match results and cleaned text appendix."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.65 * inch,
                            leftMargin=0.65 * inch, topMargin=0.65 * inch, bottomMargin=0.65 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER,
                              textColor=colors.HexColor("#1F4E79"), spaceAfter=14))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=11))
    story = [Paragraph("AI Resume Analysis Report", styles["ReportTitle"]),
             Paragraph(f"Resume file: {_safe(report.get('resume_file', 'Uploaded resume'))}", styles["BodyText"]),
             Paragraph(f"Target role: {_safe(report.get('target_role', 'Not selected'))}", styles["BodyText"]),
             Paragraph(f"Match estimate: {_safe(report.get('match_score_percent', 0))}%", styles["Heading2"]),
             Spacer(1, 8)]

    story.append(Paragraph("Recommended roles", styles["Heading2"]))
    recs = report.get("recommended_roles", [])
    role_rows = [["Rank", "Role", "Match"]]
    role_rows.extend([[str(i), _safe(item.get("role", "")), f"{item.get('score', 0)}%"]
                      for i, item in enumerate(recs, 1)])
    table = Table(role_rows, colWidths=[0.65 * inch, 4.6 * inch, 1.0 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B7C9D6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6F9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 10)])

    for heading, key in [("Skills found", "skills_found"), ("Required skills found for target role", "required_skills_found"), ("Missing skill keywords", "missing_skills")]:
        values = report.get(key, [])
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Paragraph(_safe(", ".join(values) if values else "None detected"), styles["BodyText"]))

    limited = report.get("limited_evidence_skills", [])
    story.append(Paragraph("Skills needing stronger examples", styles["Heading2"]))
    story.append(Paragraph(_safe(", ".join(limited) if limited else "None flagged"), styles["BodyText"]))
    story.append(Paragraph("Detected resume sections", styles["Heading2"]))
    for section_name, section_text in report.get("resume_sections", {}).items():
        story.append(Paragraph(f"<b>{_safe(section_name.title())}:</b> {_safe(section_text)}", styles["Small"]))

    story.append(Paragraph("Suggested learning roadmap", styles["Heading2"]))
    roadmap = report.get("roadmap", [])
    if roadmap:
        for item in roadmap:
            story.append(Paragraph(f"<b>{_safe(item.get('week', ''))}:</b> {_safe(item.get('topic', ''))}", styles["BodyText"]))
    else:
        story.append(Paragraph("No roadmap topics available.", styles["BodyText"]))

    story.extend([Spacer(1, 8), Paragraph("Important note", styles["Heading2"]),
                  Paragraph(_safe(report.get("notice", "Educational estimate only; not a hiring decision.")), styles["BodyText"]),
                  Paragraph("A missing keyword does not prove that a candidate lacks the underlying skill. Review this guidance manually.", styles["Small"]),
                  Spacer(1, 12), Paragraph("Appendix: cleaned resume text", styles["Heading2"]),
                  Paragraph("Text is lowercased, whitespace is normalized, and paragraph breaks are retained. Cleaning does not correct spelling or summarize content.", styles["Small"]),
                  Spacer(1, 5)])
    if cleaned_resume_text:
        for chunk in [cleaned_resume_text[i:i + 2500] for i in range(0, len(cleaned_resume_text), 2500)]:
            story.append(Paragraph(_safe(chunk), styles["Small"]))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No readable text extracted.", styles["Small"]))

    doc.build(story)
    return buffer.getvalue()
