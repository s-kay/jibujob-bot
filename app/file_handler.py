import httpx
import logging
import os
from datetime import datetime
import aiofiles
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import re

# We are switching to a more reliable, well-known service: file.io
UPLOAD_URL = "https://www.file.io"

def sanitize_text(text: str) -> str:
    """Removes unsupported characters for reportlab PDF generation."""
    # reportlab's default fonts have limited support for special characters.
    # This regex removes most common emojis and other symbols that might cause errors.
    return re.sub(r'[^\x00-\x7F]+', '', text)

async def generate_and_upload_pdf(cv_data: dict, desired_filename: str) -> str | None:
    """Generates a professional PDF from CV data and uploads it."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"temp_cv_{timestamp}.pdf"
    
    try:
        doc = SimpleDocTemplate(temp_filename, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        
        # Custom styles for better formatting
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='SectionHeader', parent=styles['h2'], spaceBefore=12, spaceAfter=6))
        
        story = []

        # CV Content
        if cv_data.get('full_name'):
            story.append(Paragraph(sanitize_text(cv_data.get('full_name', '').upper()), styles['h1']))
        
        contact_info = f"{cv_data.get('email', '')} | {cv_data.get('phone', '')} | {cv_data.get('links', '')}"
        story.append(Paragraph(sanitize_text(contact_info), styles['Center']))
        story.append(Spacer(1, 0.25*inch))
        
        sections = {
            "summary": "PROFESSIONAL SUMMARY", "experience": "WORK EXPERIENCE",
            "education": "EDUCATION", "certifications": "CERTIFICATIONS",
            "projects": "PROJECTS", "skills": "SKILLS", "referees": "REFEREES"
        }
        
        for section_key, section_title in sections.items():
            if cv_data.get(section_key):
                story.append(Paragraph(section_title, styles['SectionHeader']))
                content = sanitize_text(cv_data.get(section_key, ''))
                # Handle simple bullet points for PDF formatting
                content_paragraphs = content.split('\n')
                for para in content_paragraphs:
                    if para.strip().startswith(('-', '•')):
                        story.append(Paragraph(para.strip(), styles['BodyText'], bulletText='•'))
                    else:
                        story.append(Paragraph(para, styles['BodyText']))
                story.append(Spacer(1, 0.1*inch))

        doc.build(story)
        logging.info(f"Successfully created temporary PDF: {temp_filename}")
        
        return await upload_file(temp_filename, desired_filename)

    except Exception as e:
        logging.error(f"An error occurred during PDF generation: {e}", exc_info=True)
        return None
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

async def generate_and_upload_letter_pdf(letter_content: str, desired_filename: str) -> str | None:
    """Generates a PDF from cover letter text and uploads it."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"temp_letter_{timestamp}.pdf"

    try:
        doc = SimpleDocTemplate(temp_filename, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = []
        
        sanitized_content = sanitize_text(letter_content)
        paragraphs = sanitized_content.split('\n')
        for para_text in paragraphs:
            if para_text.strip():
                story.append(Paragraph(para_text, styles['BodyText']))
                story.append(Spacer(1, 12)) # 12 points of space after each paragraph

        doc.build(story)
        logging.info(f"Successfully created temporary letter PDF: {temp_filename}")

        return await upload_file(temp_filename, desired_filename)
        
    except Exception as e:
        logging.error(f"An error occurred during Letter PDF generation: {e}", exc_info=True)
        return None
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

async def upload_file(local_filepath: str, desired_filename: str) -> str | None:
    """Helper function to upload a file and return the link."""
    try:
        async with httpx.AsyncClient() as client:
            async with aiofiles.open(local_filepath, "rb") as f:
                content_bytes = await f.read()
                files = {'file': (desired_filename, content_bytes, 'application/pdf')}
                
                logging.info(f"Uploading {desired_filename} to: {UPLOAD_URL}")
                response = await client.post(UPLOAD_URL, files=files, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                download_link = result.get("link")
                if not download_link:
                    raise ValueError("Upload service did not return a link.")
                
                logging.info(f"File uploaded successfully. Link: {download_link}")
                return download_link
    except Exception as e:
        logging.error(f"An unexpected error occurred during file upload: {e}", exc_info=True)
        return None

