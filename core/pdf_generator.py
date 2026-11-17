import os
import re
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "saved_resumes")

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-_\. ]', '_', name)

def generate_resume_pdf(tailored_data: Dict[str, Any], filename_prefix: str = "curriculo") -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clean_company = sanitize_filename(tailored_data.get("job_company", "Geral")).replace(" ", "_")
    clean_title = sanitize_filename(tailored_data.get("job_title", "Dev")).replace(" ", "_")
    
    pdf_filename = f"Curriculo_Davi_Marcal_{clean_company}_{clean_title}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=22,
        bottomMargin=22
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#0F172A")    # Slate 900
    ACCENT = colors.HexColor("#1D4ED8")     # Blue 700
    TEXT_DARK = colors.HexColor("#334155")  # Slate 700
    MUTED = colors.HexColor("#64748B")      # Slate 500
    LINE_COLOR = colors.HexColor("#CBD5E1") # Slate 300

    # Custom typography styles
    name_style = ParagraphStyle(
        'DocName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=21,
        textColor=PRIMARY,
        alignment=0
    )

    headline_style = ParagraphStyle(
        'DocHeadline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=ACCENT,
        alignment=0
    )

    contact_style = ParagraphStyle(
        'DocContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=MUTED,
        alignment=0
    )

    section_heading = ParagraphStyle(
        'DocSection',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=PRIMARY,
        spaceBefore=5,
        spaceAfter=1
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=TEXT_DARK
    )

    bold_body_style = ParagraphStyle(
        'DocBoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=PRIMARY
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=TEXT_DARK,
        leftIndent=10,
        firstLineIndent=-6
    )

    story = []

    # --- 1. CABEÇALHO ---
    p = tailored_data["personal"]
    story.append(Paragraph(p["name"].upper(), name_style))
    story.append(Spacer(1, 1))
    story.append(Paragraph(tailored_data["tailored_headline"], headline_style))
    story.append(Spacer(1, 2))
    
    contact_line = f"{p['location']}  •  {p['phone']}  •  {p['email']}  •  GitHub: {p['github']}  •  18 anos"
    story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.8, color=LINE_COLOR, spaceBefore=0, spaceAfter=4))

    # --- 2. RESUMO PROFISSIONAL ---
    story.append(Paragraph("RESUMO PROFISSIONAL", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.4, color=LINE_COLOR, spaceBefore=1, spaceAfter=2))
    story.append(Paragraph(tailored_data["tailored_summary"], body_style))
    story.append(Spacer(1, 4))

    # --- 3. COMPETÊNCIAS TÉCNICAS (ORGANIZADAS) ---
    story.append(Paragraph("HABILIDADES E COMPETÊNCIAS TÉCNICAS", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.4, color=LINE_COLOR, spaceBefore=1, spaceAfter=2))
    
    skills_dict = tailored_data["tailored_skills"]
    fe = ", ".join(skills_dict.get("frontend", [])[:9])
    be = ", ".join(skills_dict.get("backend_and_apis", [])[:8])
    mob = ", ".join(skills_dict.get("mobile", [])[:4])
    ai_data = ", ".join(skills_dict.get("ai_and_data", [])[:5])
    tools = ", ".join(skills_dict.get("devops_and_tools", [])[:7])

    skills_text = (
        f"<b>• Frontend & Web:</b> {fe}<br/>"
        f"<b>• Backend, APIs & Integrações:</b> {be}<br/>"
        f"<b>• Mobile:</b> {mob}  |  <b>IA Generativa & Dados:</b> {ai_data}<br/>"
        f"<b>• Ferramentas & Metodologias:</b> {tools}"
    )
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 4))

    # --- 4. PROJETOS PRÁTICOS E SISTEMAS DESENVOLVIDOS (ENXUTOS) ---
    story.append(Paragraph("PROJETOS DE DESENVOLVIMENTO", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.4, color=LINE_COLOR, spaceBefore=1, spaceAfter=2))

    for proj in tailored_data["ranked_projects"][:3]:
        stack_str = ", ".join(proj["stack"][:4])
        hl_text = proj["highlights"][0] if proj.get("highlights") else ""
        proj_line = f"<b>{proj['name']}</b> ({stack_str}) — {hl_text} <font color='#1D4ED8'>[{proj.get('url', '')}]</font>"
        story.append(Paragraph(proj_line, body_style))
        story.append(Spacer(1, 2))

    # --- 5. EXPERIÊNCIA PROFISSIONAL ---
    if tailored_data.get("experience"):
        story.append(Paragraph("EXPERIÊNCIA PROFISSIONAL", section_heading))
        story.append(HRFlowable(width="100%", thickness=0.4, color=LINE_COLOR, spaceBefore=1, spaceAfter=2))
        for exp in tailored_data["experience"][:4]:
            exp_header = f"<b>{exp['role']}</b> — {exp['company']} <font color='#64748B'>({exp['period']} | {exp['location']})</font>"
            story.append(Paragraph(exp_header, bold_body_style))
            story.append(Paragraph(exp['description'], body_style))
            story.append(Spacer(1, 2))

    # --- 6. FORMAÇÃO ACADÊMICA, CERTIFICAÇÕES & IDIOMAS ---
    story.append(Paragraph("FORMAÇÃO ACADÊMICA, CERTIFICAÇÕES & IDIOMAS", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.4, color=LINE_COLOR, spaceBefore=1, spaceAfter=2))

    edu_items = []
    for edu in tailored_data.get("education", [])[:1]:
        edu_items.append(f"<b>{edu['degree']}</b> – {edu['institution']} ({edu['period']})")
    
    lang_items = []
    for lang in tailored_data.get("languages", []):
        lang_items.append(f"<b>{lang['name']}:</b> {lang['level']}")

    certs = tailored_data.get("certifications", [])
    cert_line = f"<br/><b>Certificações:</b> {' | '.join(certs)}" if certs else ""

    edu_and_lang = "<br/>".join(edu_items) + cert_line + "<br/>" + "  •  ".join(lang_items)
    story.append(Paragraph(edu_and_lang, body_style))
    story.append(Spacer(1, 3))

    doc.build(story)
    return pdf_path

