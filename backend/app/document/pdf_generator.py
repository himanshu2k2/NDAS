from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.templates.kidney_affidavit_template import AffidavitContext, build_sections

_W, _H = A4
_MARGIN = 2.54 * cm


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "AffTitle",
        parent=base["Title"],
        fontSize=14,
        leading=18,
        spaceAfter=4,
        alignment=1,  # center
        fontName="Helvetica-Bold",
    )
    subtitle = ParagraphStyle(
        "AffSubtitle",
        parent=base["Normal"],
        fontSize=10,
        leading=13,
        spaceAfter=8,
        alignment=1,
        fontName="Helvetica-Oblique",
    )
    heading = ParagraphStyle(
        "AffHeading",
        parent=base["Normal"],
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body = ParagraphStyle(
        "AffBody",
        parent=base["Normal"],
        fontSize=11,
        leading=15,
        spaceAfter=5,
        leftIndent=14,
        fontName="Helvetica",
    )
    return title, subtitle, heading, body


def generate_pdf(ctx: AffidavitContext) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
    )

    title_style, subtitle_style, heading_style, body_style = _styles()
    story = []
    sections = build_sections(ctx)

    for i, section in enumerate(sections):
        if section["title"]:
            story.append(Spacer(1, 0.5 * cm))
            story.append(Paragraph(section["title"], title_style))
        if section.get("subtitle"):
            story.append(Paragraph(section["subtitle"], subtitle_style))
        story.append(Spacer(1, 0.3 * cm))

        for text in section["body"]:
            text = text.strip()
            if not text:
                story.append(Spacer(1, 0.3 * cm))
                continue
            is_heading = (
                text.isupper()
                or (text.startswith("PART ") and "—" in text)
                or text in ("DEPONENT", "WITNESS", "NOTARY / OATH COMMISSIONER")
            )
            style = heading_style if is_heading else body_style
            story.append(Paragraph(text, style))

        if section["page_break_after"] and i < len(sections) - 1:
            story.append(PageBreak())

    doc.build(story)
    buf.seek(0)
    return buf
