import httpx
import logging
import os
from datetime import datetime
import aiofiles
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# We are using a reliable, well-known service: 0x0.st
UPLOAD_URL = "https://0x0.st"

async def upload_text_as_file(content: str, desired_filename: str) -> str | None:
    """
    Takes a string content, uploads it as a .txt file, and returns a shareable download link.
    This serves as a fallback if PDF generation fails.
    """
    try:
        content_bytes = content.encode('utf-8')
        files = {'file': (desired_filename, content_bytes, 'text/plain')}
        
        async with httpx.AsyncClient() as client:
            logging.info(f"Uploading TXT to: {UPLOAD_URL}")
            response = await client.post(UPLOAD_URL, files=files, timeout=30.0)
            response.raise_for_status()
            download_link = response.text.strip()
            logging.info(f"TXT file uploaded successfully. Link: {download_link}")
            return download_link

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error during TXT file upload: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred in text file handler: {e}", exc_info=True)
        return None

async def generate_and_upload_pdf(cv_data: dict, desired_filename: str) -> str | None:
    """
    Generates a professional PDF from CV data, uploads it, and returns a download link.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_pdf_filename = f"temp_{timestamp}_{desired_filename}"

    try:
        # 1. Generate the PDF document
        doc = SimpleDocTemplate(temp_pdf_filename)
        styles = getSampleStyleSheet()
        story = []

        # CV Content
        name = cv_data.get('full_name', 'N/A').upper()
        email = cv_data.get('email', 'N/A')
        phone = cv_data.get('phone', 'N/A')
        links = cv_data.get('links', 'N/A')
        
        story.append(Paragraph(name, styles['h1']))
        story.append(Paragraph(f"{email} | {phone} | {links}", styles['Normal']))
        story.append(Spacer(1, 0.25*inch))

        story.append(Paragraph("Professional Summary", styles['h2']))
        story.append(Paragraph(cv_data.get('summary', 'N/A'), styles['BodyText']))
        story.append(Spacer(1, 0.25*inch))

        story.append(Paragraph("Work Experience", styles['h2']))
        story.append(Paragraph(cv_data.get('experience', 'N/A'), styles['BodyText']))
        story.append(Spacer(1, 0.25*inch))

        story.append(Paragraph("Education", styles['h2']))
        story.append(Paragraph(cv_data.get('education', 'N/A'), styles['BodyText']))
        story.append(Spacer(1, 0.25*inch))
        
        story.append(Paragraph("Skills", styles['h2']))
        story.append(Paragraph(cv_data.get('skills', 'N/A'), styles['BodyText']))
        story.append(Spacer(1, 0.25*inch))

        doc.build(story)
        logging.info(f"Successfully created temporary PDF file: {temp_pdf_filename}")

        # 2. Upload the generated PDF
        async with httpx.AsyncClient() as client:
            async with aiofiles.open(temp_pdf_filename, "rb") as f:
                content_bytes = await f.read()
                files = {'file': (desired_filename, content_bytes, 'application/pdf')}
                
                logging.info(f"Uploading PDF to: {UPLOAD_URL}")
                response = await client.post(UPLOAD_URL, files=files, timeout=30.0)
                response.raise_for_status()
                
                download_link = response.text.strip()
                logging.info(f"PDF uploaded successfully. Link: {download_link}")
                return download_link

    except Exception as e:
        logging.error(f"An unexpected error occurred in PDF handler: {e}", exc_info=True)
        return None
    finally:
        # 3. Clean up the temporary PDF file
        if os.path.exists(temp_pdf_filename):
            os.remove(temp_pdf_filename)
            logging.info(f"Successfully cleaned up temporary PDF file: {temp_pdf_filename}")

