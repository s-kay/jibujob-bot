import httpx
import logging
import os
from datetime import datetime

# We'll use transfer.sh, a simple and free service for temporary file sharing.
UPLOAD_URL = "https://transfer.sh/"

async def upload_text_as_file(content: str, desired_filename: str) -> str | None:
    """
    Takes a string content, saves it to a temporary file, uploads it,
    and returns a shareable download link.

    Args:
        content: The string content to be put in the file (e.g., the formatted CV).
        desired_filename: The name the downloaded file should have (e.g., "KaziLeo_CV.txt").

    Returns:
        A public download link as a string, or None if the upload fails.
    """
    # Create a unique temporary filename to avoid conflicts on the server
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"temp_{timestamp}.txt"
    
    try:
        # 1. Create the temporary file on the server
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Successfully created temporary file: {temp_filename}")

        # 2. Upload the file to the hosting service
        async with httpx.AsyncClient() as client:
            with open(temp_filename, "rb") as f:
                # The service uses the URL path as the desired filename
                url = f"{UPLOAD_URL}{desired_filename}"
                logging.info(f"Uploading to: {url}")
                
                response = await client.put(url, content=f)
                
                response.raise_for_status()  # This will raise an error for 4xx or 5xx status codes
                
                # The response body is the download link
                download_link = response.text.strip()
                logging.info(f"File uploaded successfully. Link: {download_link}")
                return download_link

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error during file upload: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred in file handler: {e}", exc_info=True)
        return None
    finally:
        # 3. Clean up and delete the temporary file from our server
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logging.info(f"Successfully cleaned up temporary file: {temp_filename}")