def generate_resume_markdown(tailored_data: Dict[str, Any]) -> str:
    p = tailored_data["personal"]
    lines = []
    lines.append(f"# {p['name'].upper()}")
    lines.append(f"**{tailored_data['tailored_headline']}**")
    lines.append(f"{p['location']} | {p['phone']} | {p['email']} | [GitHub]({p['github']})")
    lines.append("\n---\n")
    
    lines.append("## Resumo Profissional")
    lines.append(tailored_data["tailored_summary"])
    lines.append("\n---\n")

    lines.append("## Competências Técnicas")
    for cat, sks in tailored_data["tailored_skills"].items():
        lines.append(f"- **{cat.replace('_', ' ').title()}:** {', '.join(sks)}")
    lines.append("\n---\n")

    lines.append("## Projetos em Destaque")
    for proj in tailored_data["ranked_projects"][:4]:
        lines.append(f"### {proj['name']} ({proj['role']})")
        lines.append(f"- **Stack:** {', '.join(proj['stack'])}")
        lines.append(f"- **Repositório:** {proj.get('url', '')}")
        for hl in proj["highlights"]:
            lines.append(f"  * {hl}")
        lines.append("")
    lines.append("---\n")

    lines.append("## Formação Acadêmica")
    for edu in tailored_data.get("education", []):
        lines.append(f"- **{edu['degree']}** – {edu['institution']} ({edu['period']})")
    
    lines.append("\n## Idiomas")
    for lang in tailored_data.get("languages", []):
        lines.append(f"- **{lang['name']}:** {lang['level']}")

    return "\n".join(lines)
