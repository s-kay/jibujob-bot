import httpx
import logging
import os
from datetime import datetime
import aiofiles

# We are using a reliable, well-known service: 0x0.st
UPLOAD_URL = "https://0x0.st"

async def upload_text_as_file(content: str, desired_filename: str) -> str | None:
    """
    Takes a string content, saves it to a temporary file, uploads it to a hosting service,
    and returns a shareable download link.

    Args:
        content: The string content to be put in the file (e.g., the formatted CV).
        desired_filename: The name the downloaded file should have (e.g., "KaziLeo_CV.txt").

    Returns:
        A public download link as a string, or None if the upload fails.
    """
    # Create a unique temporary filename to avoid conflicts on the server
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"temp_{timestamp}_{desired_filename}"
    
    try:
        # 1. Asynchronously create the temporary file on the server
        async with aiofiles.open(temp_filename, "w", encoding="utf-8") as f:
            await f.write(content)
        logging.info(f"Successfully created temporary file: {temp_filename}")

        # 2. Asynchronously upload the file to the new hosting service
        async with httpx.AsyncClient() as client:
            async with aiofiles.open(temp_filename, "rb") as f:
                # THE FIX IS HERE: We read the content into a bytes object first.
                # This resolves the type mismatch between aiofiles and httpx.
                content_bytes = await f.read()
                files = {'file': (desired_filename, content_bytes, 'text/plain')}
                
                logging.info(f"Uploading to: {UPLOAD_URL}")
                response = await client.post(UPLOAD_URL, files=files, timeout=30.0)
                
                response.raise_for_status()
                
                download_link = response.text.strip()
                logging.info(f"File uploaded successfully. Link: {download_link}")
                return download_link

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error during file upload to {UPLOAD_URL}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred in file handler: {e}", exc_info=True)
        return None
    finally:
        # 3. Clean up and delete the temporary file from our server
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logging.info(f"Successfully cleaned up temporary file: {temp_filename}")

