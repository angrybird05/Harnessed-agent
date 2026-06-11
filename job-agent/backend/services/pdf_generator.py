from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os


def generate_resume_pdf(
    resume_data: dict, user_profile: dict, output_path: str
) -> str:
    """Generate an ATS-friendly resume PDF using ReportLab.

    Sections in order: Name + contact, Summary, Skills, Experience,
    Projects, Education, Certifications.
    ATS-friendly: no tables, no columns, no images, no headers/footers.
    Font: Helvetica. Name 20pt bold. Section headers 11pt bold. Body 9pt.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "NameStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    contact_style = ParagraphStyle(
        "ContactStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        spaceAfter=6,
        spaceBefore=12,
        alignment=TA_LEFT,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        spaceAfter=4,
        alignment=TA_LEFT,
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        spaceAfter=2,
        leftIndent=20,
        alignment=TA_LEFT,
    )

    elements = []

    # --- Name + Contact ---
    full_name = user_profile.get("full_name", "")
    if full_name:
        elements.append(Paragraph(full_name, name_style))

    contact_parts = []
    email = user_profile.get("email", "")
    if email:
        contact_parts.append(email)
    phone = user_profile.get("phone", "")
    if phone:
        contact_parts.append(phone)
    linkedin = user_profile.get("linkedin_url", "")
    if linkedin:
        contact_parts.append(linkedin)
    github = user_profile.get("github_url", "")
    if github:
        contact_parts.append(github)
    portfolio = user_profile.get("portfolio_url", "")
    if portfolio:
        contact_parts.append(portfolio)

    if contact_parts:
        elements.append(Paragraph(" | ".join(contact_parts), contact_style))

    elements.append(Spacer(1, 8))

    # --- Summary ---
    summary = resume_data.get("summary", "")
    if summary:
        elements.append(Paragraph("SUMMARY", section_header_style))
        elements.append(Paragraph(summary, body_style))

    # --- Skills ---
    skills = resume_data.get("skills_ordered", [])
    if skills:
        elements.append(Paragraph("SKILLS", section_header_style))
        elements.append(Paragraph(", ".join(skills), body_style))

    # --- Experience ---
    experience = resume_data.get("experience", [])
    if experience:
        elements.append(Paragraph("EXPERIENCE", section_header_style))
        for exp in experience:
            title = exp.get("title", "")
            company = exp.get("company", "")
            dates = exp.get("dates", "")
            header_text = f"<b>{title}</b>"
            if company:
                header_text += f" — {company}"
            if dates:
                header_text += f" ({dates})"
            elements.append(Paragraph(header_text, body_style))

            bullets = exp.get("bullets", [])
            for bullet in bullets:
                elements.append(Paragraph(f"• {bullet}", bullet_style))

    # --- Projects ---
    projects = resume_data.get("projects", [])
    if projects:
        elements.append(Paragraph("PROJECTS", section_header_style))
        for proj in projects:
            name = proj.get("name", "")
            desc = proj.get("description", "")
            tech = proj.get("tech", [])
            header_text = f"<b>{name}</b>"
            if tech:
                header_text += f" — {', '.join(tech)}"
            elements.append(Paragraph(header_text, body_style))
            if desc:
                elements.append(Paragraph(desc, bullet_style))

    # --- Education ---
    education = resume_data.get("education", [])
    if education:
        elements.append(Paragraph("EDUCATION", section_header_style))
        for edu in education:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            year = edu.get("year", "")
            edu_text = f"<b>{degree}</b>"
            if institution:
                edu_text += f" — {institution}"
            if year:
                edu_text += f" ({year})"
            elements.append(Paragraph(edu_text, body_style))

    # --- Certifications ---
    certifications = resume_data.get("certifications", [])
    if certifications:
        elements.append(Paragraph("CERTIFICATIONS", section_header_style))
        for cert in certifications:
            elements.append(Paragraph(f"• {cert}", bullet_style))

    doc.build(elements)
    return output_path
